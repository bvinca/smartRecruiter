"""
RAG Retriever - Retrieve context from database/job posts
"""
from typing import List, Dict, Any, Optional
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '../../backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Make langchain optional
try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import Chroma
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    OpenAIEmbeddings = None
    Chroma = None
    Document = None

from app.config import settings


class RAGRetriever:
    """Retrieve relevant context for RAG"""
    
    def __init__(self):
        self.use_langchain = LANGCHAIN_AVAILABLE
        self.vectorstore = None
        
        if self.use_langchain:
            try:
                # Try both parameter names for compatibility
                try:
                    self.embeddings = OpenAIEmbeddings(
                        api_key=settings.OPENAI_API_KEY
                    )
                except TypeError:
                    # Fallback to older parameter name
                    self.embeddings = OpenAIEmbeddings(
                        openai_api_key=settings.OPENAI_API_KEY
                    )
                persist_directory = settings.CHROMA_PERSIST_DIR
                os.makedirs(persist_directory, exist_ok=True)
            except Exception as e:
                print(f"Warning: Could not initialize LangChain embeddings: {e}")
                self.use_langchain = False
    
    def initialize_vectorstore(self, documents: List[Dict[str, Any]]):
        """Initialize vector store with documents"""
        if not self.use_langchain:
            return
        
        if not documents:
            return
        
        try:
            # Convert documents to LangChain format
            langchain_docs = []
            for doc in documents:
                if Document:
                    langchain_docs.append(Document(
                        page_content=doc.get("content", ""),
                        metadata=doc.get("metadata", {})
                    ))
            
            self.vectorstore = Chroma.from_documents(
                documents=langchain_docs,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR
            )
        except Exception as e:
            print(f"Warning: Could not initialize vector store: {e}")
    
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: Search query
            k: Number of results to retrieve
        
        Returns:
            List of relevant text chunks
        """
        if not self.vectorstore:
            return []
        
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return []

