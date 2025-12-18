## GitLab MR & Commit Analyzer

[中文文档](README.cn.md) | English

A command-line tool for intelligently collecting, analyzing, and summarizing GitLab Merge Requests and commit records.

## Installation & Setup

### Prerequisites
- **Python 3.8+**
- **Git**
- **GitLab access**
  - `GITLAB_HOST` (e.g. `https://gitlab.example.com`)
  - `GITLAB_TOKEN` (PAT with `read_api` or `api` scope)

### Install

```bash
pip install gitlab-pr-analyzer
```

### Configuration (Environment Variables)

| Variable | Description | Required |
|----------|-------------|----------|
| `GITLAB_HOST` | GitLab instance base URL | **Yes** |
| `GITLAB_TOKEN` | Personal Access Token | **Yes** |
| `GITLAB_INSTANCE_NAME` | Banner display name | No |
| `CURSOR_AGENT_PATH` | Path to cursor-agent for AI features | No (Yes for AI) |

## Quick Start

```bash
# 1. Interactive Mode (best for starting)
glpa interactive

# 2. Search with AI analysis (English output)
glpa search "authentication bug" --analyze

# 3. Search with AI analysis (Chinese output)
glpa search "authentication bug" --analyze -cn

# 4. Collect data
glpa collect --save-json

# 5. Generate report + export datasets
glpa traverse --days 7 --save-json -cn
```

For detailed command usage, see [USAGE.md](USAGE.md).

