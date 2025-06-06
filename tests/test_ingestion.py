"""
Tests for the ingestion module functionality.

This module tests:
- Book ingestion from PDFs
- Annual report processing
- Text extraction and chunking
- Metadata extraction
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.ingestion.books import BookIngester, list_available_books, get_book_metadata
from src.ingestion.reports import ReportIngester, list_available_reports, get_company_reports


class TestBookIngestion:
    """Test book ingestion functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'storage': {'books_dir': self.temp_dir},
            'vector_db': {'provider': 'qdrant'},
            'embedding': {'chunk_size': 1000, 'chunk_overlap': 200}
        }
    
    def create_mock_pdf(self, filename: str) -> str:
        """Create a mock PDF file for testing."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(b'%PDF-1.4\nMock PDF content for testing')
        return file_path
    
    def test_book_ingester_initialization(self):
        """Test BookIngester initialization."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test: config"
            
            with patch('yaml.safe_load', return_value=self.test_config):
                ingester = BookIngester("test_config.yaml")
                assert ingester.config == self.test_config
    
    @patch('src.ingestion.books.VectorStore')
    @patch('src.ingestion.books.extract_text_from_pdf')
    def test_ingest_single_book_success(self, mock_extract, mock_vector_store):
        """Test successful ingestion of a single book."""
        # Create mock PDF file
        pdf_path = self.create_mock_pdf("test_book.pdf")
        
        # Mock text extraction
        mock_extract.return_value = "This is sample book content for testing."
        
        # Mock vector store
        mock_store_instance = Mock()
        mock_vector_store.return_value = mock_store_instance
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test: config"
            
            with patch('yaml.safe_load', return_value=self.test_config):
                ingester = BookIngester("test_config.yaml")
                result = ingester.ingest_book(pdf_path)
                
                assert result == True
                mock_extract.assert_called_once_with(pdf_path)
    
    def test_ingest_nonexistent_book(self):
        """Test ingestion of non-existent book file."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test: config"
            
            with patch('yaml.safe_load', return_value=self.test_config):
                ingester = BookIngester("test_config.yaml")
                result = ingester.ingest_book("nonexistent.pdf")
                
                assert result == False
    
    def test_list_available_books_empty(self):
        """Test listing books from empty directory."""
        books = list_available_books(self.temp_dir)
        assert books == []
    
    def test_list_available_books_with_files(self):
        """Test listing books with PDF files present."""
        # Create test PDF files
        pdf1 = self.create_mock_pdf("book1.pdf")
        pdf2 = self.create_mock_pdf("book2.pdf")
        
        books = list_available_books(self.temp_dir)
        
        assert len(books) == 2
        assert any(book['filename'] == 'book1.pdf' for book in books)
        assert any(book['filename'] == 'book2.pdf' for book in books)
    
    def test_get_book_metadata(self):
        """Test book metadata extraction."""
        pdf_path = self.create_mock_pdf("test_book.pdf")
        
        metadata = get_book_metadata(pdf_path)
        
        assert metadata['filename'] == 'test_book.pdf'
        assert metadata['file_size'] > 0
        assert metadata['file_type'] == '.pdf'


class TestReportIngestion:
    """Test annual report ingestion functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            'storage': {'reports_dir': self.temp_dir}
        }
    
    def create_mock_report(self, filename: str) -> str:
        """Create a mock report file for testing."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(b'%PDF-1.4\nMock annual report content')
        return file_path
    
    def test_report_ingester_initialization(self):
        """Test ReportIngester initialization."""
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test: config"
            
            with patch('yaml.safe_load', return_value=self.test_config):
                ingester = ReportIngester("test_config.yaml")
                assert ingester.config == self.test_config
    
    @patch('src.ingestion.reports.extract_text_from_pdf')
    @patch('src.ingestion.reports.extract_tables_from_pdf')
    def test_ingest_single_report_success(self, mock_extract_tables, mock_extract_text):
        """Test successful ingestion of a single report."""
        # Create mock report file
        report_path = self.create_mock_report("AAPL_2023_10K.pdf")
        
        # Mock extractions
        mock_extract_text.return_value = "APPLE INC. Annual Report 2023..."
        mock_extract_tables.return_value = [['Revenue', '1000'], ['Net Income', '200']]
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = "test: config"
            
            with patch('yaml.safe_load', return_value=self.test_config):
                ingester = ReportIngester("test_config.yaml")
                report = ingester.ingest_report(report_path, "AAPL", 2023)
                
                assert report is not None
                assert report.company_symbol == "AAPL"
                assert report.report_year == 2023
                mock_extract_text.assert_called_once_with(report_path)
                mock_extract_tables.assert_called_once_with(report_path)
    
    def test_list_available_reports_empty(self):
        """Test listing reports from empty directory."""
        reports = list_available_reports(self.temp_dir)
        assert reports == []
    
    def test_list_available_reports_with_files(self):
        """Test listing reports with files present."""
        # Create test report files
        self.create_mock_report("AAPL_2023_10K.pdf")
        self.create_mock_report("MSFT_2023_structured.json")
        
        reports = list_available_reports(self.temp_dir)
        
        assert len(reports) == 2
        pdf_reports = [r for r in reports if r['type'] == 'pdf']
        json_reports = [r for r in reports if r['type'] == 'structured']
        
        assert len(pdf_reports) == 1
        assert len(json_reports) == 1
    
    def test_get_company_reports(self):
        """Test getting reports for specific company."""
        # Create test report files
        self.create_mock_report("AAPL_2023_10K.pdf")
        self.create_mock_report("AAPL_2022_10K.pdf")
        self.create_mock_report("MSFT_2023_10K.pdf")
        
        aapl_reports = get_company_reports("AAPL", self.temp_dir)
        
        assert len(aapl_reports) == 2
        assert all(report['company'] == 'AAPL' for report in aapl_reports)


class TestIngestionIntegration:
    """Integration tests for the ingestion module."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_end_to_end_book_ingestion(self):
        """Test complete book ingestion workflow."""
        # This would test the entire flow from PDF to vector store
        # Placeholder for integration test
        pass
    
    def test_end_to_end_report_ingestion(self):
        """Test complete report ingestion workflow."""
        # This would test the entire flow from PDF to structured data
        # Placeholder for integration test
        pass
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


# Test fixtures and utilities
@pytest.fixture
def sample_book_content():
    """Sample book content for testing."""
    return """
    Chapter 1: Introduction to Value Investing
    
    Value investing is an investment strategy that involves picking stocks 
    that appear to be trading for less than their intrinsic value. 
    This approach was developed by Benjamin Graham and David Dodd.
    
    Key principles include:
    1. Margin of safety
    2. Long-term perspective
    3. Fundamental analysis
    """


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing."""
    return {
        'revenue': 365_000_000_000,  # $365B
        'net_income': 25_000_000_000,  # $25B
        'total_assets': 180_000_000_000,  # $180B
        'cash': 50_000_000_000,  # $50B
        'total_debt': 30_000_000_000  # $30B
    }


if __name__ == "__main__":
    pytest.main([__file__])
