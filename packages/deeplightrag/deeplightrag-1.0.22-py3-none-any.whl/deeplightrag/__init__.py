"""
DeepLightRAG: High-performance Document Indexing and Retrieval System

Simple API for document indexing and retrieval. Use with any LLM for generation.

Usage:
    from deeplightrag import DeepLightRAG
    
    # Initialize
    rag = DeepLightRAG()
    
    # Index a document
    rag.index_document("document.pdf")
    
    # Retrieve context for a query
    result = rag.retrieve("What is the main topic?")
    print(result["context"])  # Use with your LLM
"""

__version__ = "1.0.21"
__author__ = "DeepLightRAG Team"

from .core import DeepLightRAG

__all__ = [
    "__version__",
    "__author__",
    "DeepLightRAG",
]
