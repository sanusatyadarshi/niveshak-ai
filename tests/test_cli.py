"""
Tests for the CLI module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
import tempfile
import json
from pathlib import Path

from src.cli.ingest_books import ingest_books, list_books
from src.cli.ingest_reports import ingest_reports, list_reports  
from src.cli.analyze import analyze_company, ask, compare


class TestBookCLI:
    """Test cases for book ingestion CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    @patch('src.cli.ingest_books.BookIngester')
    def test_ingest_single_book(self, mock_ingester):
        """Test ingesting a single book via CLI."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.ingest_book.return_value = True
        mock_ingester.return_value = mock_instance
        
        # Create a temporary PDF file
        test_pdf = Path(self.temp_dir) / "test_book.pdf"
        test_pdf.write_text("mock pdf content")
        
        # Run command
        result = self.runner.invoke(ingest_books, [
            '--file', str(test_pdf),
            '--config', 'test_config.yaml'
        ])
        
        assert result.exit_code == 0
        assert "Successfully ingested" in result.output
        mock_instance.ingest_book.assert_called_once_with(str(test_pdf))
    
    @patch('src.cli.ingest_books.BookIngester')
    def test_ingest_directory_of_books(self, mock_ingester):
        """Test ingesting all books from a directory."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.ingest_directory.return_value = {
            'successful': ['book1.pdf', 'book2.pdf'],
            'failed': []
        }
        mock_ingester.return_value = mock_instance
        
        # Run command
        result = self.runner.invoke(ingest_books, [
            '--directory', self.temp_dir,
            '--config', 'test_config.yaml'
        ])
        
        assert result.exit_code == 0
        assert "2 books successfully" in result.output
        mock_instance.ingest_directory.assert_called_once_with(self.temp_dir)
    
    @patch('src.cli.ingest_books.list_available_books')
    def test_list_books_command(self, mock_list):
        """Test listing available books."""
        # Setup mock
        mock_list.return_value = [
            {'filename': 'book1.pdf', 'size': 1024, 'status': 'processed'},
            {'filename': 'book2.pdf', 'size': 2048, 'status': 'pending'}
        ]
        
        # Run command
        result = self.runner.invoke(list_books, [
            '--directory', self.temp_dir
        ])
        
        assert result.exit_code == 0
        assert "book1.pdf" in result.output
        assert "book2.pdf" in result.output
        assert "processed" in result.output
    
    def test_missing_file_argument(self):
        """Test CLI behavior when file argument is missing."""
        result = self.runner.invoke(ingest_books, [])
        
        assert result.exit_code != 0
        assert "Error" in result.output
    
    def test_invalid_file_path(self):
        """Test CLI behavior with invalid file path."""
        result = self.runner.invoke(ingest_books, [
            '--file', '/nonexistent/file.pdf'
        ])
        
        assert result.exit_code != 0


class TestReportCLI:
    """Test cases for report ingestion CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    @patch('src.cli.ingest_reports.ReportIngester')
    def test_ingest_single_report(self, mock_ingester):
        """Test ingesting a single report via CLI."""
        # Setup mock
        mock_instance = Mock()
        mock_report = Mock()
        mock_report.company_symbol = "AAPL"
        mock_report.report_year = 2023
        mock_instance.ingest_report.return_value = mock_report
        mock_ingester.return_value = mock_instance
        
        # Create a temporary PDF file
        test_pdf = Path(self.temp_dir) / "AAPL_2023_10K.pdf"
        test_pdf.write_text("mock annual report content")
        
        # Run command
        result = self.runner.invoke(ingest_reports, [
            '--file', str(test_pdf),
            '--company', 'AAPL',
            '--year', '2023',
            '--report-type', '10-K'
        ])
        
        assert result.exit_code == 0
        assert "Successfully processed" in result.output
        mock_instance.ingest_report.assert_called_once()
    
    @patch('src.cli.ingest_reports.list_available_reports')
    def test_list_reports_command(self, mock_list):
        """Test listing available reports."""
        # Setup mock
        mock_list.return_value = [
            {'filename': 'AAPL_2023_10K.pdf', 'company': 'AAPL', 'year': 2023, 'type': 'pdf'},
            {'filename': 'MSFT_2023_structured.json', 'company': 'MSFT', 'year': 2023, 'type': 'structured'}
        ]
        
        # Run command
        result = self.runner.invoke(list_reports, [
            '--directory', self.temp_dir
        ])
        
        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "MSFT" in result.output
        assert "2023" in result.output
    
    @patch('src.cli.ingest_reports.list_available_reports')
    def test_list_reports_by_company(self, mock_list):
        """Test listing reports filtered by company."""
        # Setup mock
        mock_list.return_value = [
            {'filename': 'AAPL_2023_10K.pdf', 'company': 'AAPL', 'year': 2023, 'type': 'pdf'},
            {'filename': 'AAPL_2022_10K.pdf', 'company': 'AAPL', 'year': 2022, 'type': 'pdf'}
        ]
        
        # Run command
        result = self.runner.invoke(list_reports, [
            '--directory', self.temp_dir,
            '--company', 'AAPL'
        ])
        
        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "2023" in result.output
        assert "2022" in result.output


class TestAnalyzeCLI:
    """Test cases for analysis CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    @patch('src.cli.analyze.QueryEngine')
    def test_analyze_company_command(self, mock_query_engine):
        """Test company analysis command."""
        # Setup mock
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.query = "Is Apple a good investment?"
        mock_response.answer = "Apple shows strong fundamentals and growth prospects."
        mock_response.confidence_score = 0.85
        mock_response.recommendations = ["Buy", "Hold for long term"]
        mock_response.reasoning = "Strong balance sheet and market position"
        mock_response.sources = ["10-K filing", "analyst report"]
        mock_response.timestamp = Mock()
        mock_response.timestamp.strftime.return_value = "2023-12-01 10:00:00"
        
        mock_instance.process_query.return_value = mock_response
        mock_query_engine.return_value = mock_instance
        
        # Run command
        result = self.runner.invoke(analyze_company, [
            '--company', 'AAPL',
            '--query', 'Is Apple a good investment?'
        ])
        
        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "strong fundamentals" in result.output
        assert "85.0%" in result.output  # Confidence score
        mock_instance.process_query.assert_called_once()
    
    @patch('src.cli.analyze.QueryEngine')
    def test_ask_general_question(self, mock_query_engine):
        """Test asking a general investment question."""
        # Setup mock
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.query = "What are the best value investing strategies?"
        mock_response.answer = "Focus on companies with strong fundamentals trading below intrinsic value."
        mock_response.confidence_score = 0.90
        mock_response.recommendations = ["Use margin of safety", "Focus on long-term"]
        mock_response.reasoning = "Based on Benjamin Graham's principles"
        mock_response.sources = ["The Intelligent Investor"]
        mock_response.timestamp = Mock()
        mock_response.timestamp.strftime.return_value = "2023-12-01 10:00:00"
        
        mock_instance.process_query.return_value = mock_response
        mock_query_engine.return_value = mock_instance
        
        # Run command
        result = self.runner.invoke(ask, [
            '--query', 'What are the best value investing strategies?'
        ])
        
        assert result.exit_code == 0
        assert "value investing" in result.output
        assert "margin of safety" in result.output
        assert "90.0%" in result.output
    
    @patch('src.cli.analyze.QueryEngine')
    def test_compare_companies(self, mock_query_engine):
        """Test comparing multiple companies."""
        # Setup mock
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.query = "Compare AAPL,MSFT,GOOGL based on financial_health,valuation,growth_prospects"
        mock_response.answer = "AAPL leads in profitability, MSFT in stability, GOOGL in growth."
        mock_response.confidence_score = 0.80
        mock_response.recommendations = ["AAPL for income", "GOOGL for growth"]
        mock_response.reasoning = "Based on financial metrics analysis"
        mock_response.sources = ["10-K filings", "financial statements"]
        mock_response.timestamp = Mock()
        mock_response.timestamp.strftime.return_value = "2023-12-01 10:00:00"
        
        mock_instance.process_query.return_value = mock_response
        mock_query_engine.return_value = mock_instance
        
        # Run command
        result = self.runner.invoke(compare, [
            '--companies', 'AAPL,MSFT,GOOGL',
            '--criteria', 'financial_health,valuation,growth_prospects'
        ])
        
        assert result.exit_code == 0
        assert "AAPL" in result.output
        assert "MSFT" in result.output
        assert "GOOGL" in result.output
        assert "profitability" in result.output
    
    @patch('src.cli.analyze.QueryEngine')
    def test_save_analysis_output(self, mock_query_engine):
        """Test saving analysis output to file."""
        # Setup mock
        mock_instance = Mock()
        mock_response = Mock()
        mock_response.query = "Test query"
        mock_response.answer = "Test answer"
        mock_response.confidence_score = 0.85
        mock_response.recommendations = ["Test recommendation"]
        mock_response.reasoning = "Test reasoning"
        mock_response.sources = ["Test source"]
        mock_response.timestamp = Mock()
        mock_response.timestamp.isoformat.return_value = "2023-12-01T10:00:00"
        mock_response.timestamp.strftime.return_value = "2023-12-01 10:00:00"
        
        mock_instance.process_query.return_value = mock_response
        mock_query_engine.return_value = mock_instance
        
        # Create temp output file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            output_file = tmp.name
        
        try:
            # Run command with output file
            result = self.runner.invoke(compare, [
                '--companies', 'AAPL,MSFT',
                '--output', output_file
            ])
            
            assert result.exit_code == 0
            assert f"saved to: {output_file}" in result.output
            
            # Verify file was created and contains expected data
            with open(output_file, 'r') as f:
                saved_data = json.load(f)
                assert 'companies' in saved_data
                assert 'analysis' in saved_data
                assert saved_data['companies'] == ['AAPL', 'MSFT']
        
        finally:
            # Clean up
            Path(output_file).unlink(missing_ok=True)
    
    def test_missing_required_arguments(self):
        """Test CLI behavior with missing required arguments."""
        # Test analyze without company or query
        result = self.runner.invoke(analyze_company, [])
        assert result.exit_code != 0
        assert "Error" in result.output
        
        # Test ask without query
        result = self.runner.invoke(ask, [])
        assert result.exit_code != 0
        
        # Test compare without companies
        result = self.runner.invoke(compare, [])
        assert result.exit_code != 0


class TestCLIIntegration:
    """Integration tests for CLI commands."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_full_workflow_simulation(self):
        """Test a complete workflow from ingestion to analysis."""
        # This would test:
        # 1. Ingest books and reports
        # 2. Run analysis queries
        # 3. Compare results
        # 
        # Since this requires full system integration,
        # this is a placeholder for future implementation
        pass
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


@pytest.fixture
def mock_config_file():
    """Mock configuration file for testing."""
    return {
        'openai': {'api_key': 'test_api_key'},
        'vector_db': {
            'provider': 'qdrant',
            'host': 'localhost',
            'port': 6333
        },
        'storage': {
            'books_dir': 'data/books',
            'reports_dir': 'data/reports'
        }
    }


def test_cli_error_handling():
    """Test CLI error handling for various edge cases."""
    runner = CliRunner()
    
    # Test with invalid config file
    result = runner.invoke(ingest_books, [
        '--file', 'test.pdf',
        '--config', 'nonexistent_config.yaml'
    ])
    
    # Should handle gracefully
    assert result.exit_code != 0


def test_cli_help_messages():
    """Test that help messages are informative."""
    runner = CliRunner()
    
    # Test help for each command
    commands = [ingest_books, ingest_reports, analyze_company, ask, compare]
    
    for command in commands:
        result = runner.invoke(command, ['--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert len(result.output) > 100  # Should have substantial help text


if __name__ == "__main__":
    pytest.main([__file__])
