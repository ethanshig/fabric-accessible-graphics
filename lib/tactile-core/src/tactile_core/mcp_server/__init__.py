"""
MCP Server for Fabric Accessible Graphics Toolkit.

Exposes the tactile image-to-piaf conversion tools to Claude,
enabling natural language interaction for converting architectural
images to tactile graphics.
"""

from tactile_core.mcp_server.server import main

__all__ = ['main']
