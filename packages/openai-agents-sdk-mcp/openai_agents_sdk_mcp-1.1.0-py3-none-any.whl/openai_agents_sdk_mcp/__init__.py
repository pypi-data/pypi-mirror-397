"""
OpenAI Agents SDK MCP Server
A Model Context Protocol server for querying OpenAI Agents SDK documentation.
"""

__version__ = "1.0.0"
__author__ = "Gavin Zhang"

from .server import start_server
from .documentation import (
    get_documentation_for_feature,
    load_or_refresh_index,
)

__all__ = [
    "start_server",
    "get_documentation_for_feature",
    "load_or_refresh_index",
]
