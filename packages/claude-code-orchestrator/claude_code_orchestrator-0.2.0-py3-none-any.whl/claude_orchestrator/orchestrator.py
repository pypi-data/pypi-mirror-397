"""Orchestrator for running parallel Claude Code agents on multiple tasks.

Each task runs in its own git worktree with a dedicated agent instance.
Supports plan mode with manual or automatic approval, and creates PRs on completion.
"""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from claude_orchestrator.config import Config, load_config
from claude_orchestrator.discovery import ProjectContext, discover_sync
from claude_orchestrator.git_provider import (
    GitProvider,
    GitProviderStatus,
    get_pr_instructions,
    get_provider_status,
)
from claude_orchestrator.task_generator import TaskConfig, TasksConfig, load_tasks_config


@dataclass
class TaskResult:
    """Result of running a task."""

    task_id: str
    status: str  # "success", "failed", "skipped"
    branch: str
    worktree_path: Optional[Path] = None
    pr_url: Optional[str] = None
    error: Optional[str] = None


def run_git(args: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a git command and return result.

    Args:
        args: Git command arguments
        cwd: Working directory

    Returns:
        CompletedProcess with result
    """
    return subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def create_worktree(
    branch: str,
    worktree_dir: Path,
    base_branch: str = "main",
    repo_root: Optional[Path] = None,
) -> Path:
    """Create a git worktree for the given branch.

    Args:
        branch: Branch name to create
        worktree_dir: Base directory for worktrees
        base_branch: Branch to base the new branch on
        repo_root: Root of the repository

    Returns:
        Path to the created worktree
    """
    if repo_root is None:
        repo_root = Path.cwd()

    worktree_path = worktree_dir / branch
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing worktree if present
    if worktree_path.exists():
        run_git(["worktree", "remove", "--force", str(worktree_path)], cwd=repo_root)

    # Fetch latest from origin
    run_git(["fetch", "origin", base_branch], cwd=repo_root)

    # Create new worktree with new branch
    result = run_git(
        ["worktree", "add", "-b", branch, str(worktree_path), f"origin/{base_branch}"],
        cwd=repo_root,
    )
    if result.returncode != 0:
        # Branch might already exist, try without -b
        run_git(["branch", "-D", branch], cwd=repo_root)  # Delete local branch if exists
        result = run_git(
            ["worktree", "add", "-b", branch, str(worktree_path), f"origin/{base_branch}"],
            cwd=repo_root,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to create worktree: {result.stderr}")

    # Copy .env to worktree if exists
    env_file = repo_root / ".env"
    if env_file.exists():
        shutil.copy(env_file, worktree_path / ".env")

    return worktree_path


def cleanup_worktree(branch: str, worktree_dir: Path, repo_root: Optional[Path] = None) -> None:
    """Remove a git worktree.

    Args:
        branch: Branch name
        worktree_dir: Base directory for worktrees
        repo_root: Root of the repository
    """
    if repo_root is None:
        repo_root = Path.cwd()

    worktree_path = worktree_dir / branch
    if worktree_path.exists():
        run_git(["worktree", "remove", "--force", str(worktree_path)], cwd=repo_root)


def build_agent_prompt(
    task: TaskConfig,
    provider_status: GitProviderStatus,
    project_context: Optional[ProjectContext] = None,
    config: Optional[Config] = None,
) -> str:
    """Build the prompt for a Claude Code agent.

    Args:
        task: Task configuration
        provider_status: Git provider status
        project_context: Discovered project context
        config: Project configuration

    Returns:
        Prompt string for the agent
    """
    # Files hint
    files_list = (
        "\n".join(f"- {f}" for f in task.files_hint)
        if task.files_hint
        else "- Determine based on task"
    )

    # Test info
    test_info = task.test_command or "Manual verification - document steps in commit message"

    # Agent instructions path
    agent_instructions = ""
    if config and config.project.agent_instructions:
        agent_instructions = f"\nRead the instructions in {config.project.agent_instructions} before starting.\n"

    # Destination branch
    dest_branch = config.git.destination_branch if config else "main"
    repo_slug = config.git.repo_slug if config else None

    # PR instructions
    pr_instructions = get_pr_instructions(
        provider_status=provider_status,
        branch=task.branch,
        title=task.title,
        description=task.description[:200] + "..." if len(task.description) > 200 else task.description,
        dest_branch=dest_branch,
        repo_slug=repo_slug,
    )

    return f"""{agent_instructions}
## Task: {task.title}

{task.description}

## Relevant Files
{files_list}

## Requirements
1. Implement the functionality described above
2. Follow project standards and conventions
3. Add tests if applicable
4. Only modify files within scope

## Testing
{test_info}

## When Complete
Create a commit with a descriptive message following project conventions.

{pr_instructions}
"""


def build_claude_args(config: Optional[Config], auto_approve: bool = False) -> list[str]:
    """Build Claude CLI arguments from config.

    Args:
        config: Project configuration
        auto_approve: Whether to auto-approve agent plans

    Returns:
        List of CLI arguments
    """
    args = []

    if config and config.tools:
        tools = config.tools

        # Permission mode
        if tools.skip_permissions or auto_approve:
            args.append("--dangerously-skip-permissions")
        elif tools.permission_mode != "default":
            args.extend(["--permission-mode", tools.permission_mode])

        # Allowed tools - combine CLI tools with explicit allowed tools
        allowed = list(tools.allowed_tools)
        for cli_tool in tools.allowed_cli:
            # Convert CLI tool name to Bash pattern
            allowed.append(f"Bash({cli_tool}:*)")
        if allowed:
            args.extend(["--allowedTools"] + allowed)

        # Disallowed tools
        if tools.disallowed_tools:
            args.extend(["--disallowedTools"] + tools.disallowed_tools)

        # Additional directories
        for add_dir in tools.add_dirs:
            args.extend(["--add-dir", add_dir])

    elif auto_approve:
        args.append("--dangerously-skip-permissions")

    return args


async def run_agent(
    task: TaskConfig,
    worktree_path: Path,
    provider_status: GitProviderStatus,
    project_context: Optional[ProjectContext] = None,
    config: Optional[Config] = None,
    auto_approve: bool = False,
    log_file: Optional[Path] = None,
) -> bool:
    """Run Claude Code agent for a task.

    Args:
        task: Task configuration
        worktree_path: Path to the worktree
        provider_status: Git provider status
        project_context: Discovered project context
        config: Project configuration
        auto_approve: Whether to auto-approve the plan
        log_file: Path to write agent output

    Returns:
        True if agent completed successfully
    """
    prompt = build_agent_prompt(task, provider_status, project_context, config)

    # Build claude command with tools/permissions config
    cmd = ["claude"]
    cmd.extend(build_claude_args(config, auto_approve))
    cmd.extend(["--print", "--verbose", "-p", prompt])

    # Open log file if specified
    log_handle = open(log_file, "w") if log_file else None

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=worktree_path,
            stdout=log_handle or asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.DEVNULL if auto_approve else None,
        )

        if not auto_approve:
            # Interactive mode - agent handles its own I/O
            await process.wait()
        else:
            # Auto-approve mode - capture output
            stdout, _ = await process.communicate()
            if log_handle and stdout:
                log_handle.write(stdout.decode() if isinstance(stdout, bytes) else stdout)

        return process.returncode == 0

    finally:
        if log_handle:
            log_handle.close()


def push_branch(branch: str, worktree_path: Path) -> bool:
    """Push branch to origin.

    Args:
        branch: Branch name
        worktree_path: Path to the worktree

    Returns:
        True if push succeeded
    """
    result = run_git(["push", "-u", "origin", branch], cwd=worktree_path)
    return result.returncode == 0


async def run_task(
    task: TaskConfig,
    config: Config,
    provider_status: GitProviderStatus,
    project_context: Optional[ProjectContext] = None,
    auto_approve: bool = False,
    dry_run: bool = False,
    no_pr: bool = False,
    logs_dir: Optional[Path] = None,
) -> TaskResult:
    """Run a single task end-to-end.

    Args:
        task: Task configuration
        config: Project configuration
        provider_status: Git provider status
        project_context: Discovered project context
        auto_approve: Whether to auto-approve agent plans
        dry_run: Show what would be done without executing
        no_pr: Skip PR creation
        logs_dir: Directory for log files

    Returns:
        TaskResult with status and details
    """
    repo_root = config.project_root or Path.cwd()
    worktree_dir = repo_root / config.worktree_dir
    worktree_path = None

    try:
        # Create worktree
        print(f"\n[{task.id}] Creating worktree for branch: {task.branch}")
        if not dry_run:
            worktree_path = create_worktree(
                task.branch,
                worktree_dir,
                config.git.base_branch,
                repo_root,
            )
            print(f"[{task.id}] Worktree created at: {worktree_path}")

        # Prepare log file
        log_file = None
        if logs_dir:
            logs_dir.mkdir(parents=True, exist_ok=True)
            log_file = logs_dir / f"{task.id}.log"

        # Run agent
        print(f"[{task.id}] Running Claude Code agent...")
        if dry_run:
            print(f"[{task.id}] DRY RUN - Would run agent with prompt:")
            prompt = build_agent_prompt(task, provider_status, project_context, config)
            print(prompt[:500] + "...")
            return TaskResult(
                task_id=task.id,
                status="skipped",
                branch=task.branch,
                error="Dry run",
            )

        success = await run_agent(
            task,
            worktree_path,
            provider_status,
            project_context,
            config,
            auto_approve=auto_approve,
            log_file=log_file,
        )

        if not success:
            return TaskResult(
                task_id=task.id,
                status="failed",
                branch=task.branch,
                worktree_path=worktree_path,
                error="Agent failed - check logs",
            )

        # Push branch
        print(f"[{task.id}] Pushing branch to origin...")
        if not push_branch(task.branch, worktree_path):
            return TaskResult(
                task_id=task.id,
                status="failed",
                branch=task.branch,
                worktree_path=worktree_path,
                error="Failed to push branch",
            )

        # Note: PR creation is now handled by the agent using MCP or gh CLI
        return TaskResult(
            task_id=task.id,
            status="success",
            branch=task.branch,
            worktree_path=worktree_path,
        )

    except Exception as e:
        return TaskResult(
            task_id=task.id,
            status="failed",
            branch=task.branch,
            worktree_path=worktree_path,
            error=str(e),
        )


def save_state(results: list[TaskResult], state_file: Path) -> None:
    """Save execution state to file.

    Args:
        results: List of task results
        state_file: Path to state file
    """
    state = {
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "task_id": r.task_id,
                "status": r.status,
                "branch": r.branch,
                "pr_url": r.pr_url,
                "error": r.error,
            }
            for r in results
        ],
    }
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def print_summary(results: list[TaskResult]) -> None:
    """Print execution summary.

    Args:
        results: List of task results
    """
    print("\n" + "=" * 60)
    print("EXECUTION SUMMARY")
    print("=" * 60)

    for result in results:
        status_emoji = {"success": "✓", "failed": "✗", "skipped": "○"}.get(result.status, "?")
        print(f"\n{status_emoji} {result.task_id} ({result.branch})")
        print(f"  Status: {result.status}")
        if result.pr_url:
            print(f"  PR: {result.pr_url}")
        if result.error:
            print(f"  Error: {result.error}")

    success_count = sum(1 for r in results if r.status == "success")
    print(f"\n{success_count}/{len(results)} tasks completed successfully")


async def run_tasks(
    tasks_config: TasksConfig,
    config: Config,
    task_ids: Optional[list[str]] = None,
    auto_approve: bool = False,
    keep_worktrees: bool = False,
    dry_run: bool = False,
    no_pr: bool = False,
    sequential: bool = False,
) -> list[TaskResult]:
    """Run multiple tasks.

    Args:
        tasks_config: Tasks configuration
        config: Project configuration
        task_ids: Specific task IDs to run (None = all)
        auto_approve: Whether to auto-approve agent plans
        keep_worktrees: Don't cleanup worktrees after completion
        dry_run: Show what would be done without executing
        no_pr: Skip PR creation
        sequential: Run tasks sequentially instead of in parallel

    Returns:
        List of TaskResult objects
    """
    repo_root = config.project_root or Path.cwd()

    # Get provider status
    provider_status = get_provider_status(str(repo_root))

    if not provider_status.is_ready and not dry_run:
        print(f"Warning: Git provider not ready: {provider_status.error}")

    # Discover project context
    project_context = discover_sync(repo_root, use_claude=False)

    # Filter tasks
    tasks = tasks_config.tasks
    if task_ids:
        tasks = [t for t in tasks if t.id in task_ids]

    if not tasks:
        print("No tasks to run")
        return []

    print(f"Running {len(tasks)} task(s):")
    for task in tasks:
        print(f"  - {task.id}: {task.title}")

    # Prepare logs directory
    logs_dir = repo_root / ".claude-orchestrator" / "logs"

    # Run tasks
    results: list[TaskResult] = []

    if sequential:
        # Run sequentially
        for task in tasks:
            result = await run_task(
                task,
                config,
                provider_status,
                project_context,
                auto_approve,
                dry_run,
                no_pr,
                logs_dir,
            )
            results.append(result)
    else:
        # Run in parallel
        coros = [
            run_task(
                task,
                config,
                provider_status,
                project_context,
                auto_approve,
                dry_run,
                no_pr,
                logs_dir,
            )
            for task in tasks
        ]
        results = list(await asyncio.gather(*coros))

    # Cleanup worktrees
    if not keep_worktrees and not dry_run:
        worktree_dir = repo_root / config.worktree_dir
        print("\nCleaning up worktrees...")
        for task in tasks:
            cleanup_worktree(task.branch, worktree_dir, repo_root)

    # Save state
    state_file = repo_root / ".claude-orchestrator" / ".state.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)
    save_state(results, state_file)

    # Print summary
    print_summary(results)

    return results


def run_tasks_sync(
    tasks_config: TasksConfig,
    config: Config,
    task_ids: Optional[list[str]] = None,
    auto_approve: bool = False,
    keep_worktrees: bool = False,
    dry_run: bool = False,
    no_pr: bool = False,
    sequential: bool = False,
) -> list[TaskResult]:
    """Synchronous wrapper for run_tasks.

    Args:
        tasks_config: Tasks configuration
        config: Project configuration
        task_ids: Specific task IDs to run (None = all)
        auto_approve: Whether to auto-approve agent plans
        keep_worktrees: Don't cleanup worktrees after completion
        dry_run: Show what would be done without executing
        no_pr: Skip PR creation
        sequential: Run tasks sequentially instead of in parallel

    Returns:
        List of TaskResult objects
    """
    return asyncio.run(
        run_tasks(
            tasks_config,
            config,
            task_ids,
            auto_approve,
            keep_worktrees,
            dry_run,
            no_pr,
            sequential,
        )
    )

