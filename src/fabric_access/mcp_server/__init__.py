"""
MCP Server for Fabric Accessible Graphics Toolkit.

Exposes the fabric-access image-to-piaf conversion tools to Claude,
enabling natural language interaction for converting architectural
images to tactile graphics.
"""

from fabric_access.mcp_server.server import main

__all__ = ['main']
