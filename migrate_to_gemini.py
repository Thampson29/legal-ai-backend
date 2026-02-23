"""
Migration Script: OpenAI ChromaDB to Gemini ChromaDB
This script migrates the existing vector database from OpenAI embeddings to Google Gemini embeddings.
"""

import os
import sys
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configuration
OLD_DB_PATH = "lawglance/chroma_db_legal_bot_part1"
NEW_DB_PATH = "chroma_db_gemini"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def migrate_database():
    """Migrate from OpenAI embeddings to Gemini embeddings."""
    
    print("=" * 60)
    print("ChromaDB Migration: OpenAI to Gemini")
    print("=" * 60)
    print()
    
    # Validate API key
    if not GOOGLE_API_KEY:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Check if old database exists
    if not os.path.exists(OLD_DB_PATH):
        print(f"❌ Error: Source database not found at: {OLD_DB_PATH}")
        sys.exit(1)
    
    print(f"📂 Source database: {OLD_DB_PATH}")
    print(f"📂 Target database: {NEW_DB_PATH}")
    print()
    
    try:
        # Step 1: Load old ChromaDB and extract documents
        print("Step 1: Loading existing ChromaDB...")
        client = chromadb.PersistentClient(
            path=OLD_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get the collection
        collections = client.list_collections()
        if not collections:
            print("❌ Error: No collections found in the database")
            sys.exit(1)
        
        collection = collections[0]
        print(f"✓ Found collection: {collection.name}")
        
        # Get all documents from the collection
        print("Step 2: Extracting documents...")
        result = collection.get(include=['documents', 'metadatas'])
        
        if not result['documents']:
            print("❌ Error: No documents found in the collection")
            sys.exit(1)
        
        # Create Document objects
        documents = []
        for doc_text, metadata in zip(result['documents'], result['metadatas']):
            if metadata is None:
                metadata = {}
            documents.append(Document(
                page_content=doc_text,
                metadata=metadata
            ))
        
        print(f"✓ Extracted {len(documents)} documents")
        print()
        
        # Step 3: Initialize Gemini embeddings
        print("Step 3: Initializing Google Gemini embeddings...")
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
        print("✓ Gemini embeddings initialized")
        print()
        
        # Step 4: Create new ChromaDB with Gemini embeddings
        print("Step 4: Creating new ChromaDB with Gemini embeddings...")
        
        # Create directory if it doesn't exist
        os.makedirs(NEW_DB_PATH, exist_ok=True)
        
        # Initialize new vector store
        new_vector_store = Chroma(
            persist_directory=NEW_DB_PATH,
            embedding_function=embeddings
        )
        
        print("✓ New vector store created")
        print()
        
        # Step 5: Add documents in batches
        print("Step 5: Adding documents to new database...")
        batch_size = 50  # Process in smaller batches to avoid rate limits
        
        for i in tqdm(range(0, len(documents), batch_size), desc="Migrating"):
            batch = documents[i:i + batch_size]
            new_vector_store.add_documents(batch)
        
        print()
        print("✓ All documents migrated successfully")
        print()
        
        # Step 6: Verify migration
        print("Step 6: Verifying migration...")
        # Test a simple query
        test_results = new_vector_store.similarity_search("constitution", k=1)
        if test_results:
            print(f"✓ Verification successful! Found {len(test_results)} results for test query")
        else:
            print("⚠️ Warning: Test query returned no results")
        
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print()
        print(f"📊 Summary:")
        print(f"   - Documents migrated: {len(documents)}")
        print(f"   - New database location: {NEW_DB_PATH}")
        print(f"   - Embedding model: text-embedding-004 (Gemini)")
        print()
        print("🚀 You can now start the backend server:")
        print("   uvicorn app.main:app --reload")
        print()
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()
