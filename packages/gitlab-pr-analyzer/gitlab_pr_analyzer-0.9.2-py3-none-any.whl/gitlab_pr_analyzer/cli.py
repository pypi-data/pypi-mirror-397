#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""command-line interface for GitLab analyzer.

goal: keep user experience consistent with github_pr_analyzer
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .ai_analyzer import AIAnalyzer
from .commit_collector import CommitCollector, CommitSummary
from .config import config
from .diff_provider import DiffProvider
from .matcher import Matcher, MatchResult
from .mr_collector import MergeRequestCollector, MergeRequestSummary
from .mr_exporter import MRJSONExporter
from .smart_search_analyzer import SmartSearchAnalyzer
from .gitlab_client import GitLabClient
from .utils import check_git, check_glab, detect_gitlab_project, format_datetime

console = Console()


ASCII_LOGO = r"""
██████╗ ██╗████████╗██╗      █████╗ ██████╗         ██████╗ ██████╗          █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗ 
██╔════╝ ██║╚══██╔══╝██║     ██╔══██╗██╔══██╗        ██╔══██╗██╔══██╗        ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
██║  ███╗██║   ██║   ██║     ███████║██████╔╝        ██████╔╝██████╔╝        ███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
██║   ██║██║   ██║   ██║     ██╔══██║██╔══██╗        ██╔═══╝ ██╔══██╗        ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
╚██████╔╝██║   ██║   ███████╗██║  ██║██████╔╝███████╗██║     ██║  ██║███████╗██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
 ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝
"""


def print_banner() -> None:
    """print application banner."""
    console.print(ASCII_LOGO, style="bold magenta")
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        GitLab MR & Commit Analyzer                    ║
    ║                                                       ║
    ║     Intelligent MR and Commit Analysis Tool           ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold magenta")


def check_prerequisites() -> bool:
    """check if all prerequisites are met."""
    console.print("\n[cyan]Checking prerequisites...[/cyan]")

    errors: List[str] = []

    if not check_git():
        errors.append("git is not installed or not in PATH")
    else:
        console.print("[green]✓ git found[/green]")

    if not config.gitlab_host:
        errors.append("GITLAB_HOST is missing")

    if not config.gitlab_token:
        errors.append("GITLAB_TOKEN is missing")

    glab_ok = check_glab()
    if glab_ok:
        console.print("[green]✓ glab found[/green]")
    else:
        console.print("[yellow]⚠ glab not found, diff may use slower fallbacks[/yellow]")

    if errors:
        console.print("\n[red]Prerequisites not met:[/red]")
        for error in errors:
            console.print("  [red]✗ {0}[/red]".format(error))
        return False

    console.print("[green]✓ All prerequisites met[/green]\n")
    return True


def resolve_repo_identifier(repo: Optional[str]) -> str:
    """resolve GitLab project path using option or git remote."""
    if repo:
        cleaned = str(repo or "").strip()
        if not cleaned:
            raise click.UsageError(
                "repo is empty; provide group/subgroup/project or a local repo directory"
            )

        if cleaned.startswith("./") and len(cleaned) > 2:
            cleaned = cleaned[2:]

        # allow passing local repo directory, e.g. '.', './TensorRT', 'TensorRT/'
        while cleaned.endswith("/") and len(cleaned) > 1:
            cleaned = cleaned[:-1]

        candidate_dir = Path(cleaned)
        if candidate_dir.exists() and candidate_dir.is_dir():
            if not config.gitlab_host:
                raise click.UsageError(
                    "GITLAB_HOST must be set to detect project path from a local repo directory"
                )
            detected = detect_gitlab_project(config.gitlab_host, repo_dir=str(candidate_dir))
            if detected:
                console.print("[cyan]detected project: {0}[/cyan]".format(detected))
                return detected
            raise click.UsageError(
                "unable to detect project from local repo directory '{0}'. "
                "ensure it has a GitLab origin remote, or provide --repo as group/subgroup/project.".format(
                    cleaned
                )
            )

        if cleaned in {".", "./"}:
            raise click.UsageError(
                "invalid repo identifier '.'; provide group/subgroup/project or run inside a git repo"
            )

        return cleaned

    if not config.gitlab_host:
        raise click.UsageError("GITLAB_HOST must be set to auto-detect project path")

    detected = detect_gitlab_project(config.gitlab_host)
    if detected:
        console.print("[cyan]detected project: {0}[/cyan]".format(detected))
        return detected

    raise click.UsageError(
        "unable to detect project from git remote. please provide --repo explicitly."
    )


def resolve_json_export_flag(
    enable_flag: bool, disable_flag: bool, default: bool, command_name: str
) -> bool:
    """resolve mutually exclusive json export flags."""
    if enable_flag and disable_flag:
        raise click.BadParameter(
            "--save-json and --no-save-json cannot be combined in {0}".format(
                command_name
            ),
            param_hint="--save-json/--no-save-json",
        )
    if enable_flag:
        return True
    if disable_flag:
        return False
    return default


def display_results_table(results: List[MatchResult]) -> None:
    """display search results in a table."""
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(
        title="Search Results ({0} matches)".format(len(results)),
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Type", width=8)
    table.add_column("ID", width=12)
    table.add_column("Date/Time", width=16)
    table.add_column("Title/Message", style="green", no_wrap=False)
    table.add_column("Author", width=18)
    table.add_column("Score", justify="right", width=8)

    for idx, result in enumerate(results, 1):
        item_id = "-"
        title = "-"
        author = "-"
        date_time = "unknown"

        if result.item_type == "MR":
            mr = result.item
            if isinstance(mr, MergeRequestSummary):
                item_id = "!{0}".format(mr.iid)
                title = mr.title[:80]
                author = mr.author
                date_time = format_datetime(mr.updated_at)
        else:
            commit = result.item
            if isinstance(commit, CommitSummary):
                item_id = commit.short_sha
                title = commit.message.split("\n")[0][:80]
                author = commit.author
                date_time = format_datetime(commit.committed_date)

        table.add_row(
            str(idx),
            result.item_type,
            item_id,
            date_time,
            title,
            author,
            str(result.score),
        )

    console.print(table)


def render_merge_request_panel(mr: MergeRequestSummary) -> None:
    """display merge request details."""
    merged_line = ""
    if mr.merged_at:
        merged_line = "[bold]Merged:[/bold] {0}\n".format(
            format_datetime(mr.merged_at, "full")
        )

    labels_text = "None"
    if mr.labels:
        labels_text = ", ".join(mr.labels)

    source_branch = "-"
    if mr.source_branch:
        source_branch = mr.source_branch

    target_branch = "-"
    if mr.target_branch:
        target_branch = mr.target_branch

    changes_count = "Unknown"
    if mr.changes_count:
        changes_count = str(mr.changes_count)

    description = "No description provided."
    if mr.description:
        description = mr.description

    info_text = """
[bold cyan]MR !{iid}[/bold cyan]: {title}

[bold]Author:[/bold] {author}
[bold]State:[/bold] {state}
[bold]Created:[/bold] {created}
[bold]Updated:[/bold] {updated}
{merged}[bold]URL:[/bold] {url}

[bold]Statistics:[/bold]
  • Labels: {labels}
  • Changes Count: {changes}
  • Source → Target: {src} → {dst}

[bold]Description:[/bold]
{desc}
    """.format(
        iid=mr.iid,
        title=mr.title,
        author=mr.author,
        state=mr.state,
        created=format_datetime(mr.created_at, "full"),
        updated=format_datetime(mr.updated_at, "full"),
        merged=merged_line,
        url=mr.web_url,
        labels=labels_text,
        changes=changes_count,
        src=source_branch,
        dst=target_branch,
        desc=description,
    )

    console.print(Panel(info_text, border_style="magenta"))


def render_commit_panel(commit: CommitSummary) -> None:
    """display commit details."""
    parents_text = "None"
    if commit.parents:
        parents_text = ", ".join(commit.parents)

    info_text = """
[bold cyan]Commit {short_sha}[/bold cyan]

[bold]Author:[/bold] {author} <{email}>
[bold]Authored:[/bold] {authored}
[bold]Committed:[/bold] {committed}
[bold]Is Merge:[/bold] {is_merge}
[bold]Parents:[/bold] {parents}

[bold]Statistics:[/bold]
  • Files Changed: {files}
  • Insertions: {ins}
  • Deletions: {dels}

[bold]Message:[/bold]
{message}
    """.format(
        short_sha=commit.short_sha,
        author=commit.author,
        email=commit.author_email,
        authored=format_datetime(commit.authored_date, "full"),
        committed=format_datetime(commit.committed_date, "full"),
        is_merge=commit.is_merge,
        parents=parents_text,
        files=commit.files_changed,
        ins=commit.insertions,
        dels=commit.deletions,
        message=commit.message,
    )

    console.print(Panel(info_text, border_style="magenta"))


def display_diff_text(diff_text: Optional[str], max_lines: int = 100) -> None:
    """display diff text with a line cap."""
    if not diff_text:
        console.print("[yellow]diff is not available[/yellow]")
        return

    lines = diff_text.splitlines()
    capped = lines[:max_lines]
    if len(lines) > max_lines:
        capped.append("... diff truncated ...")

    console.print("\n".join(capped))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    """GitLab MR and Commit Analyzer - Find and analyze relevant changes."""
    pass


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo",
    "-r",
    help="Repository in format group/subgroup/project or local repo directory (optional; used to verify project access)",
)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON for automation")
def check(repo: Optional[str], as_json: bool) -> None:
    """Check environment configuration and GitLab API connectivity."""
    print_banner()

    ok = True
    details: dict = {"ok": False, "checks": [], "repo": repo}

    git_ok = check_git()
    details["checks"].append({"name": "git", "ok": git_ok})
    if git_ok:
        console.print("[green]✓ git found[/green]")
    else:
        console.print("[red]✗ git not found[/red]")
        ok = False

    host_ok = bool(config.gitlab_host)
    token_ok = bool(config.gitlab_token)
    details["checks"].append({"name": "GITLAB_HOST", "ok": host_ok})
    details["checks"].append({"name": "GITLAB_TOKEN", "ok": token_ok})
    if not host_ok:
        console.print("[red]✗ GITLAB_HOST missing[/red]")
        ok = False
    if not token_ok:
        console.print("[red]✗ GITLAB_TOKEN missing[/red]")
        ok = False

    glab_ok = check_glab()
    details["checks"].append({"name": "glab", "ok": glab_ok})
    if glab_ok:
        console.print("[green]✓ glab found[/green]")
    else:
        console.print("[yellow]⚠ glab not found (optional)[/yellow]")

    api_result = None
    try:
        client = GitLabClient()
        api_result = client.check_connection()
    except Exception as exc:
        api_result = {"ok": False, "error": str(exc)}

    details["checks"].append({"name": "gitlab_api", "result": api_result})
    if api_result and api_result.get("ok"):
        console.print("[green]✓ gitlab api ok[/green]")
        user = api_result.get("user")
        if isinstance(user, dict):
            display = user.get("username")
            if not display:
                display = user.get("name")
            if display:
                console.print("[green]✓ user: {0}[/green]".format(display))
    else:
        ok = False
        console.print("[red]✗ gitlab api failed[/red]")
        if api_result and api_result.get("error"):
            console.print("[red]{0}[/red]".format(api_result.get("error")))

    if repo:
        project_ok = False
        project_error = None
        try:
            client = GitLabClient()
            project = client.get_project(repo)
            project_ok = True
            web_url = getattr(project, "web_url", None)
            if web_url:
                console.print("[green]✓ project access ok: {0}[/green]".format(repo))
                console.print("[green]✓ url: {0}[/green]".format(web_url))
            else:
                console.print("[green]✓ project access ok: {0}[/green]".format(repo))
        except Exception as exc:
            project_ok = False
            project_error = str(exc)
            console.print("[red]✗ project access failed: {0}[/red]".format(repo))
            console.print("[red]{0}[/red]".format(project_error))
            ok = False

        details["checks"].append(
            {"name": "project_access", "ok": project_ok, "repo": repo, "error": project_error}
        )

    details["ok"] = ok

    if as_json:
        import json as _json

        console.print(_json.dumps(details, ensure_ascii=False, indent=2))

    if not ok:
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo",
    "-r",
    help="Repository in format group/subgroup/project or local repo directory (auto-detect if not specified)",
)
@click.option(
    "--months",
    "-m",
    type=int,
    default=3,
    show_default=True,
    help="Number of months to look back for merged items",
)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export collected MRs into JSON files",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Disable MR JSON export",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gl_pr_exports"),
    show_default=True,
    help="Directory for exported MR JSON files",
)
def collect(
    repo: Optional[str],
    months: int,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
) -> None:
    """Collect all MRs and commits from the repository."""
    print_banner()

    if months <= 0:
        console.print("[red]months must be a positive integer[/red]")
        sys.exit(1)

    if not check_prerequisites():
        sys.exit(1)

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=False, command_name="collect"
    )

    project_path = resolve_repo_identifier(repo)
    try:
        mr_collector = MergeRequestCollector(project_path)
        console.print("\n[bold]Repository:[/bold] {0}\n".format(project_path))

        data = mr_collector.collect_by_months(months=months)
        open_mrs = data.get("open", [])
        merged_mrs = data.get("merged", [])

        console.print("[bold magenta]Summary:[/bold magenta]")
        console.print("  • Open MRs: {0}".format(len(open_mrs)))
        console.print(
            "  • Merged MRs (last {0} months): {1}".format(months, len(merged_mrs))
        )

        commit_collector = CommitCollector()
        commits = commit_collector.collect_commits(days=months * 30)
        console.print("  • Commits (last {0} months): {1}".format(months, len(commits)))
        console.print()

        if save_json:
            exporter = MRJSONExporter(project_path=project_path, output_dir=output_dir)
            pairs: List[Tuple[int, Optional[str]]] = []
            for mr in open_mrs:
                pairs.append((mr.iid, mr.title))
            for mr in merged_mrs:
                pairs.append((mr.iid, mr.title))
            saved = 0
            for iid, title in pairs:
                try:
                    exporter.export_mr(iid, title_hint=title)
                    saved += 1
                except Exception as exc:
                    console.print(
                        "[red]Failed to export MR !{0}: {1}[/red]".format(iid, exc)
                    )
            if saved == 0:
                console.print("[yellow]No MR JSON files were created[/yellow]")
            else:
                console.print(
                    "[green]✓ Exported {0} MR file(s) to {1}[/green]".format(
                        saved, str(output_dir)
                    )
                )

    except Exception as exc:
        console.print("[red]Error: {0}[/red]".format(exc))
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query")
@click.option(
    "--repo",
    "-r",
    help="Repository in format group/subgroup/project or local repo directory (auto-detect if not specified)",
)
@click.option("--months", "-m", type=int, default=3, show_default=True)
@click.option("--min-score", type=int, default=30, show_default=True)
@click.option("--max-results", type=int, default=20, show_default=True)
@click.option(
    "--ai",
    "use_ai",
    is_flag=True,
    default=False,
    help="Enable AI analysis (requires CURSOR_AGENT_PATH)",
)
@click.option(
    "--analyze",
    "-a",
    "use_ai_legacy",
    is_flag=True,
    default=False,
    hidden=True,
    help="alias of --ai",
)
@click.option("--show-diff", "-d", is_flag=True, help="Show diff for each result")
@click.option(
    "--smart-search/--no-smart-search",
    default=False,
    show_default=True,
    help="Use AI-powered smart search (requires --ai)",
)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export matched MRs into JSON files",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Disable MR JSON export",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gl_pr_exports"),
    show_default=True,
    help="Directory for exported MR JSON files",
)
@click.option(
    "-cn",
    "--chinese",
    "use_chinese",
    is_flag=True,
    default=False,
    help="Output AI analysis in Chinese (requires --ai)",
)
def search(
    query: str,
    repo: Optional[str],
    months: int,
    min_score: int,
    max_results: int,
    use_ai: bool,
    use_ai_legacy: bool,
    show_diff: bool,
    smart_search: bool,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
    use_chinese: bool,
) -> None:
    """Search for MRs and commits matching a query."""
    print_banner()

    if months <= 0:
        console.print("[red]months must be a positive integer[/red]")
        sys.exit(1)

    if not check_prerequisites():
        sys.exit(1)

    if use_ai_legacy:
        use_ai = True

    if smart_search and (not use_ai):
        raise click.UsageError("--smart-search requires --ai")

    project_path = resolve_repo_identifier(repo)
    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=False, command_name="search"
    )

    try:
        mr_collector = MergeRequestCollector(project_path)
        console.print("\n[bold]Repository:[/bold] {0}\n".format(project_path))

        data = mr_collector.collect_by_months(months=months)
        merge_requests = data.get("open", []) + data.get("merged", [])

        commit_collector = CommitCollector()
        commits = commit_collector.collect_commits(days=months * 30)

        matcher = Matcher(minimum_score=min_score)
        keywords = query.split()
        if smart_search:
            analyzer = SmartSearchAnalyzer()
            keywords = analyzer.extract_search_keywords(query)
        results = matcher.search_with_keywords(
            merge_requests=merge_requests,
            commits=commits,
            keywords=keywords,
            max_results=max_results,
        )

        console.print()
        display_results_table(results)

        if not results:
            return

        diff_provider = DiffProvider(project_path)

        if show_diff:
            console.print("\n[bold cyan]Displaying diffs...[/bold cyan]\n")
            for result in results[:5]:
                diff_text = diff_provider.get_diff(result.item)
                display_diff_text(diff_text, max_lines=100)
                console.print()

        if use_ai:
            language = "en"
            if use_chinese:
                language = "cn"
            ai_analyzer = AIAnalyzer(language=language)
            if not ai_analyzer.is_available:
                console.print(
                    "\n[yellow]AI analysis not available. Please set CURSOR_AGENT_PATH environment variable[/yellow]"
                )
                return

            console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")

            def provide_diff(item) -> Optional[str]:
                return diff_provider.get_diff(item)

            items_to_analyze = [r.item for r in results[:5]]
            analyzed = []
            exporter = None
            if save_json:
                exporter = MRJSONExporter(project_path=project_path, output_dir=output_dir)

            for idx, item in enumerate(items_to_analyze, 1):
                console.print("[cyan]Analyzing {0}/{1}...[/cyan]".format(idx, len(items_to_analyze)))
                analysis = ai_analyzer.analyze(
                    item, include_diff=True, diff_provider=provide_diff
                )
                analyzed.append((item, analysis))
                if analysis:
                    ai_analyzer.display_analysis(item, analysis)

                if save_json and exporter and isinstance(item, MergeRequestSummary):
                    try:
                        path = exporter.export_mr(item.iid, title_hint=item.title)
                        console.print("[green]✓ JSON saved: {0}[/green]\n".format(path))
                    except Exception as exc:
                        console.print(
                            "[red]Failed to export MR !{0}: {1}[/red]\n".format(
                                item.iid, exc
                            )
                        )

            if save_json and analyzed:
                report = ai_analyzer.generate_summary_report(analyzed, query)
                report_file = "mr_analysis_report_{0}.md".format(
                    project_path.replace("/", "_")
                )
                Path(report_file).write_text(report, encoding="utf-8")
                console.print("[green]✓ Report saved to: {0}[/green]".format(report_file))

        if (not analyze) and save_json:
            exporter = MRJSONExporter(project_path=project_path, output_dir=output_dir)
            saved = 0
            for result in results:
                if isinstance(result.item, MergeRequestSummary):
                    try:
                        exporter.export_mr(result.item.iid, title_hint=result.item.title)
                        saved += 1
                    except Exception as exc:
                        console.print(
                            "[red]Failed to export MR !{0}: {1}[/red]".format(
                                result.item.iid, exc
                            )
                        )
            if saved == 0:
                console.print("[yellow]No MR JSON files were created[/yellow]")

    except Exception as exc:
        console.print("[red]Error: {0}[/red]".format(exc))
        sys.exit(1)


@cli.command("view-pr", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("pr_number", type=int)
@click.option(
    "--repo",
    "-r",
    help="Repository in format group/subgroup/project or local repo directory (auto-detect if not specified)",
)
@click.option(
    "--ai",
    "use_ai",
    is_flag=True,
    default=False,
    help="Enable AI analysis (requires CURSOR_AGENT_PATH)",
)
@click.option(
    "--analyze",
    "-a",
    "use_ai_legacy",
    is_flag=True,
    default=False,
    hidden=True,
    help="alias of --ai",
)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export this MR into a JSON file (default: enabled)",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Skip exporting this MR to JSON",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gl_pr_exports"),
    show_default=True,
    help="Directory for exported MR JSON files",
)
@click.option(
    "-cn",
    "--chinese",
    "use_chinese",
    is_flag=True,
    default=False,
    help="Output AI analysis in Chinese (requires --ai)",
)
def view_pr(
    pr_number: int,
    repo: Optional[str],
    use_ai: bool,
    use_ai_legacy: bool,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
    use_chinese: bool,
) -> None:
    """View details of a specific MR (iid)."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=True, command_name="view-pr"
    )

    project_path = resolve_repo_identifier(repo)

    if use_ai_legacy:
        use_ai = True

    try:
        collector = MergeRequestCollector(project_path)
        data = collector.collect(days=365)
        items = data.get("open", []) + data.get("merged", [])
        target = None
        for mr in items:
            if mr.iid == pr_number:
                target = mr
                break

        if not target:
            console.print("[red]MR !{0} not found[/red]".format(pr_number))
            return

        render_merge_request_panel(target)

        diff_provider = DiffProvider(project_path)
        if Confirm.ask("\nShow diff?", default=True):
            diff_text = diff_provider.get_merge_request_diff(target)
            display_diff_text(diff_text, max_lines=300)

        if use_ai:
            language = "en"
            if use_chinese:
                language = "cn"
            ai_analyzer = AIAnalyzer(language=language)
            if ai_analyzer.is_available:

                def provide_diff(item) -> Optional[str]:
                    return diff_provider.get_diff(item)

                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")
                analysis = ai_analyzer.analyze(
                    target, include_diff=True, diff_provider=provide_diff
                )
                if analysis:
                    ai_analyzer.display_analysis(target, analysis)

        if save_json:
            exporter = MRJSONExporter(project_path=project_path, output_dir=output_dir)
            exporter.export_mr(target.iid, title_hint=target.title)

    except Exception as exc:
        console.print("[red]Error: {0}[/red]".format(exc))
        sys.exit(1)


@cli.command("view-commit", context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("commit_sha")
@click.option(
    "--ai",
    "use_ai",
    is_flag=True,
    default=False,
    help="Enable AI analysis (requires CURSOR_AGENT_PATH)",
)
@click.option(
    "--analyze",
    "-a",
    "use_ai_legacy",
    is_flag=True,
    default=False,
    hidden=True,
    help="alias of --ai",
)
def view_commit(commit_sha: str, use_ai: bool, use_ai_legacy: bool) -> None:
    """View details of a specific commit."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    if use_ai_legacy:
        use_ai = True

    try:
        commit_collector = CommitCollector()
        commit = commit_collector.get_commit_details(commit_sha)
        if not commit:
            console.print("[red]Commit {0} not found[/red]".format(commit_sha))
            return

        render_commit_panel(commit)

        diff_provider = DiffProvider(".")
        if Confirm.ask("\nShow diff?", default=True):
            diff_text = diff_provider.get_commit_diff(commit)
            display_diff_text(diff_text, max_lines=300)

        if use_ai:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_available:

                def provide_diff(item) -> Optional[str]:
                    return diff_provider.get_diff(item)

                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")
                analysis = ai_analyzer.analyze(
                    commit, include_diff=True, diff_provider=provide_diff
                )
                if analysis:
                    ai_analyzer.display_analysis(commit, analysis)

    except Exception as exc:
        console.print("[red]Error: {0}[/red]".format(exc))
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo",
    "-r",
    help="Repository in format group/subgroup/project or local repo directory (auto-detect if not specified)",
)
@click.option("--days", "-d", type=int, default=60, show_default=True)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export traversed MRs into JSON files",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Disable MR JSON export",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gl_pr_exports"),
    show_default=True,
    help="Directory for exported MR JSON files",
)
@click.option(
    "-cn",
    "--chinese",
    "use_chinese",
    is_flag=True,
    default=False,
    help="Output AI analysis in Chinese (requires --ai)",
)
@click.option(
    "--ai",
    "use_ai",
    is_flag=True,
    default=False,
    help="Enable AI analysis (requires CURSOR_AGENT_PATH)",
)
@click.option(
    "--analyze",
    "-a",
    "use_ai_legacy",
    is_flag=True,
    default=False,
    hidden=True,
    help="alias of --ai",
)
def traverse(
    repo: Optional[str],
    days: int,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
    use_chinese: bool,
    use_ai: bool,
    use_ai_legacy: bool,
) -> None:
    """Traverse recent MRs and optionally analyze them with AI."""
    print_banner()

    if days <= 0:
        console.print("[red]days must be a positive integer[/red]")
        sys.exit(1)

    if not check_prerequisites():
        sys.exit(1)

    project_path = resolve_repo_identifier(repo)

    if use_ai_legacy:
        use_ai = True

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=False, command_name="traverse"
    )

    try:
        collector = MergeRequestCollector(project_path)
        data = collector.collect(days=days)
        open_mrs = data.get("open", [])
        merged_mrs = data.get("merged", [])

        console.print("\n[bold]Repository:[/bold] {0}\n".format(project_path))
        console.print("[bold cyan]Traversal summary:[/bold cyan]")
        console.print("  • Open MRs (last {0} days): {1}".format(days, len(open_mrs)))
        console.print(
            "  • Merged MRs (last {0} days): {1}".format(days, len(merged_mrs))
        )

        if not open_mrs and not merged_mrs:
            console.print("[yellow]No MRs found in the specified range[/yellow]")
            return

        if use_ai:
            language = "en"
            if use_chinese:
                language = "cn"
            ai_analyzer = AIAnalyzer(language=language)
            if not ai_analyzer.is_available:
                console.print(
                    "[red]AI analysis not available. Please set CURSOR_AGENT_PATH environment variable[/red]"
                )
                sys.exit(1)

            diff_provider = DiffProvider(project_path)

            def provide_diff(item) -> Optional[str]:
                return diff_provider.get_diff(item)

            analyzed_items: List[tuple[MergeRequestSummary, Optional[str]]] = []

            exporter = None
            if save_json:
                exporter = MRJSONExporter(project_path=project_path, output_dir=output_dir)

            def analyze_group(items: List[MergeRequestSummary], label: str) -> None:
                if not items:
                    console.print(
                        "[yellow]No {0} to analyze[/yellow]".format(label.lower())
                    )
                    return

                console.print("\n[bold cyan]Analyzing {0}...[/bold cyan]".format(label))
                total = len(items)
                index_value = 1
                for mr in items:
                    console.print(
                        "\n[bold]Analyzing {0} {1}/{2}: MR !{3}[/bold]".format(
                            label[:-1], index_value, total, mr.iid
                        )
                    )
                    analysis = ai_analyzer.analyze(
                        mr, include_diff=True, diff_provider=provide_diff
                    )
                    analyzed_items.append((mr, analysis))
                    if analysis:
                        ai_analyzer.display_analysis(mr, analysis)

                    if save_json and exporter:
                        try:
                            path = exporter.export_mr(mr.iid, title_hint=mr.title)
                            console.print(
                                "[green]✓ JSON saved: {0}[/green]\n".format(path)
                            )
                        except Exception as exc:
                            console.print(
                                "[red]Failed to export MR !{0}: {1}[/red]\n".format(
                                    mr.iid, exc
                                )
                            )

                    index_value += 1

            analyze_group(merged_mrs, "Merged MRs")
            analyze_group(open_mrs, "Open MRs")

            if save_json and analyzed_items:
                report = ai_analyzer.generate_summary_report(
                    analyzed_items,
                    query="Traversal analysis for last {0} days".format(days),
                )
                report_file = "mr_traversal_report_{0}_{1}d.md".format(
                    project_path.replace("/", "_"), days
                )
                Path(report_file).write_text(report, encoding="utf-8")
                console.print("[green]✓ Report saved to: {0}[/green]".format(report_file))
        else:
            if save_json:
                exporter = MRJSONExporter(project_path=project_path, output_dir=output_dir)
                saved = 0
                for mr in merged_mrs:
                    try:
                        exporter.export_mr(mr.iid, title_hint=mr.title)
                        saved += 1
                    except Exception as exc:
                        console.print(
                            "[red]Failed to export MR !{0}: {1}[/red]".format(mr.iid, exc)
                        )
                for mr in open_mrs:
                    try:
                        exporter.export_mr(mr.iid, title_hint=mr.title)
                        saved += 1
                    except Exception as exc:
                        console.print(
                            "[red]Failed to export MR !{0}: {1}[/red]".format(mr.iid, exc)
                        )
                if saved == 0:
                    console.print("[yellow]No MR JSON files were created[/yellow]")
                else:
                    console.print(
                        "[green]✓ Exported {0} MR file(s) to {1}[/green]".format(
                            saved, str(output_dir)
                        )
                    )

    except Exception as exc:
        console.print("[red]Error: {0}[/red]".format(exc))
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--ai",
    "use_ai",
    is_flag=True,
    default=False,
    help="Enable AI features in interactive mode (requires CURSOR_AGENT_PATH)",
)
@click.option(
    "--analyze",
    "-a",
    "use_ai_legacy",
    is_flag=True,
    default=False,
    hidden=True,
    help="alias of --ai",
)
def interactive(use_ai: bool, use_ai_legacy: bool) -> None:
    """Interactive mode for exploring MRs and commits."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    if use_ai_legacy:
        use_ai = True

    try:
        repo_input = Prompt.ask(
            "\n[magenta]Repository (group/subgroup/project, or press Enter to auto-detect)[/magenta]",
            default="",
        )
        months = int(Prompt.ask("[magenta]Months to look back[/magenta]", default="3"))
        if months <= 0:
            console.print("[red]months must be a positive integer[/red]")
            sys.exit(1)

        project_path = resolve_repo_identifier(repo_input or None)
        console.print("\n[bold]Repository:[/bold] {0}\n".format(project_path))

        mr_collector = MergeRequestCollector(project_path)
        data = mr_collector.collect_by_months(months=months)
        merge_requests = data.get("open", []) + data.get("merged", [])

        commit_collector = CommitCollector()
        commits = commit_collector.collect_commits(days=months * 30)

        diff_provider = DiffProvider(project_path)
        matcher = Matcher(minimum_score=30)
        ai_analyzer = None
        if use_ai:
            ai_analyzer = AIAnalyzer()

        console.print("[bold cyan]Data collected:[/bold cyan]")
        console.print("  • Total MRs: {0}".format(len(merge_requests)))
        console.print("  • Total Commits: {0}".format(len(commits)))

        while True:
            console.print("\n[bold magenta]Options:[/bold magenta]")
            console.print("  1. Search by query")
            console.print("  2. View specific MR")
            console.print("  3. View specific commit")
            console.print("  4. Exit")

            choice = Prompt.ask(
                "\n[magenta]Choose an option[/magenta]", choices=["1", "2", "3", "4"]
            )

            if choice == "1":
                query = Prompt.ask("\n[magenta]Enter search query[/magenta]")
                results = matcher.search(merge_requests, commits, query)
                display_results_table(results)

                if use_ai and ai_analyzer is not None and results:
                    if Confirm.ask("\nAnalyze results with AI?", default=False):
                        if ai_analyzer.is_available:

                            def provide_diff(item) -> Optional[str]:
                                return diff_provider.get_diff(item)

                            items = [r.item for r in results[:5]]
                            analyzed = ai_analyzer.batch_analyze(
                                items, include_diff=True, diff_provider=provide_diff
                            )
                            for item, analysis in analyzed:
                                if analysis:
                                    ai_analyzer.display_analysis(item, analysis)
                        else:
                            console.print("[yellow]AI analysis not available[/yellow]")

            elif choice == "2":
                iid = int(Prompt.ask("\n[magenta]Enter MR iid[/magenta]"))
                target = None
                for mr in merge_requests:
                    if mr.iid == iid:
                        target = mr
                        break
                if target:
                    render_merge_request_panel(target)
                else:
                    console.print("[yellow]MR !{0} not found[/yellow]".format(iid))

            elif choice == "3":
                sha = Prompt.ask("\n[magenta]Enter commit SHA[/magenta]")
                commit = commit_collector.get_commit_details(sha)
                if commit:
                    render_commit_panel(commit)
                else:
                    console.print("[yellow]Commit {0} not found[/yellow]".format(sha))

            elif choice == "4":
                console.print("\n[magenta]goodbye![/magenta]")
                break

    except KeyboardInterrupt:
        console.print("\n[magenta]interrupted by user[/magenta]")
        sys.exit(0)
    except Exception as exc:
        console.print("[red]Error: {0}[/red]".format(exc))
        sys.exit(1)


# legacy aliases for backward compatibility
cli.add_command(view_pr, name="view_mr")
cli.add_command(view_commit, name="view_commit")


if __name__ == "__main__":
    cli()
