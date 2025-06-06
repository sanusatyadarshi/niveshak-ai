"""
PDF processing utilities for extracting text and tables from PDF documents.

This module provides functions for:
- Text extraction from PDF files
- Table extraction and parsing
- Text chunking and preprocessing
- PDF metadata extraction
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import re

# PDF processing libraries
try:
    import PyPDF2
    import pdfplumber
    import fitz  # PyMuPDF
    PDF_LIBRARIES_AVAILABLE = True
except ImportError:
    PDF_LIBRARIES_AVAILABLE = False

from .logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: str, method: str = "pdfplumber") -> str:
    """
    Extract text from a PDF file using specified method.
    
    Args:
        file_path: Path to the PDF file
        method: Extraction method ('pdfplumber', 'pypdf2', 'pymupdf')
        
    Returns:
        Extracted text as string
        
    Raises:
        ValueError: If PDF libraries are not available or method is unsupported
        FileNotFoundError: If file doesn't exist
    """
    if not PDF_LIBRARIES_AVAILABLE:
        raise ValueError("PDF processing libraries not available. Install with: pip install PyPDF2 pdfplumber PyMuPDF")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    
    logger.info(f"Extracting text from {file_path} using {method}")
    
    try:
        if method == "pdfplumber":
            return _extract_with_pdfplumber(file_path)
        elif method == "pypdf2":
            return _extract_with_pypdf2(file_path)
        elif method == "pymupdf":
            return _extract_with_pymupdf(file_path)
        else:
            raise ValueError(f"Unsupported extraction method: {method}")
            
    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {str(e)}")
        raise


def _extract_with_pdfplumber(file_path: str) -> str:
    """Extract text using pdfplumber library."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def _extract_with_pypdf2(file_path: str) -> str:
    """Extract text using PyPDF2 library."""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


def _extract_with_pymupdf(file_path: str) -> str:
    """Extract text using PyMuPDF library."""
    text = ""
    doc = fitz.open(file_path)
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text


def extract_tables_from_pdf(file_path: str) -> List[List[List[str]]]:
    """
    Extract tables from PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of tables, where each table is a list of rows,
        and each row is a list of cell values
    """
    if not PDF_LIBRARIES_AVAILABLE:
        raise ValueError("PDF processing libraries not available")
    
    logger.info(f"Extracting tables from {file_path}")
    
    try:
        tables = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        
        logger.info(f"Extracted {len(tables)} tables from {file_path}")
        return tables
        
    except Exception as e:
        logger.error(f"Failed to extract tables from {file_path}: {str(e)}")
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks for embedding.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to end at a sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            search_start = max(end - 100, start)
            sentence_end = _find_sentence_boundary(text, search_start, end)
            if sentence_end > start:
                end = sentence_end
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    logger.info(f"Split text into {len(chunks)} chunks")
    return chunks


def _find_sentence_boundary(text: str, start: int, end: int) -> int:
    """Find the best sentence boundary within a range."""
    # Look for sentence endings (., !, ?)
    sentence_endings = []
    for i in range(end - 1, start - 1, -1):
        if text[i] in '.!?':
            # Check if it's followed by whitespace or end of text
            if i + 1 >= len(text) or text[i + 1].isspace():
                sentence_endings.append(i + 1)
    
    if sentence_endings:
        return sentence_endings[0]
    
    # Fall back to word boundary
    return _find_word_boundary(text, start, end)


def _find_word_boundary(text: str, start: int, end: int) -> int:
    """Find the best word boundary within a range."""
    for i in range(end - 1, start - 1, -1):
        if text[i].isspace():
            return i + 1
    return end


def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text.
    
    Args:
        text: Raw extracted text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and headers/footers (basic patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\"\'\/\%\$\&]', ' ', text)
    
    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()


def get_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract metadata from PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Dictionary containing PDF metadata
    """
    metadata = {
        'filename': Path(file_path).name,
        'file_size': os.path.getsize(file_path),
        'num_pages': 0,
        'title': None,
        'author': None,
        'subject': None,
        'creator': None,
        'creation_date': None
    }
    
    if not PDF_LIBRARIES_AVAILABLE:
        return metadata
    
    try:
        with pdfplumber.open(file_path) as pdf:
            metadata['num_pages'] = len(pdf.pages)
            
            # Get document metadata
            if pdf.metadata:
                metadata.update({
                    'title': pdf.metadata.get('Title'),
                    'author': pdf.metadata.get('Author'),
                    'subject': pdf.metadata.get('Subject'),
                    'creator': pdf.metadata.get('Creator'),
                    'creation_date': pdf.metadata.get('CreationDate')
                })
        
    except Exception as e:
        logger.warning(f"Failed to extract metadata from {file_path}: {str(e)}")
    
    return metadata


def validate_pdf_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a file is a valid PDF.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not file_path.lower().endswith('.pdf'):
        return False, "File is not a PDF"
    
    try:
        with pdfplumber.open(file_path) as pdf:
            # Try to access first page
            if len(pdf.pages) == 0:
                return False, "PDF has no pages"
            
            # Try to extract text from first page
            first_page = pdf.pages[0]
            first_page.extract_text()
            
        return True, None
        
    except Exception as e:
        return False, f"PDF validation failed: {str(e)}"


def batch_process_pdfs(directory: str, 
                      output_dir: str = None,
                      chunk_size: int = 1000,
                      overlap: int = 200) -> List[Dict[str, Any]]:
    """
    Process multiple PDF files in a directory.
    
    Args:
        directory: Directory containing PDF files
        output_dir: Optional directory to save processed text files
        chunk_size: Size of text chunks
        overlap: Overlap between chunks
        
    Returns:
        List of processing results
    """
    results = []
    pdf_dir = Path(directory)
    
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
    
    for pdf_file in pdf_dir.glob("*.pdf"):
        try:
            logger.info(f"Processing {pdf_file.name}")
            
            # Validate PDF
            is_valid, error = validate_pdf_file(str(pdf_file))
            if not is_valid:
                results.append({
                    'file': pdf_file.name,
                    'status': 'failed',
                    'error': error
                })
                continue
            
            # Extract text
            text = extract_text_from_pdf(str(pdf_file))
            cleaned_text = clean_extracted_text(text)
            
            # Chunk text
            chunks = chunk_text(cleaned_text, chunk_size, overlap)
            
            # Save processed text if output directory specified
            if output_dir:
                output_file = output_path / f"{pdf_file.stem}_processed.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
            
            results.append({
                'file': pdf_file.name,
                'status': 'success',
                'text_length': len(cleaned_text),
                'num_chunks': len(chunks),
                'output_file': str(output_file) if output_dir else None
            })
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {str(e)}")
            results.append({
                'file': pdf_file.name,
                'status': 'failed',
                'error': str(e)
            })
    
    return results
