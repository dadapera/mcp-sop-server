import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from fastmcp import FastMCP
from .document_processor import DocumentProcessor
from .document_searcher import DocumentSearcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Initialize FastMCP server
mcp = FastMCP("SOP Document Server")

# Get the project root directory (where main.py is located)
# Go up from src/mcp_sop_server/ to the project root
project_root = Path(__file__).parent.parent.parent
sop_directory = project_root / "sop_documents"

# Initialize components with absolute path
document_processor = DocumentProcessor(str(sop_directory))
document_searcher = DocumentSearcher()
logger = logging.getLogger(__name__)

# Track initialization status
is_initialized = False

async def initialize_server():
    """Initialize the server with SOP documents."""
    global is_initialized
    
    if is_initialized:
        return
        
    logger.info("🔄 Initializing SOP server...")
    
    try:
        # Check if collection already has documents
        stats = document_searcher.get_collection_stats()
        
        if stats.get('total_chunks', 0) == 0:
            # Process and add documents
            logger.info("⚠️  No existing documents found, processing SOP documents...")
            documents = document_processor.scan_sop_documents()
            if documents:
                logger.info(f"📊 Found {len(documents)} SOP documents to process...")
                success = document_searcher.add_documents(documents)
                if success:
                    is_initialized = True
                    final_stats = document_searcher.get_collection_stats()
                    logger.info(f"✅ SOP server initialized successfully - {final_stats.get('total_chunks', 0)} document chunks indexed")
                else:
                    logger.error("❌ Failed to initialize document search index")
                    raise Exception("Failed to initialize document search index")
            else:
                logger.warning("⚠️  No SOP documents found to process")
                # Still mark as initialized to prevent repeated attempts
                is_initialized = True
        else:
            is_initialized = True
            logger.info(f"✅ Using existing document collection - {stats.get('total_chunks', 0)} document chunks available")
            
    except Exception as e:
        logger.error(f"❌ Error during server initialization: {e}")
        # Print to stderr so MCP client can see the error
        print(f"SOP Server initialization error: {e}", file=sys.stderr)
        raise

async def ensure_initialized():
    """Ensure the server is initialized with documents."""
    global is_initialized
    
    if not is_initialized:
        await initialize_server()

@mcp.tool()
async def search_sop_documents(
    query: str,
    max_results: int = 5,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search SOP documents using semantic search with Italian language support.
    
    Args:
        query: Search query in Italian or English describing what you're looking for
        max_results: Maximum number of results to return (default: 5)
        category: Optional SOP category to filter results (e.g., "SOP01 Quality System Documentation Management")
    
    Returns:
        Dictionary containing search results with relevant SOP content and metadata
    """
    logger.info(f"🔧 Called tool: search_sop_documents - query: '{query}', max_results: {max_results}, category: {category}")
    
    try:
        # Initialize on first call if not already done
        await ensure_initialized()
        
        results = document_searcher.search(
            query=query,
            n_results=max_results,
            sop_category=category
        )
        
        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error searching SOP documents: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query
        }

@mcp.tool()
async def list_sop_categories() -> Dict[str, Any]:
    """
    Get a list of all available SOP categories.
    
    Returns:
        Dictionary containing all SOP categories available in the system
    """
    logger.info("🔧 Called tool: list_sop_categories")
    
    try:
        categories = document_processor.get_sop_categories()
        stats = document_searcher.get_collection_stats()
        
        return {
            "success": True,
            "categories": categories,
            "total_categories": len(categories),
            "collection_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error listing SOP categories: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_sop_by_category(category: str) -> Dict[str, Any]:
    """
    Get all SOP documents in a specific category.
    
    Args:
        category: SOP category name (e.g., "SOP01 Quality System Documentation Management")
    
    Returns:
        Dictionary containing all SOPs in the specified category
    """
    logger.info(f"🔧 Called tool: get_sop_by_category - category: '{category}'")
    
    try:
        await ensure_initialized()
        
        sops = document_searcher.get_sop_by_category(category)
        
        return {
            "success": True,
            "category": category,
            "sop_count": len(sops),
            "sops": sops
        }
        
    except Exception as e:
        logger.error(f"Error getting SOPs by category: {e}")
        return {
            "success": False,
            "error": str(e),
            "category": category
        }

@mcp.tool()
async def get_sop_guidance(
    situation: str,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get guidance on what to do in a specific situation based on SOP documents.
    
    Args:
        situation: Description of the situation in Italian or English
        category: Optional SOP category to focus the search
    
    Returns:
        Dictionary containing relevant SOP guidance and procedures
    """
    logger.info(f"🔧 Called tool: get_sop_guidance - situation: '{situation}', category: {category}")
    
    try:
        await ensure_initialized()
        
        # Search for relevant SOPs
        search_results = document_searcher.search(
            query=situation,
            n_results=5,
            sop_category=category
        )
        
        # Format guidance response
        guidance = []
        for result in search_results:
            guidance.append({
                "sop_name": result['sop_name'],
                "sop_category": result['sop_category'],
                "relevant_content": result['content'],
                "similarity_score": result['similarity_score'],
                "file_path": result['file_path']
            })
        
        return {
            "success": True,
            "situation": situation,
            "guidance_found": len(guidance) > 0,
            "guidance": guidance,
            "recommendation": "Follow the procedures outlined in the relevant SOP documents above." if guidance else "No specific SOP guidance found for this situation."
        }
        
    except Exception as e:
        logger.error(f"Error getting SOP guidance: {e}")
        return {
            "success": False,
            "error": str(e),
            "situation": situation
        }

@mcp.tool()
async def refresh_sop_database() -> Dict[str, Any]:
    """
    Refresh the SOP document database by reprocessing all documents.
    Use this when SOP documents have been updated or added.
    WARNING: This operation is computationally expensive and time-consuming.
    Only use this tool in exceptional cases when the SOP database needs to be updated.
    
    Returns:
        Dictionary containing the refresh operation status
    """
    logger.info("🔧 Called tool: refresh_sop_database")
    
    global is_initialized
    
    try:
        logger.info("Starting SOP database refresh...")
        
        # Clear existing collection
        document_searcher.clear_collection()
        
        # Process all documents
        documents = document_processor.scan_sop_documents()
        
        if not documents:
            return {
                "success": False,
                "error": "No documents found to process"
            }
        
        # Add documents to search index
        success = document_searcher.add_documents(documents)
        
        if success:
            stats = document_searcher.get_collection_stats()
            is_initialized = True
            
            return {
                "success": True,
                "message": "SOP database refreshed successfully",
                "documents_processed": len(documents),
                "collection_stats": stats
            }
        else:
            return {
                "success": False,
                "error": "Failed to add documents to search index"
            }
        
    except Exception as e:
        logger.error(f"Error refreshing SOP database: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def get_server_status() -> Dict[str, Any]:
    """
    Get the current status of the SOP server.
    
    Returns:
        Dictionary containing server status and statistics
    """
    logger.info("🔧 Called tool: get_server_status")
    
    try:
        stats = document_searcher.get_collection_stats()
        categories = document_processor.get_sop_categories()
        
        return {
            "success": True,
            "server_status": "running",
            "initialized": is_initialized,
            "sop_directory": "sop_documents",
            "available_categories": categories,
            "collection_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting server status: {e}")
        return {
            "success": False,
            "error": str(e)
        }
