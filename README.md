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

## Installation

1. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Verify SOP Documents**:
   Ensure your SOP documents are in the `sop_documents/` directory, organized by category folders.

## Usage

### Starting the Server

```bash
python main.py
```

The server will:

1. Scan all SOP documents in the `sop_documents/` directory
2. Process and extract text from PDF and DOCX files
3. Generate embeddings using the multilingual model
4. Store everything in ChromaDB for fast retrieval
5. Start the MCP server on stdio transport

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

## Document Structure

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

## Configuration

### Embedding Model

The server uses `paraphrase-multilingual-MiniLM-L12-v2` by default for Italian language support. You can change this in `document_searcher.py`:

```python
model_name = "sentence-transformers/your-preferred-model"
```

### Chunk Size

Text chunking can be adjusted in `document_processor.py`:

```python
def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200):
```

### Database Location

ChromaDB storage location can be configured in `document_searcher.py`:

```python
db_path = "your_custom_chroma_db_path"
```

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

### Logs

The server provides detailed logging. Check the console output for:

- Document processing status
- Embedding generation progress
- Search query results
- Error messages

## Development

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

Add new MCP tools by extending the `_register_tools()` method in `SOPServer`.

## License

This project is intended for internal company use for accessing SOP documentation.

## Support

For issues or questions about the SOP MCP server, please contact your IT department or the development team.
