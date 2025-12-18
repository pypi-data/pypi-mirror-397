#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Command-line interface for GitHub PR Analyzer.

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

import sys
from typing import List, Optional, Tuple
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from .config import config
from .utils import check_gh_cli, check_git, format_datetime
from .pr_collector import PRCollector, PullRequest
from .commit_collector import CommitCollector
from .diff_viewer import DiffViewer
from .matcher import Matcher, MatchResult
from .ai_analyzer import AIAnalyzer
from .pr_exporter import PRJSONExporter

console = Console()


ASCII_LOGO = r"""
 ██████╗ ██╗████████╗██╗  ██╗██╗   ██╗██████╗         ██████╗ ██████╗          █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗███████╗██████╗ 
██╔════╝ ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗        ██╔══██╗██╔══██╗        ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝╚══███╔╝██╔════╝██╔══██╗
██║  ███╗██║   ██║   ███████║██║   ██║██████╔╝        ██████╔╝██████╔╝        ███████║██╔██╗ ██║███████║██║   ╚████╔╝   ███╔╝ █████╗  ██████╔╝
██║   ██║██║   ██║   ██╔══██║██║   ██║██╔══██╗        ██╔═══╝ ██╔══██╗        ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝   ███╔╝  ██╔══╝  ██╔══██╗
╚██████╔╝██║   ██║   ██║  ██║╚██████╔╝██████╔╝███████╗██║     ██║  ██║███████╗██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████╗███████╗██║  ██║
 ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝                                                                                                                                             
"""


def print_banner():
    """print application banner."""
    console.print(ASCII_LOGO, style="bold cyan")
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║                                                       ║
    ║        GitHub PR & Commit Analyzer v1.0.0            ║
    ║                                                       ║
    ║     Intelligent PR and Commit Analysis Tool          ║
    ║                                                       ║
    ╚═══════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def check_prerequisites() -> bool:
    """
    check if all prerequisites are installed.

    Returns:
        bool: True if all prerequisites are met
    """
    console.print("\n[cyan]Checking prerequisites...[/cyan]")

    errors = []

    if not check_git():
        errors.append("Git is not installed or not in PATH")
    else:
        console.print("[green]✓ Git found[/green]")

    if not check_gh_cli():
        errors.append("GitHub CLI (gh) is not installed or not authenticated")
        console.print("[red]✗ GitHub CLI not ready[/red]")
    else:
        console.print("[green]✓ GitHub CLI found and authenticated[/green]")

    is_valid, config_errors = config.validate()
    if not is_valid:
        console.print("[yellow]⚠ Configuration warnings:[/yellow]")
        for error in config_errors:
            console.print(f"  [yellow]- {error}[/yellow]")

    if errors:
        console.print("\n[red]Prerequisites not met:[/red]")
        for error in errors:
            console.print(f"  [red]✗ {error}[/red]")
        return False

    console.print("[green]✓ All prerequisites met[/green]\n")
    return True


def display_results_table(results: list[MatchResult]):
    """
    display search results in a table.

    Args:
        results: list of match results
    """
    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    table = Table(
        title=f"Search Results ({len(results)} matches)",
        show_header=True,
        header_style="bold cyan",
    )

    table.add_column("#", style="dim", width=4)
    table.add_column("Type", width=8)
    table.add_column("ID", width=10)
    table.add_column("Date/Time", width=16)
    table.add_column("Title/Message", style="green", no_wrap=False)
    table.add_column("Author", width=15)
    table.add_column("Score", justify="right", width=8)

    for idx, result in enumerate(results, 1):
        if result.item_type == "PR":
            item = result.item
            item_id = f"#{item.number}"
            title = item.title[:80]
            author = item.author
            # format PR date - use created_at
            date_time = format_datetime(getattr(item, "created_at", None))
        else:
            item = result.item
            item_id = item.short_sha
            title = item.message.split("\n")[0][:80]
            author = item.author
            # format commit date
            date_time = format_datetime(getattr(item, "committed_date", None))

        score_style = (
            "green" if result.score >= 70 else "yellow" if result.score >= 50 else "red"
        )

        table.add_row(
            str(idx),
            result.item_type,
            item_id,
            date_time,
            title,
            author,
            f"[{score_style}]{result.score}[/{score_style}]",
        )

    console.print(table)


def export_pr_datasets(
    repo_name: str, pr_pairs: List[Tuple[int, Optional[str]]], output_dir: Path
):
    """export PR data into JSON files."""
    if not pr_pairs:
        console.print("[yellow]No PR numbers provided for export[/yellow]")
        return

    filtered_pairs: List[Tuple[int, Optional[str]]] = []
    seen: set[int] = set()
    for number, title in pr_pairs:
        if number in seen:
            continue
        seen.add(number)
        filtered_pairs.append((number, title))

    try:
        exporter = PRJSONExporter(repo_name=repo_name, output_dir=output_dir)
    except Exception as exc:
        console.print(f"[red]Failed to initialize exporter: {str(exc)}[/red]")
        return

    exported_count = 0
    for number, title in filtered_pairs:
        try:
            exporter.export_pr(number, title_hint=title)
            exported_count += 1
        except Exception as exc:
            console.print(f"[red]Failed to export PR #{number}: {str(exc)}[/red]")

    if exported_count == 0:
        console.print("[yellow]No PR JSON files were created[/yellow]")
        return

    console.print(
        f"[green]✓ Exported {exported_count} PR file(s) to {str(output_dir)}[/green]"
    )


def resolve_json_export_flag(
    enable_flag: bool, disable_flag: bool, default: bool, command_name: str
) -> bool:
    """
    resolve the final json export behavior based on mutually exclusive flags.

    Args:
        enable_flag: whether --save-json was provided
        disable_flag: whether --no-save-json was provided
        default: default behavior when neither flag is set
        command_name: current command, used for clearer error text
    """
    if enable_flag and disable_flag:
        raise click.BadParameter(
            f"--save-json and --no-save-json cannot be combined in {command_name}",
            param_hint="--save-json/--no-save-json",
        )
    if enable_flag:
        return True
    if disable_flag:
        return False
    return default


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """GitHub PR and Commit Analyzer - Find and analyze relevant changes."""
    pass


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo",
    "-r",
    help="Repository in format owner/repo (auto-detect if not specified)",
)
@click.option(
    "--months",
    "-m",
    type=int,
    default=3,
    help="Number of months to look back for merged items",
)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export collected PRs into JSON files",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Disable PR JSON export",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gh_pr_exports"),
    show_default=True,
    help="Directory for exported PR JSON files",
)
def collect(
    repo: Optional[str],
    months: int,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
):
    """Collect all PRs and commits from the repository."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=False, command_name="collect"
    )

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        all_prs = pr_collector.collect_all_prs(months)

        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  • Open PRs: {len(all_prs['open'])}")
        console.print(
            f"  • Merged PRs (last {months} months): {len(all_prs['merged'])}"
        )

        commit_collector = CommitCollector(repo_name=pr_collector.repo)
        merge_commits = commit_collector.collect_merge_commits(months=months)

        console.print(f"  • Merge Commits (last {months} months): {len(merge_commits)}")
        console.print()

        if save_json:
            pr_pairs: List[Tuple[int, Optional[str]]] = []
            for pr in all_prs.get("open", []):
                pr_pairs.append((pr.number, pr.title))
            for pr in all_prs.get("merged", []):
                pr_pairs.append((pr.number, pr.title))
            export_pr_datasets(pr_collector.repo, pr_pairs, output_dir)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("query")
@click.option("--repo", "-r", help="Repository in format owner/repo")
@click.option("--months", "-m", type=int, default=3, help="Months to look back")
@click.option("--min-score", type=int, default=30, help="Minimum match score (0-100)")
@click.option("--max-results", type=int, default=20, help="Maximum number of results")
@click.option("--analyze", "-a", is_flag=True, help="Analyze results with AI")
@click.option("--show-diff", "-d", is_flag=True, help="Show diff for each result")
@click.option(
    "--smart-search/--no-smart-search",
    default=True,
    help="Use AI-powered smart search (default: enabled)",
)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export matched PRs into JSON files",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Disable PR JSON export",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gh_pr_exports"),
    show_default=True,
    help="Directory for exported PR JSON files",
)
@click.option(
    "-cn",
    "--chinese",
    "use_chinese",
    is_flag=True,
    default=False,
    help="Output AI analysis in Chinese",
)
def search(
    query: str,
    repo: Optional[str],
    months: int,
    min_score: int,
    max_results: int,
    analyze: bool,
    show_diff: bool,
    smart_search: bool,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
    use_chinese: bool,
):
    """Search for PRs and commits matching a query."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=False, command_name="search"
    )

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        all_prs = pr_collector.collect_all_prs(months)
        all_pr_list = all_prs["open"] + all_prs["merged"]

        commit_collector = CommitCollector(repo_name=pr_collector.repo)
        commits = commit_collector.collect_all_commits(months=months)

        console.print()

        matcher = Matcher(use_smart_search=smart_search)
        results = matcher.search(
            all_pr_list, commits, query, min_score=min_score, max_results=max_results
        )

        console.print()
        display_results_table(results)

        if not results:
            return

        if show_diff or analyze:
            diff_viewer = DiffViewer(repo_name=pr_collector.repo)

            if show_diff:
                console.print("\n[bold cyan]Displaying diffs...[/bold cyan]\n")
                for result in results[:5]:
                    if result.item_type == "PR":
                        diff_viewer.display_pr_diff(result.item.number, max_lines=100)
                    else:
                        diff_viewer.display_commit_diff(result.item.sha, max_lines=100)
                    console.print()

            if analyze:
                language = "cn" if use_chinese else "en"
                ai_analyzer = AIAnalyzer(language=language)
                if not ai_analyzer.is_available:
                    console.print(
                        "\n[yellow]AI analysis not available. Please set CURSOR_AGENT_PATH environment variable[/yellow]"
                    )
                    return

                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")

                # analyze and save each item immediately
                items_to_analyze = [r.item for r in results[:5]]
                analyzed = []
                exporter = None
                if save_json:
                    exporter = PRJSONExporter(
                        repo_name=pr_collector.repo, output_dir=output_dir
                    )

                for idx, item in enumerate(items_to_analyze, 1):
                    console.print(f"[cyan]Analyzing {idx}/{len(items_to_analyze)}...[/cyan]")
                    analysis = ai_analyzer.analyze(
                        item, include_diff=True, diff_viewer=diff_viewer
                    )
                    analyzed.append((item, analysis))

                    if analysis:
                        ai_analyzer.display_analysis(item, analysis)

                    # save JSON immediately after each analysis
                    if save_json and exporter:
                        if hasattr(item, "number"):
                            try:
                                file_path = exporter.export_pr(item.number, title_hint=item.title)
                                console.print(f"[green]✓ JSON saved: {file_path}[/green]\n")
                            except Exception as exc:
                                console.print(f"[red]Failed to export PR #{item.number}: {exc}[/red]\n")

                # save report automatically if save_json is enabled
                if save_json and analyzed:
                    report = ai_analyzer.generate_summary_report(analyzed, query)
                    report_file = (
                        f"pr_analysis_report_{pr_collector.repo.replace('/', '_')}.md"
                    )
                    Path(report_file).write_text(report)
                    console.print(f"[green]✓ Report saved to: {report_file}[/green]")

        elif save_json:
            # if not analyzing, still export JSON files
            pr_pairs: List[Tuple[int, Optional[str]]] = []
            for result in results:
                if result.item_type == "PR":
                    pr_pairs.append((result.item.number, result.item.title))
                else:
                    pr_number = getattr(result.item, "pr_number", None)
                    if pr_number:
                        pr_pairs.append((pr_number, None))
            if pr_pairs:
                export_pr_datasets(pr_collector.repo, pr_pairs, output_dir)
            else:
                console.print("[yellow]No PR entries available for export[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("pr_number", type=int)
@click.option("--repo", "-r", help="Repository in format owner/repo")
@click.option("--analyze", "-a", is_flag=True, help="Analyze with AI")
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export this PR into a JSON file (default: enabled)",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Skip exporting this PR to JSON",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gh_pr_exports"),
    show_default=True,
    help="Directory for exported PR JSON files",
)
@click.option(
    "-cn",
    "--chinese",
    "use_chinese",
    is_flag=True,
    default=False,
    help="Output AI analysis in Chinese",
)
def view_pr(
    pr_number: int,
    repo: Optional[str],
    analyze: bool,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
    use_chinese: bool,
):
    """View details of a specific PR."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=True, command_name="view-pr"
    )

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        pr = pr_collector.get_pr_details(pr_number)
        if not pr:
            console.print(f"[red]PR #{pr_number} not found[/red]")
            return

        info_text = f"""
[bold cyan]PR #{pr.number}[/bold cyan]: {pr.title}

[bold]Author:[/bold] {pr.author}
[bold]State:[/bold] {pr.state}
[bold]Created:[/bold] {format_datetime(pr.created_at, "full")}
[bold]Updated:[/bold] {format_datetime(pr.updated_at, "full")}
{f'[bold]Merged:[/bold] {format_datetime(pr.merged_at, "full")}' if pr.merged_at else ''}
[bold]URL:[/bold] {pr.url}

[bold]Statistics:[/bold]
  • Files Changed: {pr.changed_files}
  • Additions: {pr.additions}
  • Deletions: {pr.deletions}
  • Labels: {', '.join(pr.labels) if pr.labels else 'None'}

[bold]Description:[/bold]
{pr.body or 'No description provided.'}
        """

        console.print(Panel(info_text, border_style="cyan"))

        diff_viewer = DiffViewer(repo_name=pr_collector.repo)

        show_diff = Confirm.ask("\nShow diff?", default=True)
        if show_diff:
            diff_viewer.display_pr_diff(pr_number)

        if analyze:
            language = "cn" if use_chinese else "en"
            ai_analyzer = AIAnalyzer(language=language)
            if ai_analyzer.is_available:
                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")
                analysis = ai_analyzer.analyze(
                    pr, include_diff=True, diff_viewer=diff_viewer
                )
                if analysis:
                    ai_analyzer.display_analysis(pr, analysis)

        if save_json:
            export_pr_datasets(
                pr_collector.repo,
                [(pr.number, pr.title)],
                output_dir,
            )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("commit_sha")
@click.option("--analyze", "-a", is_flag=True, help="Analyze with AI")
def view_commit(commit_sha: str, analyze: bool):
    """View details of a specific commit."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        commit_collector = CommitCollector()

        commit = commit_collector.get_commit_details(commit_sha)
        if not commit:
            console.print(f"[red]Commit {commit_sha} not found[/red]")
            return

        info_text = f"""
[bold cyan]Commit {commit.short_sha}[/bold cyan]

[bold]Author:[/bold] {commit.author} <{commit.author_email}>
[bold]Authored:[/bold] {format_datetime(commit.authored_date, "full")}
[bold]Committed:[/bold] {format_datetime(commit.committed_date, "full")}
[bold]Is Merge:[/bold] {commit.is_merge}
{f'[bold]PR Number:[/bold] #{commit.pr_number}' if commit.pr_number else ''}
[bold]Full SHA:[/bold] {commit.sha}

[bold]Statistics:[/bold]
  • Files Changed: {commit.files_changed}
  • Insertions: {commit.insertions}
  • Deletions: {commit.deletions}

[bold]Message:[/bold]
{commit.message}
        """

        console.print(Panel(info_text, border_style="cyan"))

        diff_viewer = DiffViewer()

        show_diff = Confirm.ask("\nShow diff?", default=True)
        if show_diff:
            diff_viewer.display_commit_diff(commit.sha)

        if analyze:
            ai_analyzer = AIAnalyzer()
            if ai_analyzer.is_available:
                console.print("\n[bold cyan]Running AI analysis...[/bold cyan]\n")
                analysis = ai_analyzer.analyze(
                    commit, include_diff=True, diff_viewer=diff_viewer
                )
                if analysis:
                    ai_analyzer.display_analysis(commit, analysis)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
def interactive():
    """Interactive mode for exploring PRs and commits."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    try:
        repo = Prompt.ask(
            "\n[cyan]Repository (owner/repo, or press Enter to auto-detect)[/cyan]",
            default="",
        )
        months = int(Prompt.ask("[cyan]Months to look back[/cyan]", default="3"))

        pr_collector = PRCollector(repo if repo else None)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        console.print("[cyan]Collecting data...[/cyan]\n")
        all_prs = pr_collector.collect_all_prs(months)
        all_pr_list = all_prs["open"] + all_prs["merged"]

        commit_collector = CommitCollector(repo_name=pr_collector.repo)
        commits = commit_collector.collect_all_commits(months=months)

        diff_viewer = DiffViewer(repo_name=pr_collector.repo)
        matcher = Matcher(
            use_smart_search=True
        )  # enable smart search by default in interactive mode
        ai_analyzer = AIAnalyzer()

        console.print(f"\n[bold cyan]Data collected:[/bold cyan]")
        console.print(f"  • Total PRs: {len(all_pr_list)}")
        console.print(f"  • Total Commits: {len(commits)}")
        console.print()

        while True:
            console.print("\n[bold cyan]Options:[/bold cyan]")
            console.print("  1. Search by query")
            console.print("  2. View specific PR")
            console.print("  3. View specific commit")
            console.print("  4. Exit")

            choice = Prompt.ask(
                "\n[cyan]Choose an option[/cyan]", choices=["1", "2", "3", "4"]
            )

            if choice == "1":
                query = Prompt.ask("\n[cyan]Enter search query[/cyan]")

                results = matcher.search(
                    all_pr_list, commits, query, min_score=30, max_results=20
                )
                display_results_table(results)

                if results:
                    if Confirm.ask("\nAnalyze results with AI?"):
                        if ai_analyzer.is_available:
                            items = [r.item for r in results[:5]]
                            analyzed = ai_analyzer.batch_analyze(
                                items, include_diff=True, diff_viewer=diff_viewer
                            )

                            for item, analysis in analyzed:
                                if analysis:
                                    ai_analyzer.display_analysis(item, analysis)
                        else:
                            console.print("[yellow]AI analysis not available[/yellow]")

            elif choice == "2":
                pr_number = int(Prompt.ask("\n[cyan]Enter PR number[/cyan]"))
                pr = pr_collector.get_pr_details(pr_number)

                if pr:
                    console.print(f"\n{pr}")
                    if Confirm.ask("Show diff?"):
                        diff_viewer.display_pr_diff(pr_number)
                    if Confirm.ask("Analyze with AI?"):
                        if ai_analyzer.is_available:
                            analysis = ai_analyzer.analyze(
                                pr, include_diff=True, diff_viewer=diff_viewer
                            )
                            if analysis:
                                ai_analyzer.display_analysis(pr, analysis)

            elif choice == "3":
                sha = Prompt.ask("\n[cyan]Enter commit SHA[/cyan]")
                commit = commit_collector.get_commit_details(sha)

                if commit:
                    console.print(f"\n{commit}")
                    if Confirm.ask("Show diff?"):
                        diff_viewer.display_commit_diff(sha)
                    if Confirm.ask("Analyze with AI?"):
                        if ai_analyzer.is_available:
                            analysis = ai_analyzer.analyze(
                                commit, include_diff=True, diff_viewer=diff_viewer
                            )
                            if analysis:
                                ai_analyzer.display_analysis(commit, analysis)

            elif choice == "4":
                console.print("\n[cyan]Goodbye![/cyan]")
                break

    except KeyboardInterrupt:
        console.print("\n\n[cyan]Interrupted by user[/cyan]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--repo",
    "-r",
    help="Repository in format owner/repo (auto-detect if not specified)",
)
@click.option(
    "--days",
    "-d",
    type=int,
    default=60,
    help="Number of days to look back for PR traversal",
)
@click.option(
    "--save-json",
    "save_json_flag",
    is_flag=True,
    default=False,
    help="Export traversed PRs into JSON files",
)
@click.option(
    "--no-save-json",
    "no_save_json_flag",
    is_flag=True,
    default=False,
    help="Disable PR JSON export",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("gh_pr_exports"),
    show_default=True,
    help="Directory for exported PR JSON files",
)
@click.option(
    "-cn",
    "--chinese",
    "use_chinese",
    is_flag=True,
    default=False,
    help="Output AI analysis in Chinese",
)
def traverse(
    repo: Optional[str],
    days: int,
    save_json_flag: bool,
    no_save_json_flag: bool,
    output_dir: Path,
    use_chinese: bool,
):
    """Traverse recent PRs and analyze them with AI."""
    print_banner()

    if not check_prerequisites():
        sys.exit(1)

    if days <= 0:
        console.print("[red]Days must be a positive integer[/red]")
        sys.exit(1)

    language = "cn" if use_chinese else "en"
    ai_analyzer = AIAnalyzer(language=language)
    if not ai_analyzer.is_available:
        console.print(
            "[red]AI analysis not available. Please set CURSOR_AGENT_PATH environment variable[/red]"
        )
        sys.exit(1)

    save_json = resolve_json_export_flag(
        save_json_flag, no_save_json_flag, default=False, command_name="traverse"
    )

    try:
        pr_collector = PRCollector(repo)
        console.print(f"\n[bold]Repository:[/bold] {pr_collector.repo}\n")

        all_prs = pr_collector.collect_all_prs(days=days)
        open_prs = all_prs.get("open", [])
        merged_prs = all_prs.get("merged", [])

        console.print("[bold cyan]Traversal summary:[/bold cyan]")
        console.print(f"  • Open PRs (last {days} days): {len(open_prs)}")
        console.print(f"  • Merged PRs (last {days} days): {len(merged_prs)}")

        if not open_prs and not merged_prs:
            console.print("[yellow]No PRs found in the specified range[/yellow]")
            return

        diff_viewer = DiffViewer(repo_name=pr_collector.repo)

        analyzed_items: List[Tuple[PullRequest, Optional[str]]] = []

        # initialize exporter if save_json is enabled
        exporter = None
        if save_json:
            exporter = PRJSONExporter(
                repo_name=pr_collector.repo, output_dir=output_dir
            )

        def analyze_pr_group(prs: List[PullRequest], label: str) -> None:
            if not prs:
                console.print(f"[yellow]No {label.lower()} to analyze[/yellow]")
                return

            console.print(f"\n[bold cyan]Analyzing {label}...[/bold cyan]")

            total = len(prs)
            for index, pr in enumerate(prs, start=1):
                console.print(
                    f"\n[bold]Analyzing {label[:-1]} {index}/{total}: PR #{pr.number}[/bold]"
                )
                analysis = ai_analyzer.analyze(
                    pr,
                    include_diff=True,
                    diff_viewer=diff_viewer,
                )
                analyzed_items.append((pr, analysis))
                if analysis:
                    ai_analyzer.display_analysis(pr, analysis)

                # save JSON immediately after each analysis
                if save_json and exporter:
                    try:
                        file_path = exporter.export_pr(pr.number, title_hint=pr.title)
                        console.print(f"[green]✓ JSON saved: {file_path}[/green]\n")
                    except Exception as exc:
                        console.print(f"[red]Failed to export PR #{pr.number}: {exc}[/red]\n")

        analyze_pr_group(merged_prs, "Merged PRs")
        analyze_pr_group(open_prs, "Open PRs")

        # save report automatically if save_json is enabled
        if analyzed_items and save_json:
            report = ai_analyzer.generate_summary_report(
                analyzed_items,
                query=f"Traversal analysis for last {days} days",
            )
            report_file = (
                f"pr_traversal_report_{pr_collector.repo.replace('/', '_')}_{days}d.md"
            )
            Path(report_file).write_text(report)
            console.print(f"[green]✓ Report saved to: {report_file}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
