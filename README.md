# MCP SOP Server

A Model Context Protocol (MCP) server for accessing and searching Standard Operating Procedures (SOPs) with Italian language support.

## Overview

This MCP server provides AI agents with the ability to:

- Search through your company's SOP documentation using semantic search
- Retrieve relevant procedures based on specific situations
- Browse SOPs by category
- Get guidance on what to do in specific scenarios

The server uses:

- **ChromaDB** for vector storage and semantic search
- **Sentence Transformers** with multilingual models for Italian language support
- **FastMCP** for the MCP server implementation
- **RAG (Retrieval Augmented Generation)** for intelligent document retrieval

## Features

- 🇮🇹 **Italian Language Support**: Uses multilingual embeddings optimized for Italian text
- 📄 **Multi-format Support**: Processes PDF and DOCX documents
- 🔍 **Semantic Search**: Find relevant SOPs based on meaning, not just keywords
- 📁 **Category Filtering**: Search within specific SOP categories
- 🤖 **AI-Ready**: Provides structured responses perfect for LLM consumption
- ⚡ **Fast Retrieval**: Efficient vector-based search with ChromaDB
- 🚀 **Lazy Initialization**: Server starts quickly, documents are indexed on first request

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/dadapera/mcp-sop-server.git
   cd mcp-sop-server
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Add your SOP documents**:
   Create a `sop_documents/` directory and organize your SOP files by category folders.

## Configuration

### MCP Client Setup

To use this server with Claude Desktop or other MCP clients, add it to your MCP client configuration:

**For Claude Desktop** (`mcp-client-config.json`):

```json
{
  "mcpServers": {
    "sop-server": {
      "command": "/path/to/your/venv/Scripts/python.exe",
      "args": ["/path/to/your/mcp-sop-server/main.py"],
      "cwd": "/path/to/your/mcp-sop-server"
    }
  }
}
```

> **Note**: Make sure to use the full path to your virtual environment's Python executable and adjust paths according to your system.

### Directory Structure

The server expects SOP documents to be organized as follows:

```
sop_documents/
├── SOP01 Quality System Documentation Management/
│   ├── document1.pdf
│   └── document2.docx
├── SOP02 HR management/
│   └── hr_procedures.pdf
├── SOP03 Design/
│   └── design_process.docx
└── ...
```

## Usage

### Starting the Server

The server is typically started automatically by your MCP client (like Claude Desktop). If running manually:

```bash
python main.py
```

**Note on entry points:**

This project provides two main Python scripts for running the server:
- `main.py`: This is the standard entry point, intended for use when the server is run in a remote/production environment.
- `main_local.py`: This script is configured for local development and local MCP clients.

The server will:

1. Start quickly and wait for connections
2. On first tool call: scan all SOP documents in the `sop_documents/` directory
3. Process and extract text from PDF and DOCX files
4. Generate embeddings using the multilingual model
5. Store everything in ChromaDB for fast retrieval

### Available Tools

The server provides the following MCP tools:

#### 1. `search_sop_documents`

Search for relevant SOP content using natural language queries.

**Parameters:**

- `query` (string): Search query in Italian or English
- `max_results` (int, optional): Maximum results to return (default: 5)
- `category` (string, optional): Filter by SOP category

**Example:**

```json
{
  "query": "Come gestire una non conformità nel processo di produzione",
  "max_results": 3,
  "category": "SOP05 Non Conformity"
}
```

#### 2. `get_sop_guidance`

Get specific guidance for a situation based on SOP documents.

**Parameters:**

- `situation` (string): Description of the situation
- `category` (string, optional): Focus search on specific category

**Example:**

```json
{
  "situation": "Un cliente ha segnalato un difetto nel prodotto consegnato",
  "category": "SOP05 Non Conformity"
}
```

#### 3. `list_sop_categories`

Get all available SOP categories and collection statistics.

#### 4. `get_sop_by_category`

Retrieve all SOPs within a specific category.

**Parameters:**

- `category` (string): SOP category name

#### 5. `refresh_sop_database`

Refresh the document database (use when SOPs are updated).

#### 6. `get_server_status`

Get current server status and statistics.

## Technical Configuration

### Embedding Model

The server uses `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` by default for Italian language support. You can change this in `src/mcp_sop_server/document_searcher.py`:

```python
model_name = "sentence-transformers/your-preferred-model"
```

### Chunk Size

Text chunking can be adjusted in `src/mcp_sop_server/document_processor.py`:

```python
def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200):
```

### Database Location

ChromaDB storage location is automatically set to `chroma_db/` in the project root.

## Example Queries

Here are some example queries you can use:

**Italian:**

- "Come gestire una non conformità?"
- "Procedura per la manutenzione dell'infrastruttura"
- "Cosa fare in caso di audit interno?"
- "Gestione del magazzino e inventario"

**English:**

- "How to handle quality issues?"
- "Software development lifecycle procedures"
- "Risk management protocols"
- "Employee training requirements"

## Troubleshooting

### Common Issues

1. **No documents found**: Ensure SOP documents are in the correct directory structure
2. **Embedding model download**: First run may take time to download the multilingual model
3. **Memory usage**: Large document collections may require more RAM for embedding generation
4. **Path issues**: Make sure to use absolute paths in your MCP client configuration

### Logs

The server provides detailed logging with emojis for better readability:

- 🚀 Server startup and initialization
- 📄 Document processing status
- 📊 Processing statistics
- ✅ Success messages
- ❌ Error messages

Check the console output or your MCP client logs for detailed information.

## Development

### Project Structure

```
mcp-sop-server/
├── src/mcp_sop_server/          # Main package
│   ├── __init__.py              # Package initialization
│   ├── mcp_server.py            # FastMCP server and tools
│   ├── document_processor.py    # Document text extraction
│   └── document_searcher.py     # Vector search with ChromaDB
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── test_server.py              # Server testing
├── mcp-client-config.json      # Example client configuration
└── README.md                   # This file
```

### Adding New Document Types

To support additional file formats, extend the `DocumentProcessor` class:

```python
def extract_text_from_new_format(self, file_path: Path) -> str:
    # Implementation for new format
    pass
```

### Custom Search Logic

Modify the `DocumentSearcher` class to implement custom search algorithms or filters.

### Additional Tools

Add new MCP tools by defining them with the `@mcp.tool()` decorator in `mcp_server.py`.

## License

This project is intended for internal company use for accessing SOP documentation.

## Support

For issues or questions about the SOP MCP server, please contact your IT department or create an issue on the GitHub repository.
