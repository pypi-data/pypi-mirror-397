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
from claude_orchestrator.config import Config, GitConfig, config_exists, load_config, save_config
from claude_orchestrator.discovery import discover_sync
from claude_orchestrator.git_provider import GitProvider, get_provider_status
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
    else:
        # Check common MCPs
        mcp_list = ["bitbucket", "atlassian", "linear", "postgres", "chrome"]

    # Get status of each MCP
    for mcp_name in mcp_list:
        status = get_mcp_status(mcp_name)

        if status.is_ready:
            console.print(f"  [green]✓[/green] {mcp_name}: ready")
        elif status.is_configured:
            if status.auth_type == AuthType.OAUTH_BROWSER:
                console.print(f"  [yellow]○[/yellow] {mcp_name}: configured (may need browser auth)")
            else:
                console.print(f"  [yellow]![/yellow] {mcp_name}: {status.message}")
        else:
            # Check if it's needed
            if mcp_name == "bitbucket" and provider_status.provider != GitProvider.BITBUCKET:
                console.print(f"  [dim]○[/dim] {mcp_name}: not needed (using {provider_name})")
            else:
                console.print(f"  [red]✗[/red] {mcp_name}: not configured")
                if status.setup_instructions:
                    console.print(f"      Setup:\n{status.setup_instructions}")

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
            base_branch="main",
            destination_branch="main",
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
    project_dir: Path = typer.Option(
        Path.cwd(),
        "--project-dir",
        "-d",
        help="Project directory.",
    ),
):
    """Generate task configuration from a todo file.

    Uses Claude to analyze the todo file and generate task_config.yaml.
    """
    if not from_todo.exists():
        console.print(f"[red]Error: Todo file not found: {from_todo}[/red]")
        raise typer.Exit(1)

    console.print("[bold]Generating task configuration[/bold]\n")
    console.print(f"  Input: {from_todo}")
    console.print(f"  Output: {output}")

    # Load config
    config = load_config(project_dir)

    # Discover project
    console.print("\nAnalyzing project...")
    context = discover_sync(project_dir, use_claude=False)

    # Generate tasks
    console.print("Generating tasks with Claude...")
    tasks_config = generate_tasks_sync(from_todo, context, config)

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
    """
    # Handle --from-todo
    if from_todo:
        if not from_todo.exists():
            console.print(f"[red]Error: Todo file not found: {from_todo}[/red]")
            raise typer.Exit(1)

        console.print("[bold]Generating tasks from todo...[/bold]\n")

        # Load config
        config = load_config(project_dir)

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

        if not execute:
            console.print(f"\nReview {config_file} and run: claude-orchestrator run")
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

    # Load project config
    config = load_config(project_dir)

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

