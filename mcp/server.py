#!/usr/bin/env python3
"""
Tactile Core MCP Server

A standalone MCP server for non-PAI Claude Code users.
This server provides tools for converting images to tactile-ready PDFs.

Usage:
    python server.py

Or add to Claude Code's MCP configuration:
    {
        "mcpServers": {
            "tactile": {
                "command": "python",
                "args": ["/path/to/radical-accessibility/mcp/server.py"]
            }
        }
    }
"""

import sys
from pathlib import Path

# Add the tactile-core library to the path
lib_path = Path(__file__).parent.parent / "lib" / "tactile-core" / "src"
sys.path.insert(0, str(lib_path))

# Import and run the server
from tactile_core.mcp_server.server import main

if __name__ == "__main__":
    main()
