import logging
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from pathlib import Path

class DocumentSearcher:
    """
    Handles semantic search of SOP documents using ChromaDB and Italian language embeddings.
    """
    
    def __init__(self, 
                 db_path: str = "chroma_db",
                 collection_name: str = "sop_documents",
                 model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize the document searcher.
        
        Args:
            db_path: Path to ChromaDB storage
            collection_name: Name of the ChromaDB collection
            model_name: Sentence transformer model (multilingual for Italian support)
        """
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.logger = logging.getLogger(__name__)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Load multilingual sentence transformer for Italian support
        self.logger.info(f"🤖 Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
    def _get_or_create_collection(self):
        """Get existing collection or create a new one."""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            self.logger.info(f"Using existing collection: {self.collection_name}")
        except:
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "SOP documents collection with Italian language support"}
            )
            self.logger.info(f"📚 Created new collection: {self.collection_name}")
        
        return collection
    
    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            return []
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add processed documents to the ChromaDB collection.
        
        Args:
            documents: List of processed document dictionaries
            
        Returns:
            bool: Success status
        """
        try:
            all_texts = []
            all_metadatas = []
            all_ids = []
            
            for doc in documents:
                for i, chunk in enumerate(doc['chunks']):
                    # Create unique ID for each chunk
                    chunk_id = f"{doc['sop_category']}_{doc['sop_name']}_chunk_{i}"
                    
                    # Prepare metadata
                    metadata = {
                        'sop_category': doc['sop_category'],
                        'sop_name': doc['sop_name'],
                        'file_path': doc['file_path'],
                        'language': doc['language'],
                        'chunk_index': i,
                        'total_chunks': doc['chunk_count'],
                        'file_size': doc['file_size'],
                        'last_modified': doc['last_modified']
                    }
                    
                    all_texts.append(chunk)
                    all_metadatas.append(metadata)
                    all_ids.append(chunk_id)
            
            if not all_texts:
                self.logger.warning("No texts to add to collection")
                return False
            
            # Generate embeddings
            self.logger.info(f"Generating embeddings for {len(all_texts)} text chunks...")
            embeddings = self._generate_embeddings(all_texts)
            
            if not embeddings:
                self.logger.error("Failed to generate embeddings")
                return False
            
            # Add to collection
            self.collection.add(
                documents=all_texts,
                metadatas=all_metadatas,
                ids=all_ids,
                embeddings=embeddings
            )
            
            self.logger.info(f"Successfully added {len(all_texts)} document chunks to collection")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding documents to collection: {e}")
            return False
    
    def search(self, 
               query: str, 
               n_results: int = 5,
               sop_category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant SOP documents based on query.
        
        Args:
            query: Search query in Italian or English
            n_results: Number of results to return
            sop_category: Optional filter by SOP category
            
        Returns:
            List of relevant document chunks with metadata
        """
        try:
            # Generate embedding for query
            query_embedding = self._generate_embeddings([query])[0]
            
            # Prepare where clause for filtering
            where_clause = None
            if sop_category:
                where_clause = {"sop_category": sop_category}
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    result = {
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'sop_category': results['metadatas'][0][i]['sop_category'],
                        'sop_name': results['metadatas'][0][i]['sop_name'],
                        'file_path': results['metadatas'][0][i]['file_path']
                    }
                    formatted_results.append(result)
            
            self.logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    def get_sop_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all SOPs in a specific category."""
        try:
            results = self.collection.get(
                where={"sop_category": category},
                include=['documents', 'metadatas']
            )
            
            # Group by SOP name to avoid duplicates
            sops = {}
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i]
                    sop_name = metadata['sop_name']
                    
                    if sop_name not in sops:
                        sops[sop_name] = {
                            'sop_name': sop_name,
                            'sop_category': metadata['sop_category'],
                            'file_path': metadata['file_path'],
                            'language': metadata['language'],
                            'total_chunks': metadata['total_chunks']
                        }
            
            return list(sops.values())
            
        except Exception as e:
            self.logger.error(f"Error getting SOPs by category {category}: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection."""
        try:
            count = self.collection.count()
            
            # Get all metadata to calculate stats
            results = self.collection.get(include=['metadatas'])
            
            categories = set()
            languages = set()
            sop_names = set()
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    categories.add(metadata['sop_category'])
                    languages.add(metadata['language'])
                    sop_names.add(metadata['sop_name'])
            
            return {
                'total_chunks': count,
                'total_documents': len(sop_names),
                'categories': sorted(list(categories)),
                'languages': sorted(list(languages)),
                'category_count': len(categories)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self._get_or_create_collection()
            self.logger.info("Collection cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing collection: {e}")
            return False 