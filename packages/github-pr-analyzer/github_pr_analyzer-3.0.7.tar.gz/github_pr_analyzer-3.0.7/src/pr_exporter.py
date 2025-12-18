#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export pull request data with commits and conversations."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from rich.console import Console

from .commit_collector import Commit, CommitCollector
from .diff_viewer import DiffViewer
from .utils import run_command

console = Console()


class ExportError(RuntimeError):
    """raised when exporting PR data fails."""


class PRJSONExporter:
    """exporter that saves PR data with commit diffs and conversations."""

    def __init__(
        self,
        repo_name: str,
        output_dir: Optional[Path] = None,
        repo_path: str = ".",
    ):
        if not repo_name:
            raise ValueError("repo_name is required for exporting")

        if output_dir is None:
            resolved_output = Path.cwd() / "gh_pr_exports"
        else:
            resolved_output = Path(output_dir)

        self.repo_name = repo_name
        self.output_dir = resolved_output
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.repo_path = repo_path
        self.diff_viewer = DiffViewer(repo_path=self.repo_path, repo_name=self.repo_name)
        self.commit_collector = CommitCollector(
            repo_path=self.repo_path, repo_name=self.repo_name
        )

    def export_pr(self, pr_number: int, title_hint: Optional[str] = None) -> Path:
        """
        export a pull request into a JSON file with commit diffs and conversations.

        Args:
            pr_number: pull request number
            title_hint: optional fallback title

        Returns:
            Path: path to the exported JSON file
        """
        payload = self._fetch_pr_payload(pr_number)
        pr_title = payload.get("title")
        if not pr_title and title_hint:
            pr_title = title_hint
        if not pr_title:
            pr_title = f"pr_{pr_number}"

        # extract PR state and timestamp for filename
        pr_state = payload.get("state", "UNKNOWN")
        merged_at = payload.get("mergedAt")
        updated_at = payload.get("updatedAt")

        export_payload = {
            "repo": self.repo_name,
            "pr": self._build_pr_section(payload, pr_number, pr_title),
            "commits": self._build_commit_entries(payload),
            "conversation": self._build_conversation(payload),
        }

        file_path = self.output_dir / self._build_filename(
            pr_number, pr_title, pr_state, merged_at, updated_at
        )
        file_path.write_text(json.dumps(export_payload, ensure_ascii=False, indent=2))
        console.print(
            f"[green]✓ Saved PR #{pr_number} data to {str(file_path)}[/green]"
        )
        return file_path

    def _fetch_pr_payload(self, pr_number: int) -> Dict[str, Any]:
        fields = [
            "number",
            "title",
            "url",
            "body",
            "author",
            "state",
            "createdAt",
            "updatedAt",
            "mergedAt",
            "baseRefName",
            "headRefName",
            "commits",
            "comments",
            "reviews",
        ]

        try:
            command = [
                "gh",
                "pr",
                "view",
                str(pr_number),
                "--repo",
                self.repo_name,
                "--json",
                ",".join(fields),
            ]
            _, stdout, _ = run_command(command)
            return json.loads(stdout)
        except Exception as exc:
            raise ExportError(
                f"failed to fetch PR #{pr_number} data: {str(exc)}"
            ) from exc

    def _build_pr_section(
        self, payload: Dict[str, Any], pr_number: int, pr_title: str
    ) -> Dict[str, Any]:
        author_info = self._extract_author_info(payload.get("author"))
        pr_section = {
            "number": pr_number,
            "title": pr_title,
            "url": payload.get("url"),
            "author": author_info.get("login", "unknown"),
            "author_name": author_info.get("name"),
            "author_email": author_info.get("email"),
            "state": payload.get("state"),
            "created_at": payload.get("createdAt"),
            "updated_at": payload.get("updatedAt"),
            "merged_at": payload.get("mergedAt"),
            "base_ref": payload.get("baseRefName"),
            "head_ref": payload.get("headRefName"),
            "body": self._format_body_text(payload.get("body")),
        }
        return pr_section

    def _format_body_text(self, body: Optional[str]) -> List[str]:
        """
        format body text for better readability in JSON.

        - convert \\r\\n to \\n
        - remove trailing whitespace from each line
        - split into lines array

        Args:
            body: raw body text

        Returns:
            list of lines for readable JSON output
        """
        if not body:
            return []

        # normalize line endings: \r\n -> \n, \r -> \n
        normalized = body.replace("\r\n", "\n").replace("\r", "\n")

        # split into lines and strip trailing whitespace
        lines = [line.rstrip() for line in normalized.split("\n")]

        return lines

    def _extract_author_info(self, author_data: Any) -> Dict[str, Optional[str]]:
        """
        extract author information including login, name and email.

        Args:
            author_data: author data from GitHub API

        Returns:
            dict with login, name, and email fields
        """
        result: Dict[str, Optional[str]] = {
            "login": None,
            "name": None,
            "email": None,
        }

        if isinstance(author_data, dict):
            result["login"] = author_data.get("login")
            result["name"] = author_data.get("name")
            result["email"] = author_data.get("email")
        elif isinstance(author_data, str):
            result["login"] = author_data

        return result

    def _build_commit_entries(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        commit_nodes = self._extract_nodes(payload.get("commits"))
        seen_shas: set[str] = set()

        for node in commit_nodes:
            commit_data = node
            if isinstance(node, dict) and "commit" in node:
                commit_data = node.get("commit") or {}

            sha = self._pick_first_value(
                commit_data,
                ["oid", "abbreviatedOid", "sha"],
            )

            if not sha:
                continue
            if sha in seen_shas:
                continue
            seen_shas.add(sha)

            # try local repo first (silent mode), then fallback to API
            commit_obj = self.commit_collector.get_commit_details(sha, silent=True)
            title = self._extract_commit_title(commit_obj, commit_data)
            message = self._extract_commit_message(commit_obj, commit_data)
            committer_info = self._extract_committer_info(commit_obj, commit_data)

            # try local repo first, fallback to GitHub API if commit not available locally
            file_entries = self.diff_viewer.get_commit_file_diffs(sha, silent=True)
            if not file_entries:
                file_entries = self.diff_viewer.get_commit_file_diffs_from_api(sha)

            entry = {
                "id": sha,
                "title": title,
                "message": message,
                "committer_name": committer_info.get("name"),
                "committer_email": committer_info.get("email"),
                "files": file_entries,
            }
            entries.append(entry)

        return entries

    def _extract_committer_info(
        self, commit_obj: Optional[Commit], fallback_data: Dict[str, Any]
    ) -> Dict[str, Optional[str]]:
        """
        extract committer name and email from commit.

        Args:
            commit_obj: local Commit object (may be None)
            fallback_data: commit data from GitHub API

        Returns:
            dict with name and email fields
        """
        result: Dict[str, Optional[str]] = {
            "name": None,
            "email": None,
        }

        # try local commit object first
        if commit_obj:
            result["name"] = commit_obj.committer
            result["email"] = commit_obj.author_email
            return result

        # fallback to GitHub API data
        # GitHub API returns authors/committers in nested structure
        authors = fallback_data.get("authors")
        if isinstance(authors, dict):
            nodes = authors.get("nodes", [])
            if nodes and isinstance(nodes, list) and len(nodes) > 0:
                author_node = nodes[0]
                if isinstance(author_node, dict):
                    result["name"] = author_node.get("name")
                    result["email"] = author_node.get("email")

        return result

    def _extract_commit_title(
        self, commit_obj: Optional[Commit], fallback_data: Dict[str, Any]
    ) -> str:
        if commit_obj:
            commit_message = commit_obj.message.strip()
            if commit_message:
                first_line = commit_message.split("\n")[0].strip()
                if first_line:
                    return first_line

        candidates = [
            fallback_data.get("messageHeadline"),
            fallback_data.get("message"),
            fallback_data.get("messageHeadlineHTML"),
        ]
        for candidate in candidates:
            if candidate:
                stripped = str(candidate).strip()
                if stripped:
                    return stripped.split("\n")[0].strip()
        return ""

    def _extract_commit_message(
        self, commit_obj: Optional[Commit], fallback_data: Dict[str, Any]
    ) -> str:
        if commit_obj:
            return commit_obj.message

        candidates = [
            fallback_data.get("messageBody"),
            fallback_data.get("message"),
        ]
        for candidate in candidates:
            if candidate:
                return str(candidate)
        return ""

    def _build_conversation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        conversation = {
            "issue_comments": self._build_issue_comments(payload),
            "review_threads": self._build_review_threads(payload),
            "reviews": self._build_reviews(payload),
        }
        return conversation

    def _build_issue_comments(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        comments: List[Dict[str, Any]] = []
        nodes = self._extract_nodes(payload.get("comments"))

        for node in nodes:
            entry = {
                "author": self._safe_author(node.get("author")),
                "body": self._coalesce_body(node),
                "created_at": node.get("createdAt"),
                "updated_at": node.get("updatedAt"),
                "url": node.get("url"),
            }
            comments.append(entry)

        return comments

    def _build_review_threads(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        threads: List[Dict[str, Any]] = []
        nodes = self._extract_nodes(payload.get("reviewThreads"))

        for node in nodes:
            comments = []
            comment_nodes = self._extract_nodes(node.get("comments"))
            for comment in comment_nodes:
                comment_entry = {
                    "author": self._safe_author(comment.get("author")),
                    "body": self._coalesce_body(comment),
                    "state": comment.get("state"),
                    "created_at": comment.get("createdAt"),
                    "updated_at": comment.get("updatedAt"),
                    "url": comment.get("url"),
                }
                comments.append(comment_entry)

            thread_entry = {
                "path": node.get("path"),
                "is_resolved": node.get("isResolved"),
                "is_outdated": node.get("isOutdated"),
                "comments": comments,
            }
            threads.append(thread_entry)

        return threads

    def _build_reviews(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        reviews: List[Dict[str, Any]] = []
        nodes = self._extract_nodes(payload.get("reviews"))

        for node in nodes:
            entry = {
                "author": self._safe_author(node.get("author")),
                "state": node.get("state"),
                "body": self._coalesce_body(node),
                "submitted_at": node.get("submittedAt"),
                "url": node.get("url"),
            }
            reviews.append(entry)

        return reviews

    def _extract_nodes(self, value: Any) -> List[Dict[str, Any]]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nodes_value = value.get("nodes")
            if isinstance(nodes_value, list):
                return nodes_value
            edges_value = value.get("edges")
            if isinstance(edges_value, list):
                collected: List[Dict[str, Any]] = []
                for edge in edges_value:
                    node = edge.get("node")
                    if node:
                        collected.append(node)
                return collected
        return []

    def _safe_author(self, author_data: Any) -> str:
        if isinstance(author_data, dict):
            login = author_data.get("login")
            if login:
                return str(login)
            name = author_data.get("name")
            if name:
                return str(name)
        if isinstance(author_data, str):
            return author_data
        return "unknown"

    def _coalesce_body(self, node: Dict[str, Any]) -> List[str]:
        """
        extract and format body text from node.

        Args:
            node: data node containing body text

        Returns:
            list of lines for readable JSON output
        """
        for key in ["bodyText", "body"]:
            value = node.get(key)
            if value:
                return self._format_body_text(str(value))
        return []

    def _build_filename(
        self,
        pr_number: int,
        title: str,
        state: str,
        merged_at: Optional[str],
        updated_at: Optional[str],
    ) -> str:
        """
        build filename with PR state and timestamp.

        Format: {repo}_{merged_pr|open_pr}_{pr_number}_{title}_{timestamp}.json

        Args:
            pr_number: PR number
            title: PR title
            state: PR state (MERGED, OPEN, CLOSED)
            merged_at: merge timestamp (ISO format)
            updated_at: update timestamp (ISO format)

        Returns:
            formatted filename string
        """
        safe_repo = self.repo_name.replace("/", "_")

        # determine PR status label
        if state == "MERGED":
            status_label = "merged_pr"
        else:
            status_label = "open_pr"

        # clean title
        cleaned_title = title.strip()
        if not cleaned_title:
            cleaned_title = f"pr_{pr_number}"
        cleaned_title = re.sub(r"\s+", "_", cleaned_title)
        cleaned_title = re.sub(r"[^A-Za-z0-9_.-]", "_", cleaned_title)
        # truncate title if too long
        if len(cleaned_title) > 50:
            cleaned_title = cleaned_title[:50]

        # build timestamp from merged_at or updated_at
        timestamp = self._format_timestamp(merged_at if merged_at else updated_at)

        return f"{safe_repo}_{status_label}_{pr_number}_{cleaned_title}_{timestamp}.json"

    def _format_timestamp(self, iso_timestamp: Optional[str]) -> str:
        """
        format ISO timestamp to YYYYMMDD_HHMM format.

        Args:
            iso_timestamp: timestamp in ISO format (e.g., 2025-11-30T09:23:45Z)

        Returns:
            formatted timestamp string (e.g., 20251130_0923)
        """
        if not iso_timestamp:
            from datetime import datetime
            now = datetime.now()
            return now.strftime("%Y%m%d_%H%M")

        try:
            from datetime import datetime
            # parse ISO format timestamp
            dt = datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y%m%d_%H%M")
        except Exception:
            from datetime import datetime
            now = datetime.now()
            return now.strftime("%Y%m%d_%H%M")

    def _pick_first_value(
        self, data: Dict[str, Any], keys: Sequence[str]
    ) -> Optional[str]:
        for key in keys:
            if key in data:
                value = data.get(key)
                if value:
                    return str(value)
        return None

