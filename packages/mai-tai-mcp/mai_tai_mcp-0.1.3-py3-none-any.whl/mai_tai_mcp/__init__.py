"""Mai-Tai MCP Server - Connect your coding agent to mai-tai."""

__version__ = "0.1.0"

from .backend import MaiTaiBackend, MaiTaiBackendError, create_backend
from .config import MaiTaiConfig, get_config
from .server import main, mcp

__all__ = [
    "MaiTaiBackend",
    "MaiTaiBackendError",
    "MaiTaiConfig",
    "create_backend",
    "get_config",
    "main",
    "mcp",
]

