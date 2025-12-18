#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diff provider for merge requests and commits with fallback mechanisms."""

from typing import Optional, Union
from rich.console import Console

from .mr_collector import MergeRequestSummary
from .commit_collector import CommitSummary
from .gitlab_client import GitLabClient
from .utils import run_command

console = Console()


class DiffProvider:
    """provides diff content with multiple fallback strategies."""

    def __init__(self, project_path: str, client: Optional[GitLabClient] = None):
        self.project_path = project_path
        self.client = client or GitLabClient()
        self.project = self.client.get_project(project_path)
        self._glab_available = self._check_glab_availability()

    def _check_glab_availability(self) -> bool:
        """check if glab command is available."""
        try:
            returncode, _, _ = run_command(["glab", "--version"], check=False)
            return returncode == 0
        except Exception:
            return False

    def _get_mr_diff_via_glab(self, mr: MergeRequestSummary) -> Optional[str]:
        """get merge request diff using glab command."""
        if not self._glab_available:
            return None

        try:
            command = [
                "glab",
                "mr",
                "diff",
                str(mr.iid),
                "--repo",
                self.project_path,
            ]
            _, stdout, stderr = run_command(command, check=False)
            
            if stderr and "not found" in stderr.lower():
                console.print(f"[yellow]glab command failed: {stderr}[/yellow]")
                return None
                
            return stdout if stdout else None
        except Exception as error:
            console.print(f"[yellow]glab command error: {error}[/yellow]")
            return None

    def _get_mr_diff_via_api(self, mr: MergeRequestSummary) -> Optional[str]:
        """get merge request diff using GitLab API."""
        try:
            # get the merge request object from GitLab API
            gitlab_mr = self.project.mergerequests.get(mr.iid)
            
            # get changes/diffs from the merge request
            changes = gitlab_mr.changes()
            
            if not changes or 'changes' not in changes:
                return None
                
            # format the diff content
            diff_lines = []
            for change in changes['changes']:
                if 'diff' in change:
                    diff_lines.append(f"--- a/{change.get('old_path', 'unknown')}")
                    diff_lines.append(f"+++ b/{change.get('new_path', 'unknown')}")
                    diff_lines.append(change['diff'])
                    diff_lines.append("")
            
            return "\n".join(diff_lines) if diff_lines else None
            
        except Exception as error:
            console.print(f"[yellow]API diff fetch failed: {error}[/yellow]")
            return None

    def get_merge_request_diff(self, mr: MergeRequestSummary) -> Optional[str]:
        """get merge request diff using multiple fallback strategies."""
        console.print(f"[dim]Fetching diff for MR !{mr.iid}...[/dim]")
        
        # strategy 1: try glab command first (fastest when available)
        if self._glab_available:
            diff = self._get_mr_diff_via_glab(mr)
            if diff:
                console.print(f"[dim]✓ Got diff via glab[/dim]")
                return diff
        
        # strategy 2: try GitLab API
        diff = self._get_mr_diff_via_api(mr)
        if diff:
            console.print(f"[dim]✓ Got diff via API[/dim]")
            return diff
        
        console.print(f"[yellow]⚠ Could not fetch diff for MR !{mr.iid}[/yellow]")
        return None

    def get_commit_diff(self, commit: CommitSummary) -> Optional[str]:
        """get commit diff using GitLab API."""
        try:
            console.print(f"[dim]Fetching diff for commit {commit.short_sha}...[/dim]")
            commit_obj = self.project.commits.get(commit.sha)
            changes = commit_obj.diff()
            if not isinstance(changes, list):
                return None

            diff_lines = []
            for change in changes:
                old_path = change.get("old_path", "unknown")
                new_path = change.get("new_path", old_path)
                diff_text = change.get("diff")

                diff_lines.append(f"--- a/{old_path}")
                diff_lines.append(f"+++ b/{new_path}")
                if diff_text:
                    diff_lines.append(diff_text)
                diff_lines.append("")

            if not diff_lines:
                return None
            console.print(f"[dim]✓ Got commit diff via API[/dim]")
            return "\n".join(diff_lines)
        except Exception as error:
            console.print(f"[yellow]failed to get commit diff: {error}[/yellow]")
            return None

    def get_diff(self, item: Union[MergeRequestSummary, CommitSummary]) -> Optional[str]:
        """get diff for either merge request or commit."""
        if isinstance(item, MergeRequestSummary):
            return self.get_merge_request_diff(item)
        elif isinstance(item, CommitSummary):
            return self.get_commit_diff(item)
        else:
            console.print(f"[red]unsupported item type: {type(item)}[/red]")
            return None
