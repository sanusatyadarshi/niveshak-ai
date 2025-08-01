"""
CLI command for analyzing companies using AI-powered investment analysis.

Usage:
    python -m src.cli.analyze --company AAPL --query "Is Apple a good investment?"
    python -m src.cli.analyze --company MSFT --valuation dcf
    python -m src.cli.analyze --query "What are the best tech stocks to buy?"
"""

import click
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from ..analysis.query import QueryEngine, AnalysisReportGenerator
from ..analysis.valuation import DCFAnalyzer, MultipleValuation, create_dcf_analyzer

# Load environment variables from .env file
load_dotenv()
from ..utils.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.option('--company', '-c', 
              help='Company stock symbol to analyze (e.g., AAPL)')
@click.option('--query', '-q', 
              help='Investment question to ask')
@click.option('--valuation', '-v',
              type=click.Choice(['dcf', 'pe', 'pb']),
              help='Valuation method to use')
@click.option('--output', '-o',
              help='Output file to save analysis results')
@click.option('--config', 
              default='config/settings.yaml',
              help='Configuration file path')
@click.option('--verbose', 
              is_flag=True, 
              help='Verbose output')
def analyze_company(company: str, query: str, valuation: str, output: str, config: str, verbose: bool):
    """Analyze a company using AI-powered investment analysis."""
    
    if not company and not query:
        click.echo("Error: Must specify either --company or --query")
        return
    
    try:
        if company:
            company = company.upper()
            click.echo(f"🔍 Analyzing {company}...")
            
            # Use direct symbol-based analysis to bypass vector database
            from ..analysis.symbol_stock_analyzer import SymbolStockAnalyzer
            
            analyzer = SymbolStockAnalyzer(symbol=company)
            
            # Extract multi-year financial data
            financial_data = analyzer.extract_multi_year_financial_data(company)
            
            # Generate fundamental analysis report
            report_content = analyzer.generate_fundamental_analysis_report(company, financial_data)
            
            # Generate DCF analysis
            dcf_results = analyzer.generate_dcf_analysis(company, financial_data)
            
            # Add DCF section to report
            dcf_section = analyzer._format_dcf_section(dcf_results)
            report_content += dcf_section
            
            # Save report
            report_file = analyzer.reports_dir / f"{company}-{analyzer._get_report_date()}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            click.echo(f"\n✅ Analysis completed!")
            click.echo(f"📄 Report saved: {report_file}")
            click.echo(f"🎯 Recommendation: {dcf_results.get('recommendation', 'HOLD')}")
            click.echo(f"💰 Intrinsic Value: ₹{dcf_results.get('intrinsic_value_per_share', 0):.2f}")
            click.echo(f"📈 Current Price: ₹{dcf_results.get('current_price', 0):.2f}")
            
        elif query:
            # For general queries, we still need the QueryEngine
            # Initialize query engine
            query_engine = QueryEngine(config)
            
            # General investment query
            click.echo(f"💭 Processing query: {query}")
            response = query_engine.process_query(query)
            _display_analysis_response(response, verbose)
        
    except Exception as e:
        click.echo(f"❌ Analysis failed: {str(e)}")
        if verbose:
            logger.error(f"Company analysis failed: {str(e)}")
            logger.error(f"Company analysis failed: {str(e)}")


def _display_analysis_response(response, verbose: bool):
    """Display analysis response in formatted output."""
    click.echo("\n" + "="*60)
    click.echo("📊 INVESTMENT ANALYSIS")
    click.echo("="*60)
    
    click.echo(f"\n🎯 Query: {response.query}")
    click.echo(f"⏰ Generated: {response.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    click.echo(f"🎯 Confidence: {response.confidence_score:.1%}")
    
    click.echo(f"\n📝 Analysis:")
    click.echo("-" * 40)
    click.echo(response.answer)
    
    if verbose and response.reasoning:
        click.echo(f"\n🧠 Reasoning:")
        click.echo("-" * 40)
        click.echo(response.reasoning)
    
    if response.recommendations:
        click.echo(f"\n💡 Recommendations:")
        click.echo("-" * 40)
        for i, rec in enumerate(response.recommendations, 1):
            click.echo(f"{i}. {rec}")
    
    if verbose and response.sources:
        click.echo(f"\n📚 Sources:")
        click.echo("-" * 40)
        for source in set(response.sources):
            click.echo(f"• {source}")


def _perform_valuation_analysis(company: str, method: str, verbose: bool):
    """Perform valuation analysis using specified method."""
    click.echo(f"⚠️  Valuation analysis requires financial data for {company}")
    click.echo("This is a placeholder implementation.")
    
    # TODO: Implement actual valuation analysis
    # This would require:
    # 1. Loading financial data for the company
    # 2. Performing the specified valuation method
    # 3. Displaying results
    
    if method == 'dcf':
        click.echo("📊 DCF Analysis would be performed here")
    elif method == 'pe':
        click.echo("📊 P/E Multiple Analysis would be performed here")
    elif method == 'pb':
        click.echo("📊 P/B Multiple Analysis would be performed here")


def _generate_company_report(company: str, query_engine: QueryEngine, output: Optional[str], verbose: bool):
    """Generate comprehensive company analysis report."""
    try:
        report_generator = AnalysisReportGenerator(query_engine)
        report = report_generator.generate_company_analysis_report(company)
        
        # Display summary
        click.echo("\n" + "="*60)
        click.echo(f"📋 COMPREHENSIVE ANALYSIS REPORT - {company}")
        click.echo("="*60)
        
        for section_name, section_data in report['sections'].items():
            click.echo(f"\n📝 {section_name}:")
            click.echo("-" * 40)
            click.echo(section_data['analysis'][:300] + "..." if len(section_data['analysis']) > 300 else section_data['analysis'])
            click.echo(f"   Confidence: {section_data['confidence']:.1%}")
        
        # Save report if output specified
        if output:
            with open(output, 'w') as f:
                json.dump(report, f, indent=2)
            click.echo(f"\n💾 Report saved to: {output}")
        else:
            # Save to default location
            output_file = report_generator.save_report(report)
            click.echo(f"\n💾 Report saved to: {output_file}")
            
    except Exception as e:
        click.echo(f"❌ Failed to generate report: {str(e)}")


@click.command()
@click.option('--query', '-q', 
              required=True,
              help='Investment question to ask')
@click.option('--config', 
              default='config/settings.yaml',
              help='Configuration file path')
@click.option('--verbose', 
              is_flag=True, 
              help='Verbose output')
def ask(query: str, config: str, verbose: bool):
    """Ask a general investment question to the AI assistant."""
    
    try:
        query_engine = QueryEngine(config)
        
        click.echo(f"💭 Processing: {query}")
        response = query_engine.process_query(query)
        
        _display_analysis_response(response, verbose)
        
    except Exception as e:
        click.echo(f"❌ Query failed: {str(e)}")
        if verbose:
            logger.error(f"Query processing failed: {str(e)}")


@click.command()
@click.option('--companies', '-c',
              required=True,
              help='Comma-separated list of company symbols to compare (e.g., AAPL,MSFT,GOOGL)')
@click.option('--criteria', 
              default='financial_health,valuation,growth_prospects',
              help='Comma-separated comparison criteria')
@click.option('--output', '-o',
              help='Output file to save comparison results')
@click.option('--config', 
              default='config/settings.yaml',
              help='Configuration file path')
@click.option('--verbose', 
              is_flag=True, 
              help='Verbose output')
def compare(companies: str, criteria: str, output: str, config: str, verbose: bool):
    """Compare multiple companies side by side."""
    
    try:
        company_list = [c.strip().upper() for c in companies.split(',')]
        criteria_list = [c.strip() for c in criteria.split(',')]
        
        query_engine = QueryEngine(config)
        
        click.echo(f"⚖️  Comparing companies: {', '.join(company_list)}")
        click.echo(f"📊 Criteria: {', '.join(criteria_list)}")
        
        # Generate comparison query
        comparison_query = f"Compare {', '.join(company_list)} based on {', '.join(criteria_list)}. Which would be the best investment?"
        
        response = query_engine.process_query(comparison_query)
        _display_analysis_response(response, verbose)
        
        if output:
            comparison_data = {
                'companies': company_list,
                'criteria': criteria_list,
                'analysis': response.answer,
                'reasoning': response.reasoning,
                'recommendations': response.recommendations,
                'timestamp': response.timestamp.isoformat()
            }
            
            with open(output, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            click.echo(f"\n💾 Comparison saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Comparison failed: {str(e)}")
        if verbose:
            logger.error(f"Company comparison failed: {str(e)}")


@click.group()
def analyze():
    """AI-powered investment analysis commands."""
    pass


# Add commands to the group
analyze.add_command(analyze_company, name='company')
analyze.add_command(ask, name='ask')
analyze.add_command(compare, name='compare')


if __name__ == '__main__':
    analyze()
