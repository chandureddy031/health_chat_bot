import os
import pickle
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import faiss
from backend.logger import get_logger

logger = get_logger("Embeddings")

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", store_dir: str = "backend/vector_store"):
        """
        Initialize vector store with sentence transformer
        
        Args:
            model_name: Name of the sentence transformer model
            store_dir: Directory to store vector index
        """
        self.store_dir = store_dir
        os.makedirs(store_dir, exist_ok=True)
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        
        # Try to load existing index
        self.load_index()
    
    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Create embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings
        """
        logger.info(f"Creating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def add_documents(self, chunks: List[Dict[str, str]], user_id: str):
        """
        Add document chunks to vector store
        
        Args:
            chunks: List of chunk dictionaries
            user_id: User ID for ownership tracking
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.create_embeddings(texts)
        
        # Add user_id to chunks
        for chunk in chunks:
            chunk["user_id"] = user_id
        
        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))
        self.chunks.extend(chunks)
        
        logger.info(f"Added {len(chunks)} chunks to vector store")
        self.save_index()
    
    def search(self, query: str, user_id: str, k: int = 5) -> List[Dict]:
        """
        Search for similar chunks
        
        Args:
            query: Search query
            user_id: User ID to filter results
            k: Number of results to return
            
        Returns:
            List of matching chunks with scores
        """
        if len(self.chunks) == 0:
            logger.warning("No documents in vector store")
            return []
        
        # Create query embedding
        query_embedding = self.model.encode([query])
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), k * 3)
        
        # Filter by user_id and get top k
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx].copy()
                if chunk.get("user_id") == user_id:
                    chunk["score"] = float(distance)
                    results.append(chunk)
                    if len(results) >= k:
                        break
        
        logger.info(f"Found {len(results)} matching chunks for query")
        return results
    
    def delete_user_documents(self, user_id: str, filename: str = None):
        """
        Delete documents for a user
        
        Args:
            user_id: User ID
            filename: Optional specific file to delete
        """
        # Filter out chunks
        if filename:
            self.chunks = [c for c in self.chunks if not (c.get("user_id") == user_id and c.get("source") == filename)]
        else:
            self.chunks = [c for c in self.chunks if c.get("user_id") != user_id]
        
        # Rebuild index
        if len(self.chunks) > 0:
            texts = [chunk["text"] for chunk in self.chunks]
            embeddings = self.create_embeddings(texts)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings.astype('float32'))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
        
        self.save_index()
        logger.info(f"Deleted documents for user {user_id}")
    
    def save_index(self):
        """Save FAISS index and chunks to disk"""
        try:
            index_path = os.path.join(self.store_dir, "faiss_index.bin")
            chunks_path = os.path.join(self.store_dir, "chunks.pkl")
            
            faiss.write_index(self.index, index_path)
            
            with open(chunks_path, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            logger.info("Vector store saved to disk")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self):
        """Load FAISS index and chunks from disk"""
        try:
            index_path = os.path.join(self.store_dir, "faiss_index.bin")
            chunks_path = os.path.join(self.store_dir, "chunks.pkl")
            
            if os.path.exists(index_path) and os.path.exists(chunks_path):
                self.index = faiss.read_index(index_path)
                
                with open(chunks_path, 'rb') as f:
                    self.chunks = pickle.load(f)
                
                logger.info(f"Loaded {len(self.chunks)} chunks from disk")
        except Exception as e:
            logger.warning(f"Could not load existing index: {e}")