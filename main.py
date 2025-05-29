#!/usr/bin/env python3
"""
Main entry point for the SOP MCP Server.
Run this script to start the server.
"""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_sop_server import mcp

if __name__ == "__main__":
    # Run the MCP server following official pattern
    mcp.run(transport='stdio') 