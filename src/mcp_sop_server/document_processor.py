import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
from docx import Document
from langdetect import detect
import re

class DocumentProcessor:
    """
    Processes SOP documents (PDF, DOCX) and extracts text content
    with support for Italian language documents.
    """
    
    def __init__(self, sop_directory: str = "sop_documents"):
        self.sop_directory = Path(sop_directory)
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {'.pdf', '.docx', '.doc'}
        
    def extract_text_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove special characters but keep Italian accents
        text = re.sub(r'[^\w\sàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ.,;:!?()-]', '', text)
        
        return text
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks for better retrieval."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document and return metadata with text chunks."""
        try:
            # Extract text based on file extension
            if file_path.suffix.lower() == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_path.suffix.lower() in ['.docx', '.doc']:
                text = self.extract_text_from_docx(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {file_path}")
                return None
            
            if not text:
                self.logger.warning(f"No text extracted from {file_path}")
                return None
            
            # Clean text
            cleaned_text = self.clean_text(text)
            
            # Detect language (should be Italian)
            try:
                language = detect(cleaned_text[:1000])  # Use first 1000 chars for detection
            except:
                language = "unknown"
            
            # Create chunks
            chunks = self.chunk_text(cleaned_text)
            
            # Extract SOP metadata from path
            sop_category = file_path.parent.name
            sop_name = file_path.stem
            
            return {
                'file_path': str(file_path),
                'sop_category': sop_category,
                'sop_name': sop_name,
                'language': language,
                'full_text': cleaned_text,
                'chunks': chunks,
                'chunk_count': len(chunks),
                'file_size': file_path.stat().st_size,
                'last_modified': file_path.stat().st_mtime
            }
            
        except Exception as e:
            self.logger.error(f"Error processing document {file_path}: {e}")
            return None
    
    def scan_sop_documents(self) -> List[Dict[str, Any]]:
        """Scan the SOP directory and process all documents."""
        documents = []
        
        if not self.sop_directory.exists():
            self.logger.error(f"SOP directory not found: {self.sop_directory}")
            return documents
        
        # Recursively find all supported documents
        for file_path in self.sop_directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                self.logger.info(f"📄 Processing: {file_path}")
                doc_data = self.process_document(file_path)
                if doc_data:
                    documents.append(doc_data)
        
        self.logger.info(f"Processed {len(documents)} documents")
        return documents
    
    def get_sop_categories(self) -> List[str]:
        """Get list of available SOP categories."""
        categories = []
        if self.sop_directory.exists():
            for item in self.sop_directory.iterdir():
                if item.is_dir():
                    categories.append(item.name)
        return sorted(categories) 