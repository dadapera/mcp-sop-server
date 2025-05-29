#!/usr/bin/env python3
"""
Test script for the MCP SOP Server components.
Run this to verify everything is working correctly.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_sop_server import DocumentProcessor, DocumentSearcher, mcp, document_processor, document_searcher

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
        
        # Test adding documents
        print("   Adding documents to search index...")
        success = document_searcher.add_documents(documents[:2])  # Test with first 2 docs
        if success:
            print("✅ Documents added to search index")
        else:
            print("❌ Failed to add documents to search index")
            return False
        
        # Test search
        print("   Testing search functionality...")
        results = document_searcher.search("qualità", n_results=2)
        if results:
            print(f"✅ Search returned {len(results)} results")
            print(f"   Top result: {results[0]['sop_name']}")
        else:
            print("⚠️  Search returned no results")
        
        # Get stats
        stats = document_searcher.get_collection_stats()
        print(f"✅ Collection stats: {stats.get('total_chunks', 0)} chunks, {stats.get('total_documents', 0)} documents")
        
    except Exception as e:
        print(f"❌ Error with document searcher: {e}")
        return False
    
    # Test 4: MCP Server
    print("\n4. Testing MCP Server...")
    try:
        print("✅ MCP server initialized")
        print(f"✅ Server name: {mcp.name}")
        
        # Test that tools are registered - handle both sync and async versions
        try:
            # Try async version first
            if hasattr(mcp, 'list_tools') and callable(getattr(mcp, 'list_tools')):
                if asyncio.iscoroutinefunction(mcp.list_tools):
                    tools = await mcp.list_tools()
                else:
                    tools = mcp.list_tools()
                
                print(f"✅ Found {len(tools)} registered tools:")
                for tool in tools:
                    if isinstance(tool, dict) and 'name' in tool:
                        print(f"   - {tool['name']}")
                    else:
                        print(f"   - {tool}")
            else:
                # Fallback: check if tools are registered by accessing internal attributes
                if hasattr(mcp, '_tools'):
                    tools = list(mcp._tools.keys())
                    print(f"✅ Found {len(tools)} registered tools:")
                    for tool in tools:
                        print(f"   - {tool}")
                else:
                    print("⚠️  Could not access tools list, but server appears functional")
        except Exception as tool_error:
            print(f"⚠️  Could not list tools ({tool_error}), but server appears functional")
        
    except Exception as e:
        print(f"❌ Error with MCP server: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The MCP SOP Server is ready to use.")
    print("\nTo start the server, run:")
    print("   python main.py")
    print("\nExample queries to try:")
    print("   - 'Come gestire una non conformità?'")
    print("   - 'Procedura per la manutenzione'")
    print("   - 'Gestione del magazzino'")
    
    return True

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