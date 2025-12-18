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

### Recommended (optional)
- **GitLab CLI (glab)**: recommended for better and faster diff retrieval
  - install and authenticate: `glab auth login`

### Install GitLab CLI (glab)

- **macOS (Homebrew)**:

```bash
brew install glab
glab auth login
```

- **Linux (APT, Ubuntu/Debian)**:

```bash
sudo apt update
sudo apt install -y glab
glab auth login
```

- **Windows (Winget)**:

```powershell
winget install --id GitLab.glab
glab auth login
```

> Daily usage tip: use the short command `glpa` (legacy: `gl-pr-analyzer`, `gl-pr-ai`).

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
# 0. Check connectivity (recommended after setting env vars)
glpa check

# 1. Interactive Mode (best for starting)
glpa interactive

# 2. Search with AI analysis (English output)
glpa search "authentication bug" --ai

# 3. Search with AI analysis (Chinese output)
glpa search "authentication bug" --ai -cn

# 4. Collect data
glpa collect --save-json

# 5. Generate report + export datasets
glpa traverse --days 7 --save-json

# optional: enable AI analysis for traverse
glpa traverse --days 7 --save-json --ai -cn
```

For detailed command usage, see [USAGE.md](USAGE.md).

