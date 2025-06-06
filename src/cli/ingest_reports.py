"""
CLI command for ingesting annual reports into the knowledge base.

Usage:
    python -m src.cli.ingest_reports --directory data/reports
    python -m src.cli.ingest_reports --file "data/reports/AAPL_2023_10K.pdf" --symbol AAPL --year 2023
"""

import click
import os
from pathlib import Path
from typing import List

from ..ingestion.reports import ReportIngester, list_available_reports, get_company_reports
from ..utils.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.option('--directory', '-d', 
              help='Directory containing report files to ingest')
@click.option('--file', '-f', 
              help='Single report file to ingest')
@click.option('--symbol', '-s', 
              help='Company stock symbol (required when using --file)')
@click.option('--year', '-y', 
              type=int,
              help='Report year (required when using --file)')
@click.option('--config', '-c', 
              default='config/settings.yaml',
              help='Configuration file path')
@click.option('--verbose', '-v', 
              is_flag=True, 
              help='Verbose output')
def ingest_reports(directory: str, file: str, symbol: str, year: int, config: str, verbose: bool):
    """Ingest annual reports into the knowledge base."""
    
    if verbose:
        logger.info("Starting report ingestion process...")
    
    # Validate inputs
    if not directory and not file:
        click.echo("Error: Must specify either --directory or --file")
        return
    
    if directory and file:
        click.echo("Error: Cannot specify both --directory and --file")
        return
    
    if file and (not symbol or not year):
        click.echo("Error: When using --file, must also specify --symbol and --year")
        return
    
    # Check config file exists
    if not os.path.exists(config):
        click.echo(f"Error: Configuration file not found: {config}")
        return
    
    try:
        # Initialize report ingester
        ingester = ReportIngester(config)
        
        if file:
            # Ingest single file
            if not os.path.exists(file):
                click.echo(f"Error: File not found: {file}")
                return
            
            click.echo(f"Ingesting report: {file} ({symbol}, {year})")
            report = ingester.ingest_report(file, symbol, year)
            
            if report:
                click.echo(f"✅ Successfully ingested: {file}")
                if verbose:
                    click.echo(f"   Company: {report.company_name}")
                    click.echo(f"   Year: {report.report_year}")
                    click.echo(f"   Key metrics: {len(report.key_metrics)} calculated")
            else:
                click.echo(f"❌ Failed to ingest: {file}")
        
        elif directory:
            # Ingest directory
            if not os.path.exists(directory):
                click.echo(f"Error: Directory not found: {directory}")
                return
            
            click.echo(f"Ingesting reports from directory: {directory}")
            reports = ingester.ingest_reports_from_directory(directory)
            
            click.echo(f"\n📊 Ingestion Summary:")
            click.echo(f"   Successfully processed: {len(reports)} reports")
            
            if verbose and reports:
                click.echo("\n   Processed reports:")
                for report in reports:
                    click.echo(f"   • {report.company_symbol} ({report.report_year})")
    
    except Exception as e:
        click.echo(f"❌ Error during ingestion: {str(e)}")
        if verbose:
            logger.error(f"Report ingestion failed: {str(e)}")


@click.command()
@click.option('--directory', '-d', 
              default='data/reports',
              help='Directory to list reports from')
def list_reports(directory: str):
    """List available reports in the reports directory."""
    
    try:
        reports = list_available_reports(directory)
        
        if not reports:
            click.echo(f"No reports found in {directory}")
            return
        
        click.echo(f"\n📊 Available Reports in {directory}:")
        click.echo("=" * 50)
        
        # Group by type
        pdf_reports = [r for r in reports if r['type'] == 'pdf']
        structured_reports = [r for r in reports if r['type'] == 'structured']
        
        if pdf_reports:
            click.echo("\n📄 PDF Reports:")
            total_size = 0
            for report in pdf_reports:
                size_mb = report['size_mb']
                total_size += size_mb
                click.echo(f"   📋 {report['filename']}")
                click.echo(f"      Size: {size_mb:.1f} MB")
                click.echo()
            click.echo(f"   Total PDF reports: {len(pdf_reports)}, {total_size:.1f} MB")
        
        if structured_reports:
            click.echo("\n🗂️  Structured Reports:")
            for report in structured_reports:
                click.echo(f"   📊 {report['filename']}")
                click.echo(f"      Size: {report['size_mb']:.1f} MB")
                click.echo()
            click.echo(f"   Total structured reports: {len(structured_reports)}")
        
    except Exception as e:
        click.echo(f"❌ Error listing reports: {str(e)}")


@click.command()
@click.option('--symbol', '-s', 
              required=True,
              help='Company stock symbol (e.g., AAPL)')
@click.option('--directory', '-d', 
              default='data/reports',
              help='Directory to search for company reports')
def company_reports(symbol: str, directory: str):
    """List all reports for a specific company."""
    
    try:
        reports = get_company_reports(symbol.upper(), directory)
        
        if not reports:
            click.echo(f"No reports found for {symbol.upper()}")
            return
        
        click.echo(f"\n📊 Reports for {symbol.upper()}:")
        click.echo("=" * 40)
        
        for report in reports:
            click.echo(f"📋 {report['filename']}")
            click.echo(f"   Path: {report['path']}")
            click.echo()
        
        click.echo(f"Total: {len(reports)} reports")
        
    except Exception as e:
        click.echo(f"❌ Error listing company reports: {str(e)}")


@click.group()
def reports():
    """Annual report ingestion and management commands."""
    pass


# Add commands to the group
reports.add_command(ingest_reports, name='ingest')
reports.add_command(list_reports, name='list')
reports.add_command(company_reports, name='company')


if __name__ == '__main__':
    reports()
