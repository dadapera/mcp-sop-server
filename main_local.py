#!/usr/bin/env python3
"""
Main entry point for the SOP MCP Server.
Run this script to start the server.
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_sop_server import mcp
from mcp_sop_server.mcp_server import initialize_server

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting SOP MCP Server...")
    
    # Initialize the server before starting
    try:
        asyncio.run(initialize_server())
    except Exception as e:
        logger.error(f"❌ Failed to initialize server: {e}")
        sys.exit(1)
    
    logger.info("📚 SOP Server ready to accept requests")
    mcp.run(transport='stdio') 