#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Module for AI-powered analysis of PRs and commits using cursor-agent CLI.

MIT License

Copyright (c) 2025 GitHub PR Analyzer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from pathlib import Path
from typing import Optional, List, Union
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich.padding import Padding

from .config import config
from .pr_collector import PullRequest
from .commit_collector import Commit
from .diff_viewer import DiffViewer
from .utils import run_command

console = Console(soft_wrap=True)


class AIAnalyzer:
    """analyzer for summarizing PRs and commits using AI."""

    def __init__(
        self,
        cursor_agent_path: Optional[str] = None,
        language: str = "en",
    ):
        """
        initialize AI analyzer.

        Args:
            cursor_agent_path: path to cursor-agent executable
            language: output language ('en' for English, 'cn' for Chinese)
        """
        self.cursor_agent_path = cursor_agent_path or config.cursor_agent_path
        self.language = language
        self.is_available = self._check_availability()

    def _check_availability(self) -> bool:
        """
        check if cursor-agent is available.

        Returns:
            bool: True if cursor-agent is available
        """
        if not self.cursor_agent_path:
            console.print(
                "[yellow]AI analysis not available: cursor-agent path not configured[/yellow]"
            )
            console.print(
                "[yellow]Set CURSOR_AGENT_PATH environment variable to enable AI features[/yellow]"
            )
            return False

        cursor_path = Path(self.cursor_agent_path)
        if not cursor_path.exists():
            console.print(
                f"[yellow]cursor-agent not found at: {self.cursor_agent_path}[/yellow]"
            )
            return False

        return True

    def _create_analysis_prompt(
        self,
        item: Union[PullRequest, Commit],
        diff_content: Optional[str] = None,
        analysis_type: str = "summary",
    ) -> str:
        """
        create prompt for AI analysis.

        Args:
            item: PR or Commit to analyze
            diff_content: diff content (optional)
            analysis_type: type of analysis (summary, impact, technical)

        Returns:
            str: formatted prompt
        """
        if isinstance(item, PullRequest):
            # build author display string
            author_display = item.author
            if item.author_name:
                author_display = f"{item.author_name} (@{item.author})"
            if item.author_email:
                author_display += f" <{item.author_email}>"

            base_info = f"""
# Pull Request Analysis

**PR #{item.number}**: {item.title}
**Author**: {author_display}
**State**: {item.state}
**Created**: {item.created_at}
**URL**: {item.url}

## Description
{item.body or 'No description provided.'}

## Statistics
- **Files Changed**: {item.changed_files}
- **Additions**: {item.additions}
- **Deletions**: {item.deletions}
- **Labels**: {', '.join(item.labels) if item.labels else 'None'}
"""
        else:
            base_info = f"""
# Commit Analysis

**Commit**: {item.short_sha}
**Author**: {item.author} <{item.author_email}>
**Date**: {item.committed_date}
**URL**: {item.get_url() or 'N/A'}

## Commit Message
{item.message}

## Statistics
- **Files Changed**: {item.files_changed}
- **Insertions**: {item.insertions}
- **Deletions**: {item.deletions}
- **Is Merge Commit**: {item.is_merge}
"""

        if self.language == "cn":
            task = self._get_chinese_task(analysis_type)
        else:
            task = self._get_english_task(analysis_type)

        prompt = base_info + "\n" + task

        if diff_content:
            prompt += f"""

## Code Diff
```diff
{diff_content[:5000]}  
```
{"(Diff truncated for brevity)" if len(diff_content) > 5000 else ""}
"""

        return prompt

    def _get_english_task(self, analysis_type: str) -> str:
        """get English task description for AI analysis."""
        if analysis_type == "summary":
            return """
Please provide a concise summary of this change:
1. What is the main purpose of this change?
2. What key functionality or features are affected?
3. What is the overall impact?

Keep the summary under 200 words.
"""
        elif analysis_type == "impact":
            return """
Please analyze the impact of this change:
1. What areas of the codebase are affected?
2. What are the potential risks or benefits?
3. Are there any breaking changes?
4. What testing or validation is recommended?

Provide a detailed but concise analysis.
"""
        elif analysis_type == "technical":
            return """
Please provide a technical analysis:
1. What technical approach was used?
2. Are there any notable implementation details?
3. How does this fit into the overall architecture?
4. Are there any performance or security considerations?

Focus on technical depth.
"""
        return "Please analyze this change and provide insights."

    def _get_chinese_task(self, analysis_type: str) -> str:
        """get Chinese task description for AI analysis."""
        if analysis_type == "summary":
            return """
请用中文提供此变更的简要总结：
1. 此变更的主要目的是什么？
2. 受影响的关键功能或特性有哪些？
3. 整体影响是什么？

请保持总结在 200 字以内，使用左对齐格式。
"""
        elif analysis_type == "impact":
            return """
请用中文分析此变更的影响：
1. 代码库中哪些区域受到影响？
2. 有哪些潜在的风险或收益？
3. 是否有破坏性变更？
4. 建议进行哪些测试或验证？

请提供详细但简洁的分析，使用左对齐格式。
"""
        elif analysis_type == "technical":
            return """
请用中文提供技术分析：
1. 使用了什么技术方案？
2. 有哪些值得注意的实现细节？
3. 这如何融入整体架构？
4. 有哪些性能或安全方面的考虑？

请专注于技术深度，使用左对齐格式。
"""
        return "请用中文分析此变更并提供见解，使用左对齐格式。"

    def analyze(
        self,
        item: Union[PullRequest, Commit],
        include_diff: bool = True,
        analysis_type: str = "summary",
        diff_viewer: Optional[DiffViewer] = None,
    ) -> Optional[str]:
        """
        analyze a PR or commit using AI.

        Args:
            item: PR or Commit to analyze
            include_diff: whether to include diff in analysis
            analysis_type: type of analysis
            diff_viewer: DiffViewer instance for fetching diffs

        Returns:
            str: AI analysis result or None if failed
        """
        if not self.is_available:
            console.print("[red]AI analysis not available[/red]")
            return None

        console.print(f"[cyan]Analyzing with AI...[/cyan]")

        diff_content = None
        if include_diff and diff_viewer:
            if isinstance(item, PullRequest):
                diff_content = diff_viewer.get_pr_diff(item.number)
            else:
                diff_content = diff_viewer.get_commit_diff(item.sha)

        prompt = self._create_analysis_prompt(item, diff_content, analysis_type)

        try:
            command = [
                self.cursor_agent_path,
                "--print",
                "--output-format",
                "text",
                "agent",
                prompt,
            ]

            _, stdout, stderr = run_command(command, check=False)

            if stderr:
                console.print(f"[yellow]Warning: {stderr}[/yellow]")

            if stdout:
                return stdout.strip()
            else:
                console.print("[red]AI analysis produced no output[/red]")
                return None

        except Exception as e:
            console.print(f"[red]Error during AI analysis: {str(e)}[/red]")
            return None

    def batch_analyze(
        self,
        items: List[Union[PullRequest, Commit]],
        include_diff: bool = False,
        analysis_type: str = "summary",
        diff_viewer: Optional[DiffViewer] = None,
    ) -> List[tuple[Union[PullRequest, Commit], Optional[str]]]:
        """
        analyze multiple items in batch.

        Args:
            items: list of PRs or Commits to analyze
            include_diff: whether to include diff in analysis
            analysis_type: type of analysis
            diff_viewer: DiffViewer instance

        Returns:
            list: list of (item, analysis) tuples
        """
        if not self.is_available:
            console.print("[red]AI analysis not available[/red]")
            return [(item, None) for item in items]

        results = []
        total = len(items)

        for idx, item in enumerate(items, 1):
            console.print(f"[cyan]Analyzing {idx}/{total}...[/cyan]")

            analysis = self.analyze(item, include_diff, analysis_type, diff_viewer)
            results.append((item, analysis))

        return results

    def display_analysis(self, item: Union[PullRequest, Commit], analysis: str):
        """
        display analysis result in a formatted way with author info and adaptive width.

        Args:
            item: analyzed item
            analysis: analysis text
        """
        # build metadata table for item info (left-aligned)
        meta_table = Table.grid(padding=(0, 2), expand=False)
        meta_table.add_column(style="bold cyan", justify="left", width=12)
        meta_table.add_column(style="white", justify="left")

        if isinstance(item, PullRequest):
            title = f"📋 PR #{item.number}: {item.title}"
            meta_table.add_row("Author:", f"@{item.author}")
            if item.author_name:
                meta_table.add_row("Name:", item.author_name)
            if item.author_email:
                meta_table.add_row("Email:", f"[cyan]{item.author_email}[/cyan]")
            meta_table.add_row("State:", self._format_state(item.state))
            meta_table.add_row("URL:", f"[link={item.url}]{item.url}[/link]")
        else:
            title = f"📝 Commit {item.short_sha}"
            meta_table.add_row("Author:", item.author)
            meta_table.add_row("Email:", f"[cyan]{item.author_email}[/cyan]")
            meta_table.add_row("Committer:", item.committer)
            meta_table.add_row("Date:", str(item.committed_date))
            commit_url = item.get_url()
            if commit_url:
                meta_table.add_row("URL:", f"[link={commit_url}]{commit_url}[/link]")
            meta_table.add_row("Files:", str(item.files_changed))
            meta_table.add_row(
                "Changes:",
                f"[green]+{item.insertions}[/green] / [red]-{item.deletions}[/red]"
            )

        try:
            # create header panel with metadata (left-aligned)
            header_panel = Panel(
                meta_table,
                title=f"[bold white]{title}[/bold white]",
                title_align="left",
                border_style="bright_blue",
                style=Style(bgcolor="grey15"),
                padding=(0, 1),
            )

            # create analysis content with markdown (left-aligned)
            md = Markdown(analysis, code_theme="monokai", justify="left")
            content_panel = Panel(
                md,
                title="[bold green]✨ AI Analysis[/bold green]",
                title_align="left",
                border_style="green",
                style=Style(color="white", bgcolor="grey23"),
                padding=(1, 2),
            )

            # print with adaptive width
            console.print()
            console.print(header_panel)
            console.print(content_panel)
            console.print()

        except Exception:
            # fallback display
            console.print()
            console.print(Rule(title, style="cyan"))
            console.print(f"[white]{analysis}[/white]")
            console.print()

    def _format_state(self, state: str) -> str:
        """format PR state with color and emoji."""
        state_formats = {
            "MERGED": "[magenta]✅ MERGED[/magenta]",
            "OPEN": "[green]🔄 OPEN[/green]",
            "CLOSED": "[red]❌ CLOSED[/red]",
        }
        return state_formats.get(state, state)

    def generate_summary_report(
        self,
        analyzed_items: List[tuple[Union[PullRequest, Commit], Optional[str]]],
        query: Optional[str] = None,
    ) -> str:
        """
        generate a summary report from analyzed items.

        Args:
            analyzed_items: list of (item, analysis) tuples
            query: original search query

        Returns:
            str: formatted report
        """
        report_lines = []
        report_lines.append("# GitHub PR & Commit Analysis Report")
        report_lines.append("")

        if query:
            report_lines.append(f"**Search Query**: {query}")
            report_lines.append("")

        report_lines.append(f"**Total Items Analyzed**: {len(analyzed_items)}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        for idx, (item, analysis) in enumerate(analyzed_items, 1):
            if isinstance(item, PullRequest):
                report_lines.append(f"## {idx}. PR #{item.number}: {item.title}")
                # build author display string
                author_display = item.author
                if item.author_name:
                    author_display = f"{item.author_name} (@{item.author})"
                report_lines.append(f"- **Author**: {author_display}")
                if item.author_email:
                    report_lines.append(f"- **Email**: {item.author_email}")
                report_lines.append(f"- **State**: {item.state}")
                report_lines.append(f"- **URL**: {item.url}")
            else:
                title = item.message.split("\n")[0]
                report_lines.append(f"## {idx}. Commit {item.short_sha}: {title}")
                report_lines.append(f"- **Author**: {item.author} <{item.author_email}>")
                report_lines.append(f"- **Committer**: {item.committer}")
                report_lines.append(f"- **Date**: {item.committed_date}")
                report_lines.append(f"- **Changes**: +{item.insertions} / -{item.deletions} ({item.files_changed} files)")
                if item.get_url():
                    report_lines.append(f"- **URL**: {item.get_url()}")

            report_lines.append("")

            if analysis:
                report_lines.append("### Analysis")
                report_lines.append(analysis)
            else:
                report_lines.append("*No analysis available*")

            report_lines.append("")
            report_lines.append("---")
            report_lines.append("")

        return "\n".join(report_lines)
