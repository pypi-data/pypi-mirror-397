"""Anzo MCP Server - Model Context Protocol server for Anzo Graph Database.

Provides 45+ tools and 10 comprehensive prompts for working with Anzo knowledge graphs
through AI assistants like Claude Desktop and Cursor IDE.
"""

__version__ = "1.0.0"
__author__ = "Paresh Khandelwal"
__license__ = "Apache-2.0"

# Package exports
from ags_mcp.config import AnzoConfig, get_config
from ags_mcp.client import AnzoAPIClient
from ags_mcp.errors import (
    AnzoAPIError,
    AnzoConnectionError,
    AnzoAuthenticationError,
    AnzoNotFoundError,
    AnzoValidationError,
    AnzoTimeoutError
)

__all__ = [
    "AnzoConfig",
    "get_config",
    "AnzoAPIClient",
    "AnzoAPIError",
    "AnzoConnectionError",
    "AnzoAuthenticationError",
    "AnzoNotFoundError",
    "AnzoValidationError",
    "AnzoTimeoutError",
    "__version__",
]
