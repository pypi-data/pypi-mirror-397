# GitHub PR & Commit Analyzer

[中文文档](README.cn.md) | English

A powerful command-line tool for intelligently collecting, analyzing, and summarizing GitHub Pull Requests and commit records.

[![PyPI version](https://badge.fury.io/py/github-pr-analyzer.svg)](https://badge.fury.io/py/github-pr-analyzer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.8+**
- **Git**
- **GitHub CLI (gh)**: Must be logged in (`gh auth login`)

### 2. Install
```bash
pip install github-pr-analyzer
```

### 3. Configuration (Environment Variables)

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CURSOR_AGENT_PATH` | Path to cursor-agent for AI features | None | **Yes** (for AI) |
| `DEFAULT_MONTHS` | Months to look back for data | `3` | No |
| `DEFAULT_REPO_PATH` | Default repository path | `.` | No |

```bash
# Example
export CURSOR_AGENT_PATH=/path/to/cursor-agent
export DEFAULT_MONTHS=6
```

## 📖 Quick Start

```bash
# 1. Interactive Mode (Best for starting)
ghpa interactive

# 2. Search with AI Analysis (English output)
ghpa search "authentication bug" --analyze

# 3. Search with AI Analysis (Chinese output)
ghpa search "authentication bug" --analyze -cn

# 4. Collect Data
ghpa collect --save-json

# 5. Generate Daily/Weekly Report + Export Datasets
ghpa traverse --days 7 --save-json
ghpa traverse -r pytorch/pytorch --days 7 --save-json -cn
```

All CLI workflows expose matching `--save-json` / `--no-save-json` toggles so you can enable exports when needed and opt out (for example, disable the default `view-pr` export with `--no-save-json`).

### Language Options

Use `-cn` or `--chinese` flag to get AI analysis output in Chinese:

```bash
# Chinese output
ghpa search "quantization" -a -cn
ghpa view-pr 588 -a -cn
ghpa traverse --days 7 -cn
```

## ✨ Features
- 🔍 **Smart Search**: AI-powered keyword extraction
- 📊 **Data Collection**: PRs and merge commits statistics
- 🔄 **Diff Viewing**: Syntax-highlighted code changes
- 🤖 **AI Analysis**: Summarization via cursor-agent with English/Chinese output
- 📅 **Traverse Mode**: Batch analysis for reporting
- 🗂 **JSON Export**: Persist PR, commit, and review conversations as structured JSON
- 🌐 **Multi-language**: Support for English and Chinese AI analysis output
- 💾 **Instant Save**: JSON files saved immediately after each PR analysis
- 🎨 **Enhanced Display**: Beautiful terminal output with colors and formatting

For detailed command usage, see [USAGE.md](USAGE.md).

## 🗂 JSON Export Format

All major workflows (`collect`, `search`, `traverse`, `view-pr`) share the same `--save-json` / `--no-save-json` flags (with `view-pr` defaulting to export unless `--no-save-json` is specified). Files land in `gh_pr_exports/` unless `--output-dir` is provided.

### File Naming Convention

Files follow the pattern:
```
{repo}_{merged_pr|open_pr}_{pr_number}_{title}_{timestamp}.json
```

Examples:
- `NVIDIA_TensorRT_merged_pr_588_Support_AutoQuantize_20251125_1423.json`
- `pytorch_pytorch_open_pr_123_Add_feature_20251126_0930.json`

The timestamp uses the merge time for merged PRs, or the last update time for open PRs.

### JSON Structure

Each JSON document contains:

- `repo`: the `owner/repo` slug used for collection
- `pr`: metadata including:
  - `number`, `title`, `url`, `state`
  - `author`, `author_name`, `author_email`
  - `created_at`, `updated_at`, `merged_at`
  - `base_ref`, `head_ref`
  - `body`: PR description as line array (for readability)
- `commits`: ordered list of commits with:
  - `id`: full commit SHA
  - `title`: first line of the commit message
  - `message`: full commit body
  - `committer_name`, `committer_email`
  - `files`: array of `{ "path": "<file>", "diff": ["line1", "line2", ...] }`
- `conversation`: threaded review data
  - `issue_comments`: top-level PR discussion
  - `review_threads`: code review threads (note: limited availability via GitHub API)
  - `reviews`: review summaries (approve/comment/request changes)

> Example snippet:
```json
{
  "repo": "octo-org/octo-repo",
  "pr": {
    "number": 42,
    "title": "Fix login",
    "author": "octocat",
    "author_name": "The Octocat",
    "author_email": "octocat@github.com",
    "state": "MERGED",
    "body": [
      "## Summary",
      "This PR fixes the login flow.",
      "",
      "## Changes",
      "- Fixed authentication"
    ]
  },
  "commits": [
    {
      "id": "abc123...",
      "title": "Adjust auth flow",
      "message": "Adjust auth flow\n\n- add checks...\n",
      "committer_name": "The Octocat",
      "committer_email": "octocat@github.com",
      "files": [
        {
          "path": "auth/login.py",
          "diff": [
            "@@ -1,3 +1,4 @@",
            " import os",
            "-old_line",
            "+new_line"
          ]
        }
      ]
    }
  ],
  "conversation": {
    "issue_comments": [],
    "review_threads": [],
    "reviews": []
  }
}
```

Use these exports to feed downstream tooling, audits, or offline review workflows.

## 🎨 AI Analysis Display

The AI analysis output features:
- **Metadata Panel**: Shows author, email, state, URL with color-coded status
- **Analysis Panel**: Dark background with white text for readability
- **Left-aligned Content**: All text left-aligned for better reading experience
- **Adaptive Width**: Automatically adjusts to terminal window size

State indicators:
- ✅ **MERGED** (magenta)
- 🔄 **OPEN** (green)
- ❌ **CLOSED** (red)
