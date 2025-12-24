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
# Basic installation (uses Claude CLI)
pip install claude-code-orchestrator

# With Anthropic SDK for structured outputs (recommended)
pip install claude-code-orchestrator[sdk]

# With uv
uv add claude-code-orchestrator
uv add anthropic  # Optional: for structured outputs

# With pipx (for CLI usage)
pipx install claude-code-orchestrator
```

### Structured Outputs (Recommended)

For better task generation with guaranteed JSON schema compliance:

```bash
# Set your Anthropic API key
export ANTHROPIC_API_KEY=your-key-here

# Install with SDK support
pip install claude-code-orchestrator[sdk]
```

When `ANTHROPIC_API_KEY` is set, task generation uses Anthropic's structured outputs for more reliable parsing. Falls back to Claude CLI if not configured.

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

Configuration is loaded from two sources (later overrides earlier):
1. **Global config**: `~/.config/claude-orchestrator/config.yaml`
2. **Project config**: `.claude-orchestrator.yaml`

### Project Configuration

Create `.claude-orchestrator.yaml` in your project root:

```yaml
# Git settings (auto-detected if not specified)
git:
  provider: auto  # "bitbucket" / "github" / auto-detect
  base_branch: develop
  destination_branch: develop
  repo_slug: my-repo  # Required for Bitbucket

worktree_dir: ../worktrees

# MCPs to enable for agents
mcps:
  enabled:
    - atlassian    # For Jira ticket updates
    - linear       # For issue tracking

# Project context (auto-discovered if not specified)
project:
  key_files:
    - src/main.py
    - tests/
  test_command: pytest tests/
```

### Global Configuration

Set defaults that apply to all projects:

```bash
# Set global default base branch
claude-orchestrator config --global git.base_branch develop

# View global config
claude-orchestrator config --global --list
```

Global config is stored in `~/.config/claude-orchestrator/config.yaml`.

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

### `config`

Get or set configuration values (similar to `git config` or `gh config`):

```bash
# List all configuration (merged: global + project)
claude-orchestrator config --list

# Get a specific value
claude-orchestrator config git.base_branch

# Set a project-level value
claude-orchestrator config git.base_branch develop

# Set a global value (applies to all projects)
claude-orchestrator config --global git.base_branch develop
```

Available keys:
- `git.provider` - Git provider ("auto", "github", "bitbucket")
- `git.base_branch` - Base branch for PRs
- `git.destination_branch` - Target branch for PRs
- `git.repo_slug` - Repository slug (Bitbucket)
- `worktree_dir` - Directory for git worktrees
- `project.test_command` - Test command to run
- `mcps.enabled` - Comma-separated list of MCPs
- `workflow.mode` - Workflow mode ("review" or "yolo")
- `workflow.auto_approve` - Auto-approve agent actions (true/false)
- `workflow.auto_pr` - Create PRs automatically (true/false)
- `workflow.stop_after_generate` - Stop after generating tasks (true/false)
- `tools.permission_mode` - Permission mode (default, acceptEdits, plan, dontAsk, bypassPermissions)
- `tools.allowed_cli` - Comma-separated CLI tools to allow (gh, az, aws, docker, etc.)
- `tools.allowed_tools` - Comma-separated tool patterns (Bash(git:*), Edit, Read)
- `tools.disallowed_tools` - Comma-separated tool patterns to deny
- `tools.skip_permissions` - Skip all permissions (true/false, DANGEROUS)

### `run`

Execute tasks:

```bash
# Run all tasks (from existing task_config.yaml)
claude-orchestrator run

# Run specific tasks
claude-orchestrator run --tasks task1,task2

# Generate from todo, stop for review (default)
claude-orchestrator run --from-todo todo.md

# Generate and execute without stopping
claude-orchestrator run --from-todo todo.md --execute

# YOLO: Generate, execute, and create PRs without stopping
claude-orchestrator run --from-todo todo.md --yolo

# Auto-approve all agent actions
claude-orchestrator run --auto-approve
```

### `yolo`

Shortcut for full YOLO mode:

```bash
# Generate tasks, execute, and create PRs in one go
claude-orchestrator yolo TODO.md

# Equivalent to:
claude-orchestrator run --from-todo TODO.md --yolo
```

## Workflow Modes

Configure how much the orchestrator stops for review:

| Mode | Description |
|------|-------------|
| `review` (default) | Stop after generating tasks for review |
| `yolo` | Run everything without stopping |

### Configure via CLI

```bash
# Set workflow mode globally
claude-orchestrator config --global workflow.mode yolo

# Or per-project
claude-orchestrator config workflow.mode yolo

# Enable auto-approve (agents won't ask for confirmation)
claude-orchestrator config workflow.auto_approve true

# Disable automatic PR creation
claude-orchestrator config workflow.auto_pr false
```

### Configure in `.claude-orchestrator.yaml`

```yaml
workflow:
  mode: yolo           # "review" or "yolo"
  auto_approve: true   # Automatically approve agent actions
  auto_pr: true        # Create PRs automatically
  stop_after_generate: false  # Fine-grained: stop after task generation
```

## Tools & Permissions

Configure which CLI tools agents can use and their permission levels:

### Allow CLI Tools

```bash
# Allow specific CLI tools (gh, aws, az, docker, etc.)
claude-orchestrator config tools.allowed_cli "gh,az,aws,docker"

# View current settings
claude-orchestrator config tools.allowed_cli
```

These get converted to `--allowedTools Bash(gh:*) Bash(az:*) ...` when running agents.

### Permission Modes

```bash
# Set permission mode for agents
claude-orchestrator config tools.permission_mode acceptEdits
```

Available modes:
| Mode | Description |
|------|-------------|
| `default` | Normal permissions with prompts |
| `acceptEdits` | Auto-accept file edits |
| `plan` | Show plan before executing |
| `dontAsk` | Don't ask for confirmations |
| `bypassPermissions` | Skip all permission checks |

### Advanced Tool Configuration

```bash
# Allow specific tools patterns
claude-orchestrator config tools.allowed_tools "Bash(git:*),Edit,Read"

# Disallow dangerous tools
claude-orchestrator config tools.disallowed_tools "Bash(rm:*),Bash(sudo:*)"

# Skip all permissions (only for sandboxed environments!)
claude-orchestrator config tools.skip_permissions true

# Add extra directories for tool access
claude-orchestrator config tools.add_dirs "/path/to/shared/config"
```

### Configuration in `.claude-orchestrator.yaml`

```yaml
tools:
  permission_mode: acceptEdits
  allowed_cli:
    - gh
    - az
    - aws
    - docker
  allowed_tools:
    - "Bash(git:*)"
    - Edit
    - Read
  disallowed_tools:
    - "Bash(rm:-rf:*)"
  add_dirs:
    - ../shared-config
  skip_permissions: false  # Only for sandboxed environments!
```

### Project-specific vs CLAUDE.md

You have two options for tool configuration:

1. **`.claude-orchestrator.yaml`** (recommended for orchestrator tasks)
   - Centralized configuration
   - Applies to all agents launched by the orchestrator
   - Version controlled with your project

2. **`CLAUDE.md`** in your project
   - Applies to all Claude Code sessions in that project
   - Good for general project instructions
   - Not specific to orchestrator tasks

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

