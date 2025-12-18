#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Commit collector for GitLab projects."""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .gitlab_client import GitLabClient

console = Console()


@dataclass
class CommitSummary:
    """minimal commit information."""

    sha: str
    short_sha: str
    message: str
    author: str
    author_email: Optional[str]
    committed_date: str
    authored_date: Optional[str]
    parents: List[str]
    is_merge: bool
    files_changed: int
    insertions: int
    deletions: int
    web_url: Optional[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "sha": self.sha,
            "short_sha": self.short_sha,
            "message": self.message,
            "author": self.author,
            "author_email": self.author_email,
            "committed_date": self.committed_date,
            "authored_date": self.authored_date,
            "parent_count": len(self.parents),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "web_url": self.web_url,
        }


class CommitCollector:
    """collect commits using GitLab API."""

    def __init__(self, project_path: str, client: Optional[GitLabClient] = None):
        cleaned = str(project_path or "").strip()
        if not cleaned:
            raise RuntimeError("project path is required")

        self.project_path = cleaned
        self.client = client or GitLabClient()
        self.project = self.client.get_project(cleaned)

    def _convert(self, commit_obj) -> CommitSummary:
        sha = getattr(commit_obj, "id", None)
        if not sha:
            sha = getattr(commit_obj, "sha", None)
        if not sha:
            sha = ""

        short_sha = getattr(commit_obj, "short_id", None)
        if not short_sha:
            short_sha = sha[:7]

        message = getattr(commit_obj, "message", None)
        if not message:
            message = getattr(commit_obj, "title", None)
        if not message:
            message = ""
        message = str(message).strip()

        author = getattr(commit_obj, "author_name", None)
        if not author:
            author = getattr(commit_obj, "committer_name", None)
        if not author:
            author = "unknown"

        author_email = getattr(commit_obj, "author_email", None)
        if not author_email:
            author_email = getattr(commit_obj, "committer_email", None)

        committed_date = getattr(commit_obj, "committed_date", None)
        if not committed_date:
            committed_date = getattr(commit_obj, "created_at", None)
        if not committed_date:
            committed_date = ""

        authored_date = getattr(commit_obj, "authored_date", None)

        parents = getattr(commit_obj, "parent_ids", None)
        if not isinstance(parents, list):
            parents = []

        is_merge = False
        if len(parents) > 1:
            is_merge = True

        insertions = 0
        deletions = 0
        files_changed = 0

        stats = getattr(commit_obj, "stats", None)
        if isinstance(stats, dict):
            additions_value = stats.get("additions")
            deletions_value = stats.get("deletions")

            if additions_value is not None:
                try:
                    insertions = int(additions_value)
                except Exception:
                    insertions = 0

            if deletions_value is not None:
                try:
                    deletions = int(deletions_value)
                except Exception:
                    deletions = 0

        web_url = getattr(commit_obj, "web_url", None)

        return CommitSummary(
            sha=sha,
            short_sha=short_sha,
            message=message,
            author=author,
            author_email=author_email,
            committed_date=str(committed_date),
            authored_date=str(authored_date) if authored_date else None,
            parents=parents,
            is_merge=is_merge,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
            web_url=str(web_url) if web_url else None,
        )

    def collect_commits(
        self,
        days: int = 60,
        include_merge_only: bool = False,
    ) -> List[CommitSummary]:
        """collect commits within the given days."""
        if days <= 0:
            raise ValueError("days must be positive")

        since_dt = datetime.now(timezone.utc) - timedelta(days=days)
        since = since_dt.isoformat().replace("+00:00", "Z")

        results: List[CommitSummary] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Collecting commits...", total=None)
            commits = self.project.commits.list(since=since, all=True)
            for commit_obj in commits:
                summary = self._convert(commit_obj)
                if include_merge_only and not summary.is_merge:
                    continue
                results.append(summary)
            progress.update(task, completed=True)

        console.print(f"[green]✓ Collected {len(results)} commits[/green]")
        return results

    def get_commit_details(self, sha: str) -> Optional[CommitSummary]:
        """get details for a specific commit."""
        try:
            commit_obj = self.project.commits.get(sha)
            summary = self._convert(commit_obj)

            try:
                diffs = commit_obj.diff()
                if isinstance(diffs, list):
                    summary.files_changed = len(diffs)
            except Exception:
                pass

            return summary
        except Exception as error:
            console.print(f"[red]Error getting commit {sha}: {error}[/red]")
            return None
