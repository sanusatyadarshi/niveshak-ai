#!/usr/bin/env python3
"""
NiveshakAI - Personal AI Fundamental Investing Assistant

Main entry point for the application.
"""

import sys
import os
import argparse
from pathlib import Path

# Load environment variables first
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils import NiveshakLogger, logger


def main():
    """Main entry point for NiveshakAI."""
    
    parser = argparse.ArgumentParser(
        description="NiveshakAI - Personal AI Fundamental Investing Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ingest books --directory data/books
  %(prog)s ingest reports --file AAPL_2023_10K.pdf --company AAPL --year 2023
  %(prog)s analyze company --company AAPL --query "Is Apple a good investment?"
  %(prog)s analyze ask --query "What are the best value investing strategies?"
  %(prog)s analyze compare --companies AAPL,MSFT,GOOGL

For more information, visit: https://github.com/yourusername/niveshak-ai
        """
    )
    
    parser.add_argument(
        '--config',
        default='config/settings.yaml',
        help='Configuration file path (default: config/settings.yaml)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest subcommands
    ingest_parser = subparsers.add_parser('ingest', help='Ingest books and reports')
    ingest_subparsers = ingest_parser.add_subparsers(dest='ingest_type')
    
    # Books ingestion
    books_parser = ingest_subparsers.add_parser('books', help='Ingest investment books')
    books_parser.add_argument('--file', help='Single PDF file to ingest')
    books_parser.add_argument('--directory', help='Directory containing PDF files')
    books_parser.add_argument('--list', action='store_true', help='List available books')
    
    # Reports ingestion  
    reports_parser = ingest_subparsers.add_parser('reports', help='Ingest annual reports')
    reports_parser.add_argument('--file', help='Single report file to ingest')
    reports_parser.add_argument('--company', help='Company symbol')
    reports_parser.add_argument('--year', type=int, help='Report year')
    reports_parser.add_argument('--report-type', help='Report type (10-K, 10-Q, etc.)')
    reports_parser.add_argument('--list', action='store_true', help='List available reports')
    
    # Analysis subcommands
    analyze_parser = subparsers.add_parser('analyze', help='Analyze companies and investments')
    analyze_subparsers = analyze_parser.add_subparsers(dest='analyze_type')
    
    # Company analysis
    company_parser = analyze_subparsers.add_parser('company', help='Analyze a specific company')
    company_parser.add_argument('--company', '-c', required=True, help='Company symbol')
    company_parser.add_argument('--query', '-q', help='Specific question about the company')
    company_parser.add_argument('--valuation', choices=['dcf', 'pe', 'pb'], help='Valuation method')
    company_parser.add_argument('--output', '-o', help='Output file for results')
    
    # General questions
    ask_parser = analyze_subparsers.add_parser('ask', help='Ask general investment questions')
    ask_parser.add_argument('--query', '-q', required=True, help='Investment question')
    
    # Company comparison
    compare_parser = analyze_subparsers.add_parser('compare', help='Compare multiple companies')
    compare_parser.add_argument('--companies', '-c', required=True, 
                               help='Comma-separated company symbols')
    compare_parser.add_argument('--criteria', default='financial_health,valuation,growth_prospects',
                               help='Comparison criteria')
    compare_parser.add_argument('--output', '-o', help='Output file for results')
    
    args = parser.parse_args()
    
    # Setup logging
    try:
        NiveshakLogger.setup_logging()
        
        if args.verbose:
            import logging
            logging.getLogger().setLevel(logging.DEBUG)
            
        logger.info("Starting NiveshakAI...")
        
    except Exception as e:
        print(f"Warning: Could not setup logging: {e}")
    
    # Handle commands
    try:
        if args.command == 'ingest':
            handle_ingest_command(args)
        elif args.command == 'analyze':
            handle_analyze_command(args)
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        if logger:
            logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def handle_ingest_command(args):
    """Handle ingestion commands."""
    
    if args.ingest_type == 'books':
        from src.cli.ingest_books import ingest_books as books_main
        
        # Convert args to sys.argv format for click
        sys.argv = ['ingest_books']
        if args.file:
            sys.argv.extend(['--file', args.file])
        if args.directory:
            sys.argv.extend(['--directory', args.directory])
        if args.list:
            sys.argv.append('--list')
        if hasattr(args, 'config'):
            sys.argv.extend(['--config', args.config])
            
        books_main()
        
    elif args.ingest_type == 'reports':
        from src.cli.ingest_reports import ingest_reports as reports_main
        
        # Convert args to sys.argv format for click
        sys.argv = ['ingest_reports']
        if args.file:
            sys.argv.extend(['--file', args.file])
        if args.company:
            sys.argv.extend(['--company', args.company])
        if args.year:
            sys.argv.extend(['--year', str(args.year)])
        if args.report_type:
            sys.argv.extend(['--report-type', args.report_type])
        if args.list:
            sys.argv.append('--list')
        if hasattr(args, 'config'):
            sys.argv.extend(['--config', args.config])
            
        reports_main()
        
    else:
        print("Please specify 'books' or 'reports' for ingestion")


def handle_analyze_command(args):
    """Handle analysis commands."""
    
    if args.analyze_type == 'company':
        from src.cli.analyze import analyze_company
        from click.testing import CliRunner
        
        runner = CliRunner()
        cmd_args = ['--company', args.company]
        
        if args.query:
            cmd_args.extend(['--query', args.query])
        if args.valuation:
            cmd_args.extend(['--valuation', args.valuation])
        if args.output:
            cmd_args.extend(['--output', args.output])
        if hasattr(args, 'config'):
            cmd_args.extend(['--config', args.config])
            
        result = runner.invoke(analyze_company, cmd_args)
        print(result.output)
        
    elif args.analyze_type == 'ask':
        from src.cli.analyze import ask
        from click.testing import CliRunner
        
        runner = CliRunner()
        cmd_args = ['--query', args.query]
        
        if hasattr(args, 'config'):
            cmd_args.extend(['--config', args.config])
            
        result = runner.invoke(ask, cmd_args)
        print(result.output)
        
    elif args.analyze_type == 'compare':
        from src.cli.analyze import compare
        from click.testing import CliRunner
        
        runner = CliRunner()
        cmd_args = ['--companies', args.companies]
        
        if args.criteria:
            cmd_args.extend(['--criteria', args.criteria])
        if args.output:
            cmd_args.extend(['--output', args.output])
        if hasattr(args, 'config'):
            cmd_args.extend(['--config', args.config])
            
        result = runner.invoke(compare, cmd_args)
        print(result.output)
        
    else:
        print("Please specify 'company', 'ask', or 'compare' for analysis")


if __name__ == '__main__':
    main()
