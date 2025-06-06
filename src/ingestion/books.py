"""
Book ingestion module for processing investing books and literature.

This module handles:
- PDF parsing and text extraction from investing books
- Text chunking and preprocessing
- Metadata extraction (author, title, publication date)
- Vector embedding generation for knowledge base
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import yaml

from ..utils.pdf_utils import extract_text_from_pdf, chunk_text
from ..utils.logger import get_logger
from ..embedding.embedder import VectorStore

logger = get_logger(__name__)


class BookIngester:
    """Handles ingestion of investing books into the knowledge base."""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the book ingester with configuration."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.books_dir = Path(self.config['storage']['books_dir'])
        self.vector_store = VectorStore(self.config['vector_db'])
        
    def ingest_book(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Ingest a single book into the knowledge base.
        
        Args:
            file_path: Path to the book file (PDF, TXT, etc.)
            metadata: Optional metadata about the book
            
        Returns:
            bool: True if ingestion successful, False otherwise
        """
        try:
            logger.info(f"Starting ingestion of book: {file_path}")
            
            # Extract text from book
            text = self._extract_text(file_path)
            
            # Chunk the text
            chunks = self._chunk_text(text)
            
            # Generate embeddings and store
            self._store_chunks(chunks, file_path, metadata)
            
            logger.info(f"Successfully ingested book: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest book {file_path}: {str(e)}")
            return False
    
    def ingest_books_from_directory(self, directory: str) -> List[str]:
        """
        Ingest all books from a directory.
        
        Args:
            directory: Path to directory containing books
            
        Returns:
            List of successfully processed files
        """
        processed_files = []
        book_dir = Path(directory)
        
        for file_path in book_dir.glob("*.pdf"):
            if self.ingest_book(str(file_path)):
                processed_files.append(str(file_path))
                
        return processed_files
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from book file based on format."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks for embedding."""
        return chunk_text(
            text,
            chunk_size=self.config['embedding']['chunk_size'],
            overlap=self.config['embedding']['chunk_overlap']
        )
    
    def _store_chunks(self, chunks: List[str], source_file: str, metadata: Optional[Dict] = None):
        """Store text chunks in vector database."""
        # TODO: Implement vector storage logic
        pass


def list_available_books(books_dir: str = "data/books") -> List[Dict[str, str]]:
    """
    List all available books in the books directory.
    
    Returns:
        List of book information dictionaries
    """
    books = []
    book_path = Path(books_dir)
    
    for file_path in book_path.glob("*.pdf"):
        books.append({
            'filename': file_path.name,
            'path': str(file_path),
            'size_mb': file_path.stat().st_size / (1024 * 1024)
        })
    
    return books


def get_book_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a book file.
    
    Args:
        file_path: Path to the book file
        
    Returns:
        Dictionary containing book metadata
    """
    # TODO: Implement metadata extraction
    # This could include author, title, publication date, etc.
    return {
        'filename': Path(file_path).name,
        'file_size': os.path.getsize(file_path),
        'file_type': Path(file_path).suffix
    }
