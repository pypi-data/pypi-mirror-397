# claude-code-orchestrator

Orchestrator for running parallel Claude Code agents on multiple tasks. Each task runs in its own git worktree with a dedicated agent instance.

## Features

- **Parallel Task Execution**: Run multiple Claude Code agents simultaneously on different tasks
- **Git Worktree Isolation**: Each task runs in its own worktree to prevent conflicts
- **Auto-detect Git Provider**: Automatically detects Bitbucket or GitHub from remote URL
- **MCP Integration**: Uses Bitbucket MCP for Bitbucket repos, `gh` CLI for GitHub
- **Extensible MCP Registry**: Configure additional MCPs (Atlassian, Linear, Postgres, Chrome, etc.)
- **Project Discovery**: Automatically analyzes project structure and conventions
- **Task Generation**: Generate task configurations from todo.md files

## Installation

```bash
# With pip
pip install claude-code-orchestrator

# With uv
uv add claude-code-orchestrator

# With pipx (for CLI usage)
pipx install claude-code-orchestrator
```

## Prerequisites

### For GitHub Repositories

```bash
# Install GitHub CLI
brew install gh  # macOS
# or: sudo apt install gh  # Ubuntu

# Authenticate
gh auth login
```

### For Bitbucket Repositories

```bash
# Install Bitbucket MCP
pipx install mcp-server-bitbucket

# Configure MCP
claude mcp add bitbucket -s user \
  -e BITBUCKET_WORKSPACE=your-workspace \
  -e BITBUCKET_EMAIL=your-email \
  -e BITBUCKET_API_TOKEN=your-token \
  -- mcp-server-bitbucket
```

## Quick Start

```bash
# Check prerequisites
claude-orchestrator doctor

# Initialize project configuration
claude-orchestrator init

# Generate tasks from a todo file
claude-orchestrator generate --from-todo todo.md

# Run all tasks
claude-orchestrator run

# Or combine generation and execution
claude-orchestrator run --from-todo todo.md --execute
```

## Configuration

Create `.claude-orchestrator.yaml` in your project root:

```yaml
# Git settings (auto-detected if not specified)
git:
  provider: auto  # "bitbucket" / "github" / auto-detect
  base_branch: main
  destination_branch: main
  repo_slug: my-repo  # Required for Bitbucket

worktree_dir: ../worktrees

# MCPs to enable for agents
mcps:
  enabled:
    - atlassian    # For Jira ticket updates
    - linear       # For issue tracking
    - postgres     # For database access
    - chrome       # For browser automation

# Project context (auto-discovered if not specified)
project:
  key_files:
    - src/main.py
    - tests/
  test_command: pytest tests/
```

## CLI Commands

### `doctor`

Check all prerequisites and configuration:

```bash
claude-orchestrator doctor
```

Output:
```
✓ Git provider: GitHub (github.com detected)
✓ gh CLI: installed and authenticated
✓ MCP atlassian: configured
✗ MCP linear: not configured
  Run: pipx install mcp-server-linear && claude mcp add linear...
```

### `init`

Initialize project configuration:

```bash
claude-orchestrator init
```

This will:
1. Detect git provider
2. Analyze project structure
3. Create `.claude-orchestrator.yaml`

### `generate`

Generate task configuration from a todo file:

```bash
claude-orchestrator generate --from-todo todo.md
```

### `run`

Execute tasks:

```bash
# Run all tasks
claude-orchestrator run

# Run specific tasks
claude-orchestrator run --tasks task1,task2

# Auto-approve all agent actions
claude-orchestrator run --auto-approve

# Full pipeline
claude-orchestrator run --from-todo todo.md --execute
```

## Optional MCPs

| MCP | Auth Type | Use Case |
|-----|-----------|----------|
| `atlassian` | OAuth | Jira/Confluence integration |
| `linear` | OAuth | Issue tracking |
| `postgres` | Env vars | Database access |
| `chrome` | Pre-configured | Browser automation |

### Setting up OAuth MCPs

```bash
# Install the MCP
pipx install mcp-server-atlassian

# Add to Claude (first run will open browser for OAuth)
claude mcp add atlassian -s user -- mcp-server-atlassian
```

## License

MIT

