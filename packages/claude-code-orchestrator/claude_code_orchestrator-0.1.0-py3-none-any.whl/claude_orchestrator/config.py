"""Configuration handling for claude-orchestrator.

Handles loading, saving, and validating .claude-orchestrator.yaml configuration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

from claude_orchestrator.mcp_registry import AuthType, register_custom_mcp


CONFIG_FILENAME = ".claude-orchestrator.yaml"


@dataclass
class GitConfig:
    """Git-related configuration."""

    provider: str = "auto"  # "auto", "bitbucket", "github"
    base_branch: str = "main"
    destination_branch: str = "main"
    repo_slug: Optional[str] = None  # Required for Bitbucket
    owner: Optional[str] = None  # For GitHub
    repo: Optional[str] = None  # For GitHub


@dataclass
class MCPConfig:
    """MCP-related configuration."""

    enabled: list[str] = field(default_factory=list)
    custom: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class ProjectConfig:
    """Project context configuration."""

    key_files: list[str] = field(default_factory=list)
    test_command: Optional[str] = None
    agent_instructions: Optional[str] = None


@dataclass
class Config:
    """Main configuration for claude-orchestrator."""

    git: GitConfig = field(default_factory=GitConfig)
    worktree_dir: str = "../worktrees"
    mcps: MCPConfig = field(default_factory=MCPConfig)
    project: ProjectConfig = field(default_factory=ProjectConfig)

    # Runtime settings (not persisted)
    project_root: Optional[Path] = None


def load_config(project_root: Optional[Path] = None) -> Config:
    """Load configuration from .claude-orchestrator.yaml.

    Args:
        project_root: Root directory of the project. If None, uses current directory.

    Returns:
        Config object with loaded or default values
    """
    if project_root is None:
        project_root = Path.cwd()

    config_path = project_root / CONFIG_FILENAME
    config = Config(project_root=project_root)

    if not config_path.exists():
        return config

    try:
        with open(config_path) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        return config

    # Parse git config
    if "git" in data:
        git_data = data["git"]
        config.git = GitConfig(
            provider=git_data.get("provider", "auto"),
            base_branch=git_data.get("base_branch", "main"),
            destination_branch=git_data.get("destination_branch", "main"),
            repo_slug=git_data.get("repo_slug"),
            owner=git_data.get("owner"),
            repo=git_data.get("repo"),
        )

    # Parse worktree_dir
    if "worktree_dir" in data:
        config.worktree_dir = data["worktree_dir"]

    # Parse MCP config
    if "mcps" in data:
        mcps_data = data["mcps"]
        config.mcps = MCPConfig(
            enabled=mcps_data.get("enabled", []),
            custom=mcps_data.get("custom", []),
        )

        # Register custom MCPs
        for custom_mcp in config.mcps.custom:
            register_custom_mcp(
                name=custom_mcp.get("name", ""),
                package=custom_mcp.get("package", ""),
                auth_type=AuthType(custom_mcp.get("auth_type", "env_vars")),
                env_vars=custom_mcp.get("env_vars", []),
                setup_instructions=custom_mcp.get("setup_instructions", ""),
            )

    # Parse project config
    if "project" in data:
        project_data = data["project"]
        config.project = ProjectConfig(
            key_files=project_data.get("key_files", []),
            test_command=project_data.get("test_command"),
            agent_instructions=project_data.get("agent_instructions"),
        )

    return config


def save_config(config: Config, project_root: Optional[Path] = None) -> None:
    """Save configuration to .claude-orchestrator.yaml.

    Args:
        config: Configuration to save
        project_root: Root directory of the project. If None, uses config.project_root or cwd.
    """
    if project_root is None:
        project_root = config.project_root or Path.cwd()

    config_path = project_root / CONFIG_FILENAME

    data: dict[str, Any] = {}

    # Git config
    git_data: dict[str, Any] = {
        "provider": config.git.provider,
        "base_branch": config.git.base_branch,
        "destination_branch": config.git.destination_branch,
    }
    if config.git.repo_slug:
        git_data["repo_slug"] = config.git.repo_slug
    if config.git.owner:
        git_data["owner"] = config.git.owner
    if config.git.repo:
        git_data["repo"] = config.git.repo
    data["git"] = git_data

    # Worktree dir
    data["worktree_dir"] = config.worktree_dir

    # MCPs config
    if config.mcps.enabled or config.mcps.custom:
        mcps_data: dict[str, Any] = {}
        if config.mcps.enabled:
            mcps_data["enabled"] = config.mcps.enabled
        if config.mcps.custom:
            mcps_data["custom"] = config.mcps.custom
        data["mcps"] = mcps_data

    # Project config
    if config.project.key_files or config.project.test_command or config.project.agent_instructions:
        project_data: dict[str, Any] = {}
        if config.project.key_files:
            project_data["key_files"] = config.project.key_files
        if config.project.test_command:
            project_data["test_command"] = config.project.test_command
        if config.project.agent_instructions:
            project_data["agent_instructions"] = config.project.agent_instructions
        data["project"] = project_data

    with open(config_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def config_exists(project_root: Optional[Path] = None) -> bool:
    """Check if configuration file exists.

    Args:
        project_root: Root directory of the project. If None, uses current directory.

    Returns:
        True if config file exists
    """
    if project_root is None:
        project_root = Path.cwd()

    return (project_root / CONFIG_FILENAME).exists()

