"""
Legal AI Backend - FastAPI Application
A production-ready backend service for legal awareness and information retrieval.
"""

import os
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from app.vectorstore import get_vector_store_manager, VectorStoreManager
from app.rag import get_rag_system, LegalRAGSystem

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
vector_store_manager: Optional[VectorStoreManager] = None
rag_system: Optional[LegalRAGSystem] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Initialize vector store and RAG system
    global vector_store_manager, rag_system
    
    try:
        logger.info("Initializing Legal AI Backend...")
        
        # Validate environment variables
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        # Initialize vector store
        logger.info("Loading vector store...")
        vector_store_manager = get_vector_store_manager()
        
        # Initialize RAG system
        logger.info("Initializing RAG system...")
        rag_system = get_rag_system(vector_store_manager)
        
        logger.info("Legal AI Backend initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize backend: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Cleanup if needed
    logger.info("Shutting down Legal AI Backend...")


# Create FastAPI application
app = FastAPI(
    title="Legal AI Backend",
    description="A production-ready backend service for legal awareness and information retrieval using RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Legal question or query from the user"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean the query string."""
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be empty or just whitespace")
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "What are the fundamental rights guaranteed by the Indian Constitution?"
                }
            ]
        }
    }


class Citation(BaseModel):
    """Citation information for a source."""
    source_title: str = Field(..., description="Title of the source document")
    source: str = Field(..., description="Source identifier or filename")
    snippet: str = Field(..., description="Relevant excerpt from the source")
    section: Optional[str] = Field(None, description="Section number if applicable")
    page: Optional[str] = Field(None, description="Page number if applicable")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str = Field(..., description="Generated answer with legal disclaimer")
    citations: list[Citation] = Field(
        default_factory=list,
        description="List of source citations used to generate the answer"
    )
    has_context: bool = Field(
        ...,
        description="Whether sufficient context was found in the knowledge base"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "answer": "The Indian Constitution guarantees fundamental rights...\n\n**Disclaimer:** This is general legal information, not legal advice.",
                    "citations": [
                        {
                            "source_title": "Constitution of India",
                            "source": "constitution.pdf",
                            "snippet": "Part III of the Constitution deals with Fundamental Rights...",
                            "section": "Article 12-35"
                        }
                    ],
                    "has_context": True
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    vector_store_loaded: bool


# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Legal AI Backend",
        "version": "1.0.0",
        "description": "A production-ready backend service for legal awareness",
        "endpoints": {
            "POST /chat": "Process legal queries and get answers with citations",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns:
        Service health status and component availability
    """
    vector_store_loaded = vector_store_manager is not None and vector_store_manager.vector_store is not None
    
    if not vector_store_loaded:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "message": "Vector store not loaded",
                "vector_store_loaded": False
            }
        )
    
    return HealthResponse(
        status="healthy",
        message="Legal AI Backend is running",
        vector_store_loaded=True
    )


@app.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Process a legal query and return an answer with citations.
    
    This endpoint:
    1. Validates the user query
    2. Retrieves relevant legal context from the vector database
    3. Generates an answer using the RAG system
    4. Returns the answer with citations and a legal disclaimer
    5. Handles safety checks for illegal queries
    
    Args:
        request: ChatRequest containing the user's query
        
    Returns:
        ChatResponse with answer, citations, and metadata
        
    Raises:
        HTTPException: If the service is not initialized or an error occurs
    """
    # Verify system is initialized
    if not rag_system:
        logger.error("RAG system not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is not ready. Please try again in a moment."
        )
    
    try:
        logger.info(f"Processing query: {request.query[:50]}...")
        
        # Process query through RAG system
        result = rag_system.process_query(request.query)
        
        # Convert to response model
        response = ChatResponse(
            answer=result["answer"],
            citations=[Citation(**citation) for citation in result["citations"]],
            has_context=result["has_context"]
        )
        
        logger.info("Query processed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your query. Please try again."
        )


# Error handlers

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal error occurred. Please try again later."}
    )


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "False").lower() == "true"
    )
