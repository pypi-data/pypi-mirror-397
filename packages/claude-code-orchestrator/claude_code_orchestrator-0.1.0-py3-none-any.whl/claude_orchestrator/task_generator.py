"""Task generation from todo files using Claude.

Parses todo.md files and generates task configurations for parallel execution.
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from claude_orchestrator.config import Config
from claude_orchestrator.discovery import ProjectContext


@dataclass
class TaskConfig:
    """Configuration for a single task."""

    id: str
    branch: str
    title: str
    description: str
    files_hint: list[str] = field(default_factory=list)
    test_command: Optional[str] = None


@dataclass
class TasksConfig:
    """Configuration for all tasks."""

    settings: dict = field(default_factory=dict)
    tasks: list[TaskConfig] = field(default_factory=list)


def build_generation_prompt(
    todo_content: str,
    project_context: Optional[ProjectContext] = None,
    config: Optional[Config] = None,
) -> str:
    """Build the prompt for task generation.

    Args:
        todo_content: Content of the todo file
        project_context: Discovered project context
        config: Project configuration

    Returns:
        Prompt string for Claude
    """
    # Build project context section
    context_section = ""
    if project_context:
        context_section = f"""
## Project Context
Project: {project_context.project_name}
Tech Stack: {', '.join(project_context.tech_stack)}
Test Command: {project_context.test_command or 'Not configured'}

Key Files:
{chr(10).join(f'- {f}' for f in project_context.key_files[:10])}

Conventions: {project_context.conventions or 'Follow existing patterns'}
"""

    # Get settings from config
    base_branch = "main"
    dest_branch = "main"
    repo_slug = "REPO_SLUG"

    if config:
        base_branch = config.git.base_branch
        dest_branch = config.git.destination_branch
        repo_slug = config.git.repo_slug or "REPO_SLUG"

    return f"""Read the following todo list and generate a task_config.yaml for the parallel-tasks orchestrator.

## Todo List
{todo_content}

{context_section}

## Output Requirements

Generate a YAML configuration with this exact structure:

```yaml
settings:
  base_branch: {base_branch}
  destination_branch: {dest_branch}
  worktree_dir: ../worktrees
  repo_slug: {repo_slug}
  auto_cleanup: true

tasks:
  - id: <short-kebab-case-id>
    branch: feature/<descriptive-branch-name>
    title: "feat: <concise title>"
    description: |
      <Detailed description of what needs to be done>

      Requirements:
      - <Specific requirement 1>
      - <Specific requirement 2>

      Implementation hints:
      - <Helpful hint about how to implement>
    files_hint:
      - <file1.py>
      - <file2.html>
    test_command: "<pytest command or null>"
```

## Guidelines for Each Task

1. **id**: Short, unique, kebab-case (e.g., "add-swagger-link")
2. **branch**: Use feature/ prefix with descriptive name
3. **title**: Follow conventional commits (feat:, fix:, refactor:, etc.)
4. **description**:
   - Be specific about what to implement
   - List concrete requirements
   - Include implementation hints when helpful
   - Reference existing patterns in the codebase
5. **files_hint**: List the most likely files to modify
6. **test_command**: pytest command or null for UI-only changes

## Important
- Output ONLY the YAML content, no markdown fences or explanations
- Make descriptions detailed enough that another Claude agent can implement without ambiguity
- Consider dependencies between tasks (if any)

Generate the task_config.yaml now:
"""


async def generate_tasks_with_claude(
    todo_path: Path,
    project_context: Optional[ProjectContext] = None,
    config: Optional[Config] = None,
) -> Optional[TasksConfig]:
    """Generate task configuration from a todo file using Claude.

    Args:
        todo_path: Path to the todo file
        project_context: Discovered project context
        config: Project configuration

    Returns:
        TasksConfig or None if generation fails
    """
    if not todo_path.exists():
        return None

    todo_content = todo_path.read_text()
    prompt = build_generation_prompt(todo_content, project_context, config)

    project_root = todo_path.parent

    cmd = [
        "claude",
        "--print",
        "-p",
        prompt,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=project_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=120,  # 2 minute timeout
        )

        if process.returncode != 0:
            return None

        output = stdout.decode().strip()

        # Try to extract YAML from output
        yaml_str = output

        # Handle markdown fences
        if "```yaml" in output:
            start = output.find("```yaml") + 7
            end = output.find("```", start)
            yaml_str = output[start:end].strip()
        elif "```" in output:
            start = output.find("```") + 3
            end = output.find("```", start)
            yaml_str = output[start:end].strip()

        # Find YAML start markers
        for marker in ["settings:", "tasks:"]:
            if marker in yaml_str:
                idx = yaml_str.find(marker)
                if idx > 0:
                    yaml_str = yaml_str[idx:]
                break

        # Parse YAML
        data = yaml.safe_load(yaml_str)

        if not data or "tasks" not in data:
            return None

        # Convert to TasksConfig
        tasks = []
        for task_data in data.get("tasks", []):
            tasks.append(
                TaskConfig(
                    id=task_data.get("id", ""),
                    branch=task_data.get("branch", ""),
                    title=task_data.get("title", ""),
                    description=task_data.get("description", ""),
                    files_hint=task_data.get("files_hint", []),
                    test_command=task_data.get("test_command"),
                )
            )

        return TasksConfig(
            settings=data.get("settings", {}),
            tasks=tasks,
        )

    except asyncio.TimeoutError:
        return None
    except yaml.YAMLError:
        return None
    except Exception:
        return None


def generate_tasks_sync(
    todo_path: Path,
    project_context: Optional[ProjectContext] = None,
    config: Optional[Config] = None,
) -> Optional[TasksConfig]:
    """Synchronous wrapper for task generation.

    Args:
        todo_path: Path to the todo file
        project_context: Discovered project context
        config: Project configuration

    Returns:
        TasksConfig or None if generation fails
    """
    return asyncio.run(generate_tasks_with_claude(todo_path, project_context, config))


def save_tasks_config(tasks_config: TasksConfig, output_path: Path) -> None:
    """Save tasks configuration to a YAML file.

    Args:
        tasks_config: Tasks configuration to save
        output_path: Path to save the YAML file
    """
    data = {
        "settings": tasks_config.settings,
        "tasks": [
            {
                "id": task.id,
                "branch": task.branch,
                "title": task.title,
                "description": task.description,
                "files_hint": task.files_hint,
                "test_command": task.test_command,
            }
            for task in tasks_config.tasks
        ],
    }

    with open(output_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_tasks_config(config_path: Path) -> Optional[TasksConfig]:
    """Load tasks configuration from a YAML file.

    Args:
        config_path: Path to the YAML file

    Returns:
        TasksConfig or None if loading fails
    """
    if not config_path.exists():
        return None

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f)

        if not data or "tasks" not in data:
            return None

        tasks = []
        for task_data in data.get("tasks", []):
            tasks.append(
                TaskConfig(
                    id=task_data.get("id", ""),
                    branch=task_data.get("branch", ""),
                    title=task_data.get("title", ""),
                    description=task_data.get("description", ""),
                    files_hint=task_data.get("files_hint", []),
                    test_command=task_data.get("test_command"),
                )
            )

        return TasksConfig(
            settings=data.get("settings", {}),
            tasks=tasks,
        )

    except Exception:
        return None

