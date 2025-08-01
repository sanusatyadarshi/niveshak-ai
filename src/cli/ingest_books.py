"""
CLI command for ingesting investment books into the knowledge base.

Usage:
    python -m src.cli.ingest_books --directory data/books
    python -m src.cli.ingest_books --file "data/books/intelligent_investor.pdf"
"""

import click
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

from ..ingestion.books import BookIngester, list_available_books
from ..utils import logger

# Load environment variables from .env file
load_dotenv()


@click.command()
@click.option('--directory', '-d', 
              help='Directory containing book files to ingest')
@click.option('--file', '-f', 
              help='Single book file to ingest')
@click.option('--config', '-c', 
              default='config/settings.yaml',
              help='Configuration file path')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='Verbose output')
def ingest_books(directory: str, file: str, config: str, verbose: bool):
    """Ingest investment books into the knowledge base."""
    
    if verbose:
        logger.info("Starting book ingestion process...")
    
    # Validate inputs
    if not directory and not file:
        click.echo("Error: Must specify either --directory or --file")
        return
    
    if directory and file:
        click.echo("Error: Cannot specify both --directory and --file")
        return
    
    # Check config file exists
    if not os.path.exists(config):
        click.echo(f"Error: Configuration file not found: {config}")
        return
    
    try:
        # Initialize book ingester
        ingester = BookIngester(config)
        
        if file:
            # Ingest single file
            if not os.path.exists(file):
                click.echo(f"Error: File not found: {file}")
                return
            
            click.echo(f"Ingesting book: {file}")
            success = ingester.ingest_book(file)
            
            if success:
                click.echo(f"✅ Successfully ingested: {file}")
            else:
                click.echo(f"❌ Failed to ingest: {file}")
        
        elif directory:
            # Ingest directory
            if not os.path.exists(directory):
                click.echo(f"Error: Directory not found: {directory}")
                return
            
            click.echo(f"Ingesting books from directory: {directory}")
            processed_files = ingester.ingest_books_from_directory(directory)
            
            click.echo(f"\n📚 Ingestion Summary:")
            click.echo(f"   Successfully processed: {len(processed_files)} files")
            
            if verbose and processed_files:
                click.echo("\n   Processed files:")
                for file_path in processed_files:
                    click.echo(f"   • {Path(file_path).name}")
    
    except Exception as e:
        click.echo(f"❌ Error during ingestion: {str(e)}")
        if verbose:
            logger.error(f"Book ingestion failed: {str(e)}")


@click.command()
@click.option('--directory', '-d', 
              default='data/books',
              help='Directory to list books from')
def list_books(directory: str):
    """List available books in the books directory."""
    
    try:
        books = list_available_books(directory)
        
        if not books:
            click.echo(f"No books found in {directory}")
            return
        
        click.echo(f"\n📚 Available Books in {directory}:")
        click.echo("=" * 50)
        
        total_size = 0
        for book in books:
            size_mb = book['size_mb']
            total_size += size_mb
            click.echo(f"📖 {book['filename']}")
            click.echo(f"   Size: {size_mb:.1f} MB")
            click.echo(f"   Path: {book['path']}")
            click.echo()
        
        click.echo(f"Total: {len(books)} books, {total_size:.1f} MB")
        
    except Exception as e:
        click.echo(f"❌ Error listing books: {str(e)}")


@click.command()
@click.option('--book-file', '-b', 
              required=True,
              help='Book file to extract metadata from')
def show_metadata(book_file: str):
    """Show metadata for a specific book file."""
    
    try:
        if not os.path.exists(book_file):
            click.echo(f"Error: File not found: {book_file}")
            return
        
        from ..ingestion.books import get_book_metadata
        metadata = get_book_metadata(book_file)
        
        click.echo(f"\n📖 Book Metadata: {Path(book_file).name}")
        click.echo("=" * 50)
        
        for key, value in metadata.items():
            if key == 'file_size':
                value = f"{value / (1024 * 1024):.1f} MB"
            click.echo(f"{key.replace('_', ' ').title()}: {value}")
        
    except Exception as e:
        click.echo(f"❌ Error extracting metadata: {str(e)}")


@click.group()
def books():
    """Book ingestion and management commands."""
    pass


# Add commands to the group
books.add_command(ingest_books, name='ingest')
books.add_command(list_books, name='list')
books.add_command(show_metadata, name='metadata')


if __name__ == '__main__':
    books()
