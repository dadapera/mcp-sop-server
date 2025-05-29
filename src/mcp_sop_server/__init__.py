"""
MCP SOP Server - A Model Context Protocol server for accessing Standard Operating Procedures.

This package provides Italian language support for semantic search and retrieval
of company SOP documentation using ChromaDB and sentence transformers.
"""

from .mcp_server import mcp, document_processor, document_searcher
from .document_processor import DocumentProcessor
from .document_searcher import DocumentSearcher

__version__ = "1.0.0"
__author__ = "dadapera"
__description__ = "MCP Server for SOP Document Access"

__all__ = [
    "mcp",
    "document_processor",
    "document_searcher",
    "DocumentProcessor", 
    "DocumentSearcher"
] 