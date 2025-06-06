"""
NiveshakAI - Your Personal AI Fundamental Investing Assistant

A personal AI agent designed to help you become a smarter, data-driven fundamental investor.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .ingestion import books, reports
from .embedding import embedder
from .analysis import valuation, query
from .utils import logger

# Initialize logging
logger.setup_logging()
