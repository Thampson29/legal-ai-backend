"""
RAG (Retrieval-Augmented Generation) Module
Handles legal query processing with context retrieval and LLM-based answer generation.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Legal disclaimer to be included with every response
LEGAL_DISCLAIMER = "\n\n**Disclaimer:** This is general legal information, not legal advice."

# System prompt for the legal AI assistant
SYSTEM_PROMPT = """You are Lawglance, an advanced legal AI assistant designed to provide precise legal awareness and information.

**Your Core Purpose:**
- Provide legal awareness and democratize access to legal information
- Help users understand their legal rights and obligations
- Answer ONLY based on the provided context
- Be helpful, accurate, and educational

**Current Legal Knowledge Domains:**
- Indian Constitution
- Bharatiya Nyaya Sanhita, 2023 (BNS)
- Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)
- Bharatiya Sakshya Adhiniyam, 2023 (BSA)
- Consumer Protection Act, 2019
- Motor Vehicles Act, 1988
- Information Technology Act, 2000
- The Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013
- The Protection of Children from Sexual Offences Act, 2012

**Strict Guidelines:**
1. Answer ONLY from the provided context below
2. If the context doesn't contain sufficient information, respond with:
   "I don't have enough verified information in my knowledge base to answer that precisely."
3. NEVER make up legal section numbers or citations
4. NEVER provide guidance on illegal activities
5. Always cite specific legal provisions from the context when possible
6. Keep responses clear, concise, and accurate
7. Maintain a helpful and educational tone

**Safety Protocol:**
If a user asks for help with illegal activities (e.g., evading law, committing crimes), respond with:
"I cannot provide guidance on illegal activities. If you have questions about legal compliance or your rights, I'm happy to help with that instead."

---

**Retrieved Legal Context:**
{context}

---

**User Question:**
{question}

**Your Response (include relevant citations from the context):**"""


# Illegal keywords that trigger safety protocol
ILLEGAL_KEYWORDS = [
    "evade", "avoid arrest", "hide crime", "commit fraud", "forge", 
    "illegal drug", "smuggle", "bribe", "money laundering", "tax evasion",
    "hack", "break law", "get away with", "cover up crime"
]


class LegalRAGSystem:
    """
    Legal RAG system for processing queries and generating contextual answers.
    
    Uses retrieval-augmented generation to answer legal queries based on
    vectorized legal documents stored in ChromaDB.
    """
    
    def __init__(self, vector_store_manager, llm_model: str = "models/gemini-2.5-flash", temperature: float = 0.3):
        """
        Initialize the RAG system.
        
        Args:
            vector_store_manager: VectorStoreManager instance
            llm_model: Google Gemini model name
            temperature: LLM temperature for response generation (lower = more focused)
        """
        self.vector_store_manager = vector_store_manager
        self.llm_model = llm_model
        self.temperature = temperature
        
        # Initialize LLM
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.llm = ChatGoogleGenerativeAI(
            model=self.llm_model,
            temperature=self.temperature,
            google_api_key=google_api_key
        )
        
        # Create prompt template
        self.prompt_template = ChatPromptTemplate.from_template(SYSTEM_PROMPT)
        
        logger.info(f"RAG system initialized with model: {self.llm_model}")
    
    def _is_illegal_query(self, query: str) -> bool:
        """
        Check if the query contains requests for illegal guidance.
        
        Args:
            query: User query string
            
        Returns:
            True if query appears to request illegal guidance
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in ILLEGAL_KEYWORDS)
    
    def _extract_citations(self, documents: List[Document]) -> List[Dict[str, str]]:
        """
        Extract citations from retrieved documents.
        
        Args:
            documents: List of retrieved Document objects
            
        Returns:
            List of citation dictionaries with source information
        """
        citations = []
        seen_sources = set()
        
        for doc in documents:
            metadata = doc.metadata
            content_snippet = doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content
            
            # Extract source information from metadata
            source = metadata.get("source", "Unknown Source")
            
            # Create a unique identifier to avoid duplicate citations
            source_id = f"{source}_{content_snippet[:50]}"
            
            if source_id not in seen_sources:
                citation = {
                    "source_title": metadata.get("title", source),
                    "source": source,
                    "snippet": content_snippet
                }
                
                # Add additional metadata if available
                if "section" in metadata:
                    citation["section"] = metadata["section"]
                if "page" in metadata:
                    citation["page"] = str(metadata["page"])
                
                citations.append(citation)
                seen_sources.add(source_id)
        
        return citations
    
    def _retrieve_context(self, query: str, k: int = 10) -> tuple[str, List[Document]]:
        """
        Retrieve relevant context for the query.
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            Tuple of (formatted context string, list of documents)
        """
        try:
            # Get retriever
            retriever = self.vector_store_manager.get_retriever(k=k, score_threshold=0.3)
            
            # Retrieve relevant documents
            documents = retriever.invoke(query)
            
            if not documents:
                logger.warning(f"No relevant documents found for query: {query[:50]}...")
                return "", []
            
            # Format context from documents
            context_parts = []
            for i, doc in enumerate(documents, 1):
                source = doc.metadata.get("source", "Unknown")
                context_parts.append(f"[Source {i}: {source}]\n{doc.page_content}\n")
            
            context = "\n---\n".join(context_parts)
            
            logger.info(f"Retrieved {len(documents)} documents for query")
            return context, documents
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            raise
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a legal query and generate an answer with citations.
        
        Args:
            query: User's legal question
            
        Returns:
            Dictionary containing:
            - answer: Generated answer with disclaimer
            - citations: List of source citations
            - has_context: Whether relevant context was found
        """
        try:
            # Safety check for illegal queries
            if self._is_illegal_query(query):
                logger.warning(f"Illegal query detected: {query[:50]}...")
                return {
                    "answer": "I cannot provide guidance on illegal activities. If you have questions about legal compliance or your rights, I'm happy to help with that instead." + LEGAL_DISCLAIMER,
                    "citations": [],
                    "has_context": False
                }
            
            # Retrieve relevant context
            context, documents = self._retrieve_context(query)
            
            # If no context found, query LLM directly without RAG
            if not context or not documents:
                logger.warning("No context found, querying LLM directly...")
                fallback_prompt = f"""You are a helpful legal AI assistant. Answer the following question to the best of your ability:

Question: {query}

Provide a clear and accurate answer."""
                
                response = self.llm.invoke(fallback_prompt)
                answer = response.content + LEGAL_DISCLAIMER
                
                return {
                    "answer": answer,
                    "citations": [],
                    "has_context": False
                }
            
            # Generate answer using LLM with retrieved context
            prompt = self.prompt_template.format(context=context, question=query)
            
            logger.info("Generating answer with LLM...")
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Check if LLM couldn't answer from context, fallback to direct query
            if "don't have enough" in answer.lower() or "insufficient information" in answer.lower():
                logger.warning("RAG response insufficient, querying LLM directly...")
                fallback_prompt = f"""You are a helpful legal AI assistant. Answer the following question to the best of your ability:

Question: {query}

Provide a clear and accurate answer."""
                
                response = self.llm.invoke(fallback_prompt)
                answer = response.content
            
            # Add legal disclaimer
            answer_with_disclaimer = answer + LEGAL_DISCLAIMER
            
            logger.info("Query processed successfully")
            
            return {
                "answer": answer_with_disclaimer,
                "citations": [],
                "has_context": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise


# Global RAG system instance
_rag_system: Optional[LegalRAGSystem] = None


def get_rag_system(vector_store_manager) -> LegalRAGSystem:
    """
    Get or create the global RAG system instance.
    
    Args:
        vector_store_manager: VectorStoreManager instance
        
    Returns:
        LegalRAGSystem instance
    """
    global _rag_system
    if _rag_system is None:
        _rag_system = LegalRAGSystem(vector_store_manager)
    return _rag_system
