"""CLI for claude-orchestrator.

Provides commands for initializing projects, generating tasks, and running agents.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from claude_orchestrator import __version__
from claude_orchestrator.config import (
    Config,
    GitConfig,
    WorkflowConfig,
    config_exists,
    load_config,
    save_config,
    load_global_config,
    save_global_config,
    GLOBAL_CONFIG_FILE,
)
from claude_orchestrator.discovery import discover_sync
from claude_orchestrator.git_provider import (
    GitProvider,
    get_provider_status,
    get_default_branch,
    get_current_branch,
)
from claude_orchestrator.mcp_registry import AuthType, get_all_mcp_statuses, get_mcp_status
from claude_orchestrator.orchestrator import run_tasks_sync
from claude_orchestrator.task_generator import (
    generate_tasks_sync,
    load_tasks_config,
    save_tasks_config,
)


app = typer.Typer(
    name="claude-orchestrator",
    help="Orchestrator for running parallel Claude Code agents on multiple tasks.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"claude-orchestrator version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Claude Orchestrator - Run parallel Claude Code agents on multiple tasks."""
    pass


@app.command()
def doctor(
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory to check.",
    ),
    mcps: Optional[str] = typer.Option(
        None,
        "--mcps",
        "-m",
        help="Comma-separated list of MCPs to check (default: from config or common ones).",
    ),
):
    """Check prerequisites and configuration status.

    Verifies git provider, CLI tools, and MCP configurations.
    """
    console.print("\n[bold]Claude Orchestrator Doctor[/bold]\n")

    # Check git provider
    console.print("[bold]Git Provider[/bold]")
    provider_status = get_provider_status(str(project_dir))

    if provider_status.provider == GitProvider.GITHUB:
        provider_name = "GitHub"
        tool_name = "gh CLI"
    elif provider_status.provider == GitProvider.BITBUCKET:
        provider_name = "Bitbucket"
        tool_name = "mcp-server-bitbucket"
    else:
        provider_name = "Unknown"
        tool_name = "N/A"

    if provider_status.is_ready:
        console.print(f"  [green]✓[/green] Provider: {provider_name}")
        console.print(f"  [green]✓[/green] Tool: {tool_name} (ready)")
    else:
        console.print(f"  [yellow]![/yellow] Provider: {provider_name}")
        if provider_status.error:
            console.print(f"  [red]✗[/red] {provider_status.error}")

    # Check config
    console.print("\n[bold]Configuration[/bold]")
    if config_exists(project_dir):
        console.print("  [green]✓[/green] .claude-orchestrator.yaml exists")
        config = load_config(project_dir)
    else:
        console.print("  [yellow]○[/yellow] .claude-orchestrator.yaml not found (will use defaults)")
        config = Config()

    # Check MCPs
    console.print("\n[bold]MCPs[/bold]")

    # Determine which MCPs to check
    mcp_list = []
    if mcps:
        mcp_list = [m.strip() for m in mcps.split(",")]
    elif config.mcps.enabled:
        mcp_list = config.mcps.enabled
    # Only check git provider MCP if needed (Bitbucket needs MCP, GitHub uses gh CLI)
    # Don't show all MCPs by default - only what's configured or explicitly requested

    # Check git provider MCP status (only for Bitbucket)
    if provider_status.provider == GitProvider.BITBUCKET:
        status = get_mcp_status("bitbucket")
        if status.is_ready:
            console.print(f"  [green]✓[/green] bitbucket: ready")
        elif status.is_configured:
            console.print(f"  [green]✓[/green] bitbucket: configured")
        else:
            console.print(f"  [red]✗[/red] bitbucket: not configured")
            if status.setup_instructions:
                console.print(f"      Setup:\n{status.setup_instructions}")
    elif provider_status.provider == GitProvider.GITHUB:
        console.print(f"  [dim]○[/dim] Using gh CLI for GitHub (no MCP needed)")

    # Get status of explicitly enabled MCPs from config
    for mcp_name in mcp_list:
        if mcp_name == "bitbucket":
            continue  # Already handled above
        
        status = get_mcp_status(mcp_name)

        if status.is_ready:
            console.print(f"  [green]✓[/green] {mcp_name}: ready")
        elif status.is_configured:
            if status.auth_type == AuthType.OAUTH_BROWSER:
                console.print(f"  [yellow]○[/yellow] {mcp_name}: configured (may need browser auth)")
            else:
                console.print(f"  [yellow]![/yellow] {mcp_name}: {status.message}")
        else:
            console.print(f"  [red]✗[/red] {mcp_name}: not configured")
            if status.setup_instructions:
                console.print(f"      Setup:\n{status.setup_instructions}")
    
    if not mcp_list and provider_status.provider != GitProvider.BITBUCKET:
        console.print("  [dim]○[/dim] No additional MCPs configured")

    console.print()


@app.command()
def init(
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory to initialize.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration.",
    ),
    use_claude: bool = typer.Option(
        True,
        "--use-claude/--no-claude",
        help="Use Claude for project discovery.",
    ),
):
    """Initialize project configuration.

    Discovers project structure and creates .claude-orchestrator.yaml.
    """
    if config_exists(project_dir) and not force:
        console.print("[yellow]Configuration already exists. Use --force to overwrite.[/yellow]")
        raise typer.Exit(1)

    console.print("[bold]Initializing Claude Orchestrator[/bold]\n")

    # Detect git provider
    console.print("Detecting git provider...")
    provider_status = get_provider_status(str(project_dir))

    provider_name = {
        GitProvider.GITHUB: "github",
        GitProvider.BITBUCKET: "bitbucket",
    }.get(provider_status.provider, "auto")

    console.print(f"  Provider: {provider_name}")

    # Detect default branch
    console.print("Detecting default branch...")
    default_branch = get_default_branch(str(project_dir)) or "main"
    console.print(f"  Default branch: {default_branch}")

    # Discover project
    console.print("\nAnalyzing project structure...")
    context = discover_sync(project_dir, use_claude=use_claude)

    console.print(f"  Project: {context.project_name}")
    console.print(f"  Tech stack: {', '.join(context.tech_stack)}")
    console.print(f"  Test command: {context.test_command or 'Not detected'}")
    console.print(f"  Key files: {len(context.key_files)} found")

    # Create config
    config = Config(
        project_root=project_dir,
        git=GitConfig(
            provider=provider_name,
            base_branch=default_branch,
            destination_branch=default_branch,
            repo_slug=provider_status.repo_info.get("repo") if provider_status.repo_info else None,
        ),
    )

    # Add project context
    config.project.key_files = context.key_files[:10]
    config.project.test_command = context.test_command

    # Check for agent instructions
    if (project_dir / ".claude" / "AGENT_INSTRUCTIONS.md").exists():
        config.project.agent_instructions = ".claude/AGENT_INSTRUCTIONS.md"

    # Save config
    save_config(config, project_dir)
    console.print(f"\n[green]✓[/green] Created .claude-orchestrator.yaml")

    # Show next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Review and customize .claude-orchestrator.yaml")
    console.print("  2. Create a todo.md with tasks")
    console.print("  3. Run: claude-orchestrator generate --from-todo todo.md")
    console.print("  4. Run: claude-orchestrator run")


@app.command()
def generate(
    from_todo: Path = typer.Option(
        ...,
        "--from-todo",
        "-t",
        help="Path to todo.md file.",
    ),
    output: Path = typer.Option(
        Path("task_config.yaml"),
        "--output",
        "-o",
        help="Output path for task configuration.",
    ),
    use_sdk: bool = typer.Option(
        True,
        "--use-sdk/--no-sdk",
        help="Use Anthropic SDK with structured outputs (requires ANTHROPIC_API_KEY).",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory.",
    ),
):
    """Generate task configuration from a todo file.

    Uses Claude to analyze the todo file and generate task_config.yaml.
    
    By default, uses Anthropic SDK with structured outputs if ANTHROPIC_API_KEY
    is set. Falls back to Claude CLI otherwise.
    """
    import os
    
    if not from_todo.exists():
        console.print(f"[red]Error: Todo file not found: {from_todo}[/red]")
        raise typer.Exit(1)

    console.print("[bold]Generating task configuration[/bold]\n")
    console.print(f"  Input: {from_todo}")
    console.print(f"  Output: {output}")

    # Check SDK availability
    if use_sdk and os.getenv("ANTHROPIC_API_KEY"):
        console.print("  [dim]Method: Anthropic SDK (structured outputs)[/dim]")
    else:
        console.print("  [dim]Method: Claude CLI[/dim]")

    # Load config
    config = load_config(project_dir)

    # Discover project
    console.print("\nAnalyzing project...")
    context = discover_sync(project_dir, use_claude=False)

    # Generate tasks
    console.print("Generating tasks with Claude...")
    tasks_config = generate_tasks_sync(from_todo, context, config, use_sdk=use_sdk)

    if not tasks_config or not tasks_config.tasks:
        console.print("[red]Error: Failed to generate tasks[/red]")
        raise typer.Exit(1)

    # Save tasks
    save_tasks_config(tasks_config, output)

    console.print(f"\n[green]✓[/green] Generated {len(tasks_config.tasks)} task(s):")
    for task in tasks_config.tasks:
        console.print(f"  - {task.id}: {task.title}")

    console.print(f"\n[bold]Next step:[/bold] claude-orchestrator run --config {output}")


@app.command()
def run(
    config_file: Path = typer.Option(
        Path("task_config.yaml"),
        "--config",
        "-c",
        help="Path to task configuration file.",
    ),
    from_todo: Optional[Path] = typer.Option(
        None,
        "--from-todo",
        "-t",
        help="Generate tasks from todo file before running.",
    ),
    execute: bool = typer.Option(
        False,
        "--execute",
        "-e",
        help="Execute tasks after generating (requires --from-todo).",
    ),
    yolo: bool = typer.Option(
        False,
        "--yolo",
        help="YOLO mode: generate, execute, and create PRs without stopping.",
    ),
    tasks: Optional[str] = typer.Option(
        None,
        "--tasks",
        help="Comma-separated task IDs to run (default: all).",
    ),
    auto_approve: bool = typer.Option(
        False,
        "--auto-approve",
        "-y",
        help="Automatically approve all agent plans.",
    ),
    keep_worktrees: bool = typer.Option(
        False,
        "--keep-worktrees",
        help="Don't cleanup worktrees after completion.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be done without executing.",
    ),
    no_pr: bool = typer.Option(
        False,
        "--no-pr",
        help="Skip PR creation instructions in prompts.",
    ),
    sequential: bool = typer.Option(
        False,
        "--sequential",
        "-s",
        help="Run tasks sequentially instead of in parallel.",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory.",
    ),
):
    """Run tasks using Claude Code agents.

    Each task runs in its own git worktree with a dedicated agent.
    
    Workflow modes:
      - Default: Generate tasks, stop for review
      - --execute: Generate and execute, stop before PRs
      - --yolo: Generate, execute, and create PRs without stopping
    """
    # Load project config early for workflow settings
    config = load_config(project_dir)
    
    # YOLO mode overrides everything
    if yolo:
        execute = True
        auto_approve = config.workflow.auto_approve or auto_approve
        if not no_pr:
            no_pr = not config.workflow.auto_pr
    else:
        # Apply workflow config defaults
        auto_approve = auto_approve or config.workflow.auto_approve
        if config.workflow.mode == "yolo":
            execute = True
            if not no_pr:
                no_pr = not config.workflow.auto_pr

    # Handle --from-todo
    if from_todo:
        if not from_todo.exists():
            console.print(f"[red]Error: Todo file not found: {from_todo}[/red]")
            raise typer.Exit(1)

        console.print("[bold]Generating tasks from todo...[/bold]\n")

        # Discover project
        context = discover_sync(project_dir, use_claude=False)

        # Generate tasks
        tasks_config = generate_tasks_sync(from_todo, context, config)

        if not tasks_config or not tasks_config.tasks:
            console.print("[red]Error: Failed to generate tasks[/red]")
            raise typer.Exit(1)

        # Save tasks
        save_tasks_config(tasks_config, config_file)

        console.print(f"[green]✓[/green] Generated {len(tasks_config.tasks)} task(s)")

        # Check if we should stop after generate (unless yolo or execute)
        should_stop = config.workflow.stop_after_generate and not execute and not yolo
        if should_stop:
            console.print(f"\n[dim]Review {config_file} and run: claude-orchestrator run[/dim]")
            console.print("[dim]Or use --execute or --yolo to continue automatically[/dim]")
            raise typer.Exit()

        console.print("\n" + "=" * 60)
        console.print("Proceeding to execute tasks...")
        console.print("=" * 60)

    # Load task config
    tasks_config = load_tasks_config(config_file)

    if not tasks_config:
        console.print(f"[red]Error: Could not load task config: {config_file}[/red]")
        raise typer.Exit(1)

    if not tasks_config.tasks:
        console.print("[yellow]No tasks to run[/yellow]")
        raise typer.Exit()

    # Parse task IDs
    task_ids = [t.strip() for t in tasks.split(",")] if tasks else None

    # Run tasks
    console.print(f"\n[bold]Running {len(tasks_config.tasks)} task(s)[/bold]\n")

    results = run_tasks_sync(
        tasks_config=tasks_config,
        config=config,
        task_ids=task_ids,
        auto_approve=auto_approve,
        keep_worktrees=keep_worktrees,
        dry_run=dry_run,
        no_pr=no_pr,
        sequential=sequential,
    )

    # Exit with appropriate code
    failed = sum(1 for r in results if r.status == "failed")
    raise typer.Exit(1 if failed > 0 else 0)


@app.command()
def yolo(
    from_todo: Path = typer.Argument(
        ...,
        help="Path to todo.md file.",
    ),
    config_file: Path = typer.Option(
        Path("task_config.yaml"),
        "--config",
        "-c",
        help="Path to task configuration file.",
    ),
    tasks: Optional[str] = typer.Option(
        None,
        "--tasks",
        help="Comma-separated task IDs to run (default: all).",
    ),
    sequential: bool = typer.Option(
        False,
        "--sequential",
        "-s",
        help="Run tasks sequentially instead of in parallel.",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory.",
    ),
):
    """YOLO mode: Generate tasks, execute, and create PRs without stopping.

    This is a shortcut for:
        claude-orchestrator run --from-todo TODO.md --yolo

    Example:
        claude-orchestrator yolo TODO.md
    """
    # Load config
    config = load_config(project_dir)

    if not from_todo.exists():
        console.print(f"[red]Error: Todo file not found: {from_todo}[/red]")
        raise typer.Exit(1)

    console.print("[bold yellow]🚀 YOLO MODE[/bold yellow]")
    console.print("[dim]Generating → Executing → Creating PRs (no stops)[/dim]\n")

    # Generate tasks
    console.print("[bold]Step 1: Generating tasks...[/bold]")
    context = discover_sync(project_dir, use_claude=False)
    tasks_config = generate_tasks_sync(from_todo, context, config)

    if not tasks_config or not tasks_config.tasks:
        console.print("[red]Error: Failed to generate tasks[/red]")
        raise typer.Exit(1)

    save_tasks_config(tasks_config, config_file)
    console.print(f"[green]✓[/green] Generated {len(tasks_config.tasks)} task(s)\n")

    # Execute tasks
    console.print("[bold]Step 2: Executing tasks...[/bold]")
    task_ids = [t.strip() for t in tasks.split(",")] if tasks else None

    results = run_tasks_sync(
        tasks_config=tasks_config,
        config=config,
        task_ids=task_ids,
        auto_approve=config.workflow.auto_approve,
        keep_worktrees=False,
        dry_run=False,
        no_pr=not config.workflow.auto_pr,
        sequential=sequential,
    )

    # Summary
    console.print("\n[bold]Summary[/bold]")
    succeeded = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "failed")
    console.print(f"  [green]✓[/green] Succeeded: {succeeded}")
    if failed > 0:
        console.print(f"  [red]✗[/red] Failed: {failed}")

    raise typer.Exit(1 if failed > 0 else 0)


@app.command()
def config(
    key: str = typer.Argument(
        None,
        help="Configuration key (e.g., git.base_branch, git.repo_slug)",
    ),
    value: str = typer.Argument(
        None,
        help="Value to set",
    ),
    list_all: bool = typer.Option(
        False,
        "--list",
        "-l",
        help="List all configuration values.",
    ),
    is_global: bool = typer.Option(
        False,
        "--global",
        "-g",
        help="Use global configuration (~/.config/claude-orchestrator/config.yaml).",
    ),
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory.",
    ),
):
    """Get or set configuration values.

    Similar to 'git config' or 'gh config'.

    Configuration priority (higher overrides lower):
      1. Project config (.claude-orchestrator.yaml)
      2. Global config (~/.config/claude-orchestrator/config.yaml)
      3. Default values

    Examples:
        claude-orchestrator config --list
        claude-orchestrator config git.base_branch
        claude-orchestrator config git.base_branch develop
        claude-orchestrator config --global git.base_branch develop
    """
    if is_global:
        # Handle global config
        global_data = load_global_config()

        if list_all:
            console.print(f"\n[bold]Global Configuration[/bold] ({GLOBAL_CONFIG_FILE})\n")
            if not global_data:
                console.print("  [dim](no global config set)[/dim]")
            else:
                _print_nested_config(global_data, "  ")
            console.print()
            return

        if key is None:
            console.print("Usage: claude-orchestrator config --global [KEY] [VALUE]")
            console.print("       claude-orchestrator config --global --list")
            return

        # Get value from global config
        if value is None:
            val = _get_nested_value(global_data, key)
            console.print(val if val is not None else "")
            return

        # Set value in global config
        _set_nested_value(global_data, key, value)
        save_global_config(global_data)
        console.print(f"[green]✓[/green] Set global {key} = {value}")
        return

    # Handle project config
    cfg = load_config(project_dir)

    if list_all:
        console.print("\n[bold]Configuration[/bold] (merged: global + project)\n")
        console.print("[dim]# Git[/dim]")
        console.print(f"  git.provider: {cfg.git.provider}")
        console.print(f"  git.base_branch: {cfg.git.base_branch}")
        console.print(f"  git.destination_branch: {cfg.git.destination_branch}")
        console.print(f"  git.repo_slug: {cfg.git.repo_slug or '(auto)'}")
        console.print(f"  worktree_dir: {cfg.worktree_dir}")
        console.print("[dim]# Workflow[/dim]")
        console.print(f"  workflow.mode: {cfg.workflow.mode}")
        console.print(f"  workflow.stop_after_generate: {cfg.workflow.stop_after_generate}")
        console.print(f"  workflow.auto_approve: {cfg.workflow.auto_approve}")
        console.print(f"  workflow.auto_pr: {cfg.workflow.auto_pr}")
        console.print("[dim]# Tools & Permissions[/dim]")
        console.print(f"  tools.permission_mode: {cfg.tools.permission_mode}")
        if cfg.tools.allowed_cli:
            console.print(f"  tools.allowed_cli: {', '.join(cfg.tools.allowed_cli)}")
        if cfg.tools.allowed_tools:
            console.print(f"  tools.allowed_tools: {', '.join(cfg.tools.allowed_tools)}")
        if cfg.tools.disallowed_tools:
            console.print(f"  tools.disallowed_tools: {', '.join(cfg.tools.disallowed_tools)}")
        if cfg.tools.skip_permissions:
            console.print(f"  tools.skip_permissions: {cfg.tools.skip_permissions}")
        if cfg.mcps.enabled:
            console.print("[dim]# MCPs[/dim]")
            console.print(f"  mcps.enabled: {', '.join(cfg.mcps.enabled)}")
        if cfg.project.test_command:
            console.print("[dim]# Project[/dim]")
            console.print(f"  project.test_command: {cfg.project.test_command}")
        console.print()
        return

    if key is None:
        console.print("Usage: claude-orchestrator config [KEY] [VALUE]")
        console.print("       claude-orchestrator config --list")
        console.print("       claude-orchestrator config --global [KEY] [VALUE]")
        return

    # Get value
    if value is None:
        if key == "git.provider":
            console.print(cfg.git.provider)
        elif key == "git.base_branch":
            console.print(cfg.git.base_branch)
        elif key == "git.destination_branch":
            console.print(cfg.git.destination_branch)
        elif key == "git.repo_slug":
            console.print(cfg.git.repo_slug or "")
        elif key == "worktree_dir":
            console.print(cfg.worktree_dir)
        elif key == "project.test_command":
            console.print(cfg.project.test_command or "")
        elif key == "workflow.mode":
            console.print(cfg.workflow.mode)
        elif key == "workflow.stop_after_generate":
            console.print(str(cfg.workflow.stop_after_generate).lower())
        elif key == "workflow.auto_approve":
            console.print(str(cfg.workflow.auto_approve).lower())
        elif key == "workflow.auto_pr":
            console.print(str(cfg.workflow.auto_pr).lower())
        elif key == "tools.permission_mode":
            console.print(cfg.tools.permission_mode)
        elif key == "tools.allowed_cli":
            console.print(",".join(cfg.tools.allowed_cli) if cfg.tools.allowed_cli else "")
        elif key == "tools.allowed_tools":
            console.print(",".join(cfg.tools.allowed_tools) if cfg.tools.allowed_tools else "")
        elif key == "tools.disallowed_tools":
            console.print(",".join(cfg.tools.disallowed_tools) if cfg.tools.disallowed_tools else "")
        elif key == "tools.skip_permissions":
            console.print(str(cfg.tools.skip_permissions).lower())
        else:
            console.print(f"[red]Unknown key: {key}[/red]")
        return

    # Set value
    if key == "git.provider":
        cfg.git.provider = value
    elif key == "git.base_branch":
        cfg.git.base_branch = value
    elif key == "git.destination_branch":
        cfg.git.destination_branch = value
    elif key == "git.repo_slug":
        cfg.git.repo_slug = value
    elif key == "worktree_dir":
        cfg.worktree_dir = value
    elif key == "project.test_command":
        cfg.project.test_command = value
    elif key.startswith("mcps.enabled"):
        cfg.mcps.enabled = [v.strip() for v in value.split(",")]
    elif key == "workflow.mode":
        if value not in ("review", "yolo"):
            console.print(f"[red]Invalid mode: {value}. Use 'review' or 'yolo'[/red]")
            raise typer.Exit(1)
        cfg.workflow.mode = value
    elif key == "workflow.stop_after_generate":
        cfg.workflow.stop_after_generate = value.lower() in ("true", "1", "yes")
    elif key == "workflow.auto_approve":
        cfg.workflow.auto_approve = value.lower() in ("true", "1", "yes")
    elif key == "workflow.auto_pr":
        cfg.workflow.auto_pr = value.lower() in ("true", "1", "yes")
    elif key == "tools.permission_mode":
        valid_modes = ("default", "acceptEdits", "plan", "dontAsk", "bypassPermissions")
        if value not in valid_modes:
            console.print(f"[red]Invalid mode: {value}. Use one of: {', '.join(valid_modes)}[/red]")
            raise typer.Exit(1)
        cfg.tools.permission_mode = value
    elif key == "tools.allowed_cli":
        cfg.tools.allowed_cli = [v.strip() for v in value.split(",") if v.strip()]
    elif key == "tools.allowed_tools":
        cfg.tools.allowed_tools = [v.strip() for v in value.split(",") if v.strip()]
    elif key == "tools.disallowed_tools":
        cfg.tools.disallowed_tools = [v.strip() for v in value.split(",") if v.strip()]
    elif key == "tools.skip_permissions":
        cfg.tools.skip_permissions = value.lower() in ("true", "1", "yes")
    else:
        console.print(f"[red]Unknown key: {key}[/red]")
        raise typer.Exit(1)

    save_config(cfg, project_dir)
    console.print(f"[green]✓[/green] Set {key} = {value}")


def _get_nested_value(data: dict, key: str):
    """Get a nested value from a dictionary using dot notation."""
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def _set_nested_value(data: dict, key: str, value: str):
    """Set a nested value in a dictionary using dot notation."""
    parts = key.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Handle comma-separated values for lists
    if parts[-1] == "enabled":
        current[parts[-1]] = [v.strip() for v in value.split(",")]
    else:
        current[parts[-1]] = value


def _print_nested_config(data: dict, prefix: str = ""):
    """Print nested configuration dictionary."""
    for key, value in data.items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                console.print(f"{prefix}{key}.{subkey}: {subvalue}")


@app.command()
def status(
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory.",
    ),
):
    """Show status of previous run.

    Displays results from the last execution.
    """
    import json

    state_file = project_dir / ".claude-orchestrator" / ".state.json"

    if not state_file.exists():
        console.print("[yellow]No previous run found[/yellow]")
        raise typer.Exit()

    with open(state_file) as f:
        state = json.load(f)

    console.print(f"\n[bold]Last Run: {state.get('timestamp', 'Unknown')}[/bold]\n")

    # Create table
    table = Table(show_header=True, header_style="bold")
    table.add_column("Task")
    table.add_column("Status")
    table.add_column("Branch")
    table.add_column("Notes")

    for result in state.get("results", []):
        status = result.get("status", "unknown")
        status_style = {
            "success": "[green]✓ success[/green]",
            "failed": "[red]✗ failed[/red]",
            "skipped": "[yellow]○ skipped[/yellow]",
        }.get(status, status)

        notes = result.get("pr_url") or result.get("error") or ""

        table.add_row(
            result.get("task_id", ""),
            status_style,
            result.get("branch", ""),
            notes[:50] + "..." if len(notes) > 50 else notes,
        )

    console.print(table)


if __name__ == "__main__":
    app()

