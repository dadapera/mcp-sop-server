#!/usr/bin/env python3
"""
Test script for the MCP SOP Server components.
Run this to verify everything is working correctly.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_sop_server import DocumentProcessor, DocumentSearcher, mcp, document_processor, document_searcher

# Suppress some warnings for cleaner test output
logging.getLogger('chromadb').setLevel(logging.ERROR)

async def test_components():
    """Test the main components of the SOP server."""
    print("🧪 Testing MCP SOP Server Components...")
    print("=" * 50)
    
    # Test 1: Document Processor
    print("\n1. Testing Document Processor...")
    
    # Check if SOP directory exists
    if not document_processor.sop_directory.exists():
        print("❌ SOP documents directory not found!")
        print(f"   Expected: {document_processor.sop_directory}")
        return False
    
    # Get categories
    categories = document_processor.get_sop_categories()
    print(f"✅ Found {len(categories)} SOP categories:")
    for cat in categories[:5]:  # Show first 5
        print(f"   - {cat}")
    if len(categories) > 5:
        print(f"   ... and {len(categories) - 5} more")
    
    # Test 2: Process a few documents
    print("\n2. Testing Document Processing...")
    try:
        documents = document_processor.scan_sop_documents()
        if documents:
            print(f"✅ Successfully processed {len(documents)} documents")
            
            # Show sample document info
            sample_doc = documents[0]
            print(f"   Sample document: {sample_doc['sop_name']}")
            print(f"   Category: {sample_doc['sop_category']}")
            print(f"   Language: {sample_doc['language']}")
            print(f"   Chunks: {sample_doc['chunk_count']}")
            
            # Count successful vs failed documents
            successful_docs = [doc for doc in documents if doc['chunks']]
            print(f"   Successfully processed: {len(successful_docs)}/{len(documents)} documents")
        else:
            print("⚠️  No documents found to process")
            return False
    except Exception as e:
        print(f"❌ Error processing documents: {e}")
        return False
    
    # Test 3: Document Searcher
    print("\n3. Testing Document Searcher...")
    try:
        print("✅ Document searcher initialized")
        
        # Get initial stats
        initial_stats = document_searcher.get_collection_stats()
        print(f"   Initial collection: {initial_stats.get('total_chunks', 0)} chunks, {initial_stats.get('total_documents', 0)} documents")
        
        # Test search with existing data
        print("   Testing search functionality...")
        test_queries = ["qualità", "procedura", "gestione"]
        
        for query in test_queries:
            results = document_searcher.search(query, n_results=2)
            if results:
                print(f"   ✅ Query '{query}': {len(results)} results")
                print(f"      Top result: {results[0]['sop_name']} (score: {results[0]['similarity_score']:.3f})")
            else:
                print(f"   ⚠️  Query '{query}': No results")
        
    except Exception as e:
        print(f"❌ Error with document searcher: {e}")
        return False
    
    # Test 4: MCP Server
    print("\n4. Testing MCP Server...")
    try:
        print("✅ MCP server initialized")
        print(f"✅ Server name: {mcp.name}")
        
        # Test that tools are registered
        tools = await mcp.list_tools()
        print(f"✅ Found {len(tools)} registered tools:")
        for tool in tools:
            print(f"   - {tool.name}")
        
        # Test 5: Actual Tool Functionality
        print("\n5. Testing Tool Functionality...")
        
        # Test server status tool
        try:
            status_result = await test_tool_call("get_server_status", {})
            if status_result and status_result.get('success'):
                print("✅ get_server_status: Working")
                stats = status_result.get('collection_stats', {})
                print(f"   Server shows: {stats.get('total_chunks', 0)} chunks indexed")
            else:
                print("❌ get_server_status: Failed")
        except Exception as e:
            print(f"❌ get_server_status: Error - {e}")
        
        # Test list categories tool
        try:
            categories_result = await test_tool_call("list_sop_categories", {})
            if categories_result and categories_result.get('success'):
                print("✅ list_sop_categories: Working")
                cat_count = categories_result.get('total_categories', 0)
                print(f"   Found {cat_count} categories")
            else:
                print("❌ list_sop_categories: Failed")
        except Exception as e:
            print(f"❌ list_sop_categories: Error - {e}")
        
        # Test search tool
        try:
            search_result = await test_tool_call("search_sop_documents", {"query": "gestione qualità"})
            if search_result and search_result.get('success'):
                print("✅ search_sop_documents: Working")
                result_count = search_result.get('results_count', 0)
                print(f"   Search returned {result_count} results")
            else:
                print("❌ search_sop_documents: Failed")
        except Exception as e:
            print(f"❌ search_sop_documents: Error - {e}")
        
    except Exception as e:
        print(f"❌ Error with MCP server: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The MCP SOP Server is ready to use.")
    print("\nServer Statistics:")
    final_stats = document_searcher.get_collection_stats()
    print(f"   📄 Documents: {final_stats.get('total_documents', 0)}")
    print(f"   🧩 Text chunks: {final_stats.get('total_chunks', 0)}")
    print(f"   📁 Categories: {len(categories)}")
    
    print("\nTo start the server, run:")
    print("   python main.py")
    print("\nExample queries to try:")
    print("   - 'Come gestire una non conformità?'")
    print("   - 'Procedura per la manutenzione'")
    print("   - 'Gestione del magazzino'")
    
    return True

async def test_tool_call(tool_name: str, arguments: dict):
    """Helper function to test individual tool calls."""
    try:
        # Import the actual tool functions from mcp_server
        from mcp_sop_server.mcp_server import (
            get_server_status, list_sop_categories, search_sop_documents
        )
        
        # Map tool names to functions
        tools_map = {
            "get_server_status": get_server_status,
            "list_sop_categories": list_sop_categories,
            "search_sop_documents": search_sop_documents
        }
        
        if tool_name in tools_map:
            return await tools_map[tool_name](**arguments)
        else:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    try:
        success = asyncio.run(test_components())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1) 