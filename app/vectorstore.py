"""
Vector Store Module for Legal AI Backend
Handles initialization and interaction with ChromaDB vector database.
"""

import os
import logging
from typing import Optional
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages the ChromaDB vector store for legal document retrieval.
    
    This class handles initialization of the vector database and provides
    methods to retrieve relevant legal context based on queries.
    """
    
    def __init__(self, persist_directory: str = None, google_api_key: str = None):
        """
        Initialize the vector store manager.
        
        Args:
            persist_directory: Path to the ChromaDB database directory
            google_api_key: Google API key for embeddings
        """
        self.persist_directory = persist_directory or os.getenv(
            "CHROMA_DB_PATH", 
            "chroma_db_gemini"
        )
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.embeddings = None
        self.vector_store = None
        self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the embeddings model and vector store."""
        try:
            logger.info("Initializing Google Gemini embeddings...")
            # Use gemini-embedding-001 model
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=self.google_api_key
            )
            
            logger.info(f"Loading ChromaDB from: {self.persist_directory}")
            
            # Create directory if it doesn't exist
            if not os.path.exists(self.persist_directory):
                logger.warning(f"ChromaDB directory not found. Creating new database at: {self.persist_directory}")
                os.makedirs(self.persist_directory, exist_ok=True)
            
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            logger.info("Vector store initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise
    
    def get_retriever(self, k: int = 10, score_threshold: float = 0.3):
        """
        Get a retriever configured for similarity search.
        
        Args:
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score threshold
            
        Returns:
            Configured retriever instance
        """
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized")
        
        return self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": k,
                "score_threshold": score_threshold
            }
        )
    
    def similarity_search(self, query: str, k: int = 10) -> list:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if not self.vector_store:
            raise RuntimeError("Vector store not initialized")
        
        try:
            documents = self.vector_store.similarity_search(query, k=k)
            return documents
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            raise


# Global vector store instance
_vector_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager() -> VectorStoreManager:
    """
    Get or create the global vector store manager instance.
    
    Returns:
        VectorStoreManager instance
    """
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
    return _vector_store_manager
