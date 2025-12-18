#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for PRJSONExporter JSON structure."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from git import Repo

from src.pr_exporter import PRJSONExporter


class TestPRJSONExporter(TestCase):
    """validate the exported JSON payload."""

    def setUp(self):
        """prepare a temporary git repo with commits."""
        self.temp_dir = TemporaryDirectory()
        self.repo_path = Path(self.temp_dir.name)
        self.output_dir = self.repo_path / "exports"

        self.repo = Repo.init(self.repo_path)
        sample_file = self.repo_path / "sample.txt"
        sample_file.write_text("initial\n")
        self.repo.index.add([str(sample_file)])
        self.repo.index.commit("initial commit")

        sample_file.write_text("initial\nchange\n")
        self.repo.index.add([str(sample_file)])
        self.commit = self.repo.index.commit("adjust flow (#42)")

    def tearDown(self):
        """clean up temp directory."""
        self.temp_dir.cleanup()

    def _fake_pr_payload(self) -> dict:
        """build mocked gh cli payload."""
        return {
            "number": 42,
            "title": "Improve login flow",
            "url": "https://github.com/octo/example/pull/42",
            "body": "refine login behavior",
            "author": {"login": "contributor"},
            "state": "OPEN",
            "createdAt": "2025-01-02T00:00:00Z",
            "updatedAt": "2025-01-03T00:00:00Z",
            "mergedAt": None,
            "baseRefName": "main",
            "headRefName": "feature/login",
            "commits": {
                "nodes": [
                    {
                        "commit": {
                            "oid": self.commit.hexsha,
                            "messageHeadline": "adjust flow (#42)",
                            "message": "adjust flow (#42)\n\nadd safeguard checks",
                            "messageBody": "add safeguard checks",
                        }
                    }
                ]
            },
            "comments": {
                "nodes": [
                    {
                        "author": {"login": "reviewer"},
                        "bodyText": "please add a test",
                        "createdAt": "2025-01-02T01:00:00Z",
                        "updatedAt": "2025-01-02T01:05:00Z",
                        "url": "https://github.com/octo/example/pull/42#issuecomment-1",
                    }
                ]
            },
            "reviewThreads": {
                "nodes": [
                    {
                        "path": "sample.txt",
                        "isResolved": False,
                        "isOutdated": False,
                        "comments": {
                            "nodes": [
                                {
                                    "author": {"login": "thread_author"},
                                    "bodyText": "nit: rename var",
                                    "state": "COMMENTED",
                                    "createdAt": "2025-01-02T02:00:00Z",
                                    "updatedAt": "2025-01-02T02:05:00Z",
                                    "url": "https://github.com/octo/example/pull/42#discussion-1",
                                }
                            ]
                        },
                    }
                ]
            },
            "reviews": {
                "nodes": [
                    {
                        "author": {"login": "approver"},
                        "state": "APPROVED",
                        "bodyText": "ship it",
                        "submittedAt": "2025-01-02T03:00:00Z",
                        "url": "https://github.com/octo/example/pull/42#pullrequestreview-1",
                    }
                ]
            },
        }

    def test_exported_json_contains_full_sections(self):
        """ensure exporter writes commits, diffs, and conversations."""
        fake_payload = self._fake_pr_payload()

        with patch(
            "src.pr_exporter.run_command",
            return_value=(0, json.dumps(fake_payload), ""),
        ):
            exporter = PRJSONExporter(
                repo_name="octo/example",
                output_dir=self.output_dir,
                repo_path=str(self.repo_path),
            )
            exported_path = exporter.export_pr(42)

        data = json.loads(exported_path.read_text())

        self.assertEqual(data["repo"], "octo/example")
        self.assertEqual(data["pr"]["number"], 42)
        self.assertEqual(data["pr"]["title"], "Improve login flow")

        commits = data["commits"]
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0]["id"], self.commit.hexsha)
        self.assertIn("adjust flow", commits[0]["title"])
        self.assertTrue(commits[0]["files"], "commit files should not be empty")
        self.assertIn("sample.txt", commits[0]["files"][0]["path"])
        # diff is now an array of lines for better readability
        diff_lines = commits[0]["files"][0]["diff"]
        self.assertIsInstance(diff_lines, list)
        self.assertTrue(any("@@" in line for line in diff_lines))

        conversation = data["conversation"]
        # body is now an array of lines for better readability
        self.assertIn("please add a test", conversation["issue_comments"][0]["body"])
        self.assertIn(
            "nit: rename var",
            conversation["review_threads"][0]["comments"][0]["body"],
        )
        self.assertEqual(conversation["reviews"][0]["state"], "APPROVED")

