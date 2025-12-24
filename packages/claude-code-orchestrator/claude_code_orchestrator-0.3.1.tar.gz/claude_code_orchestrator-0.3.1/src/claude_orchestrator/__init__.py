"""Claude Orchestrator - Run parallel Claude Code agents on multiple tasks."""

__version__ = "0.3.1"

from claude_orchestrator.config import Config, load_config
from claude_orchestrator.git_provider import GitProvider, GitProviderStatus, get_provider_status
from claude_orchestrator.mcp_registry import AuthType, MCPDefinition, MCP_REGISTRY

__all__ = [
    "__version__",
    "Config",
    "load_config",
    "GitProvider",
    "GitProviderStatus",
    "get_provider_status",
    "AuthType",
    "MCPDefinition",
    "MCP_REGISTRY",
]

