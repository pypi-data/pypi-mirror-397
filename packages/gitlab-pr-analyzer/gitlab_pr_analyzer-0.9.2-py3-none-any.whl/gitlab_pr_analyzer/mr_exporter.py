#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""export merge request data with commits and discussions."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

from .gitlab_client import GitLabClient
from .utils import ensure_output_directory

console = Console()


class ExportError(RuntimeError):
    """raised when exporting MR data fails."""


class MRJSONExporter:
    """exporter that saves MR data with commits, changes and discussions."""

    def __init__(
        self,
        project_path: str,
        output_dir: Optional[Path] = None,
        client: Optional[GitLabClient] = None,
    ):
        if not project_path:
            raise ValueError("project_path is required for exporting")

        resolved_output = output_dir
        if resolved_output is None:
            resolved_output = Path.cwd() / "gl_pr_exports"
        resolved_output = Path(resolved_output)

        self.project_path = project_path
        self.output_dir = resolved_output
        ensure_output_directory(self.output_dir)

        self.client = client or GitLabClient()
        self.project = self.client.get_project(project_path)

    def export_mr(self, mr_iid: int, title_hint: Optional[str] = None) -> Path:
        """export a merge request into a JSON file."""
        payload = self._fetch_mr_payload(mr_iid)
        mr_section = payload.get("mr")
        if not isinstance(mr_section, dict):
            raise ExportError("unexpected payload shape: missing mr section")

        title = mr_section.get("title")
        if not title and title_hint:
            title = title_hint
        if not title:
            title = "mr_{0}".format(mr_iid)

        state = mr_section.get("state")
        merged_at = mr_section.get("merged_at")
        updated_at = mr_section.get("updated_at")

        file_path = self.output_dir / self._build_filename(
            mr_iid=mr_iid,
            title=str(title),
            state=str(state) if state else "UNKNOWN",
            merged_at=str(merged_at) if merged_at else None,
            updated_at=str(updated_at) if updated_at else None,
        )
        file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        console.print(
            "[green]✓ Saved MR !{0} data to {1}[/green]".format(mr_iid, str(file_path))
        )
        return file_path

    def _fetch_mr_payload(self, mr_iid: int) -> Dict[str, Any]:
        try:
            mr = self.project.mergerequests.get(mr_iid)
        except Exception as exc:
            raise ExportError("failed to fetch MR !{0}: {1}".format(mr_iid, exc)) from exc

        mr_dict: Dict[str, Any] = {
            "iid": getattr(mr, "iid", mr_iid),
            "id": getattr(mr, "id", None),
            "title": getattr(mr, "title", "") or "",
            "state": getattr(mr, "state", None),
            "created_at": getattr(mr, "created_at", None),
            "updated_at": getattr(mr, "updated_at", None),
            "merged_at": getattr(mr, "merged_at", None),
            "web_url": getattr(mr, "web_url", None),
            "description": getattr(mr, "description", None),
            "source_branch": getattr(mr, "source_branch", None),
            "target_branch": getattr(mr, "target_branch", None),
            "labels": getattr(mr, "labels", None) or [],
            "author": self._extract_author(mr),
        }

        commits = self._fetch_mr_commits(mr)
        changes = self._fetch_mr_changes(mr)
        discussions = self._fetch_mr_notes(mr)

        payload = {
            "project": self.project_path,
            "mr": mr_dict,
            "commits": commits,
            "changes": changes,
            "conversation": {"notes": discussions},
        }
        return payload

    def _extract_author(self, mr: Any) -> Dict[str, Optional[str]]:
        author_value = getattr(mr, "author", None)
        if isinstance(author_value, dict):
            return {
                "name": author_value.get("name"),
                "username": author_value.get("username"),
                "email": author_value.get("email"),
            }
        return {"name": None, "username": None, "email": None}

    def _fetch_mr_commits(self, mr: Any) -> List[Dict[str, Any]]:
        try:
            commits = mr.commits()
        except Exception:
            commits = []

        results: List[Dict[str, Any]] = []
        if isinstance(commits, list):
            for commit in commits:
                if not isinstance(commit, dict):
                    continue
                entry = {
                    "id": commit.get("id"),
                    "short_id": commit.get("short_id"),
                    "title": commit.get("title"),
                    "message": commit.get("message"),
                    "author_name": commit.get("author_name"),
                    "author_email": commit.get("author_email"),
                    "created_at": commit.get("created_at"),
                }
                results.append(entry)
        return results

    def _fetch_mr_changes(self, mr: Any) -> List[Dict[str, Any]]:
        try:
            changes_response = mr.changes()
        except Exception:
            return []

        if not isinstance(changes_response, dict):
            return []

        changes = changes_response.get("changes")
        if not isinstance(changes, list):
            return []

        results: List[Dict[str, Any]] = []
        for change in changes:
            if not isinstance(change, dict):
                continue
            diff_value = change.get("diff")
            diff_lines: List[str] = []
            if isinstance(diff_value, str) and diff_value:
                diff_lines = self._format_body_text(diff_value)
            results.append(
                {
                    "old_path": change.get("old_path"),
                    "new_path": change.get("new_path"),
                    "new_file": change.get("new_file"),
                    "renamed_file": change.get("renamed_file"),
                    "deleted_file": change.get("deleted_file"),
                    "diff": diff_lines,
                }
            )
        return results

    def _fetch_mr_notes(self, mr: Any) -> List[Dict[str, Any]]:
        try:
            notes = mr.notes.list(all=True)
        except Exception:
            return []

        results: List[Dict[str, Any]] = []
        for note in notes:
            try:
                author = getattr(note, "author", None)
                author_name = None
                author_username = None
                if isinstance(author, dict):
                    author_name = author.get("name")
                    author_username = author.get("username")
                entry = {
                    "id": getattr(note, "id", None),
                    "author_name": author_name,
                    "author_username": author_username,
                    "body": self._format_body_text(getattr(note, "body", "") or ""),
                    "created_at": getattr(note, "created_at", None),
                    "updated_at": getattr(note, "updated_at", None),
                    "system": getattr(note, "system", None),
                }
                results.append(entry)
            except Exception:
                continue
        return results

    def _format_body_text(self, body: str) -> List[str]:
        if not body:
            return []
        normalized = body.replace("\r\n", "\n").replace("\r", "\n")
        return [line.rstrip() for line in normalized.split("\n")]

    def _build_filename(
        self,
        mr_iid: int,
        title: str,
        state: str,
        merged_at: Optional[str],
        updated_at: Optional[str],
    ) -> str:
        safe_project = self.project_path.replace("/", "_")

        status_label = "open_pr"
        lowered = (state or "").lower()
        if lowered == "merged":
            status_label = "merged_pr"

        cleaned_title = title.strip()
        if not cleaned_title:
            cleaned_title = "mr_{0}".format(mr_iid)
        cleaned_title = re.sub(r"\s+", "_", cleaned_title)
        cleaned_title = re.sub(r"[^A-Za-z0-9_.-]", "_", cleaned_title)
        if len(cleaned_title) > 50:
            cleaned_title = cleaned_title[:50]

        timestamp = self._format_timestamp(updated_at)
        if merged_at:
            timestamp = self._format_timestamp(merged_at)

        return "{0}_{1}_{2}_{3}_{4}.json".format(
            safe_project, status_label, mr_iid, cleaned_title, timestamp
        )

    def _format_timestamp(self, iso_timestamp: Optional[str]) -> str:
        from datetime import datetime

        if not iso_timestamp:
            now = datetime.now()
            return now.strftime("%Y%m%d_%H%M")

        try:
            dt = datetime.fromisoformat(str(iso_timestamp).replace("Z", "+00:00"))
            return dt.strftime("%Y%m%d_%H%M")
        except Exception:
            now = datetime.now()
            return now.strftime("%Y%m%d_%H%M")


