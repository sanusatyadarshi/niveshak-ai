"""
AI-Powered PDF Financial Data Extractor
=======================================

Uses configurable LLM API (OpenAI, Anthropic, Ollama) to intelligently extract 
financial data from annual reports. Processes last 3 years of reports to populate 
comprehensive fundamental analysis.

Supported LLM Providers:
- OpenAI (GPT-4o, GPT-3.5-turbo)
- Anthropic (Claude-3)
- Ollama (Local models)
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import requests
import pdfplumber
import re

# LLM Provider imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    # Look for .env file in project root
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # dotenv not available, skip
    pass


class LLMPDFAnalyzer:
    """
    AI-powered PDF analyzer supporting multiple LLM providers
    
    Supports:
    - OpenAI (GPT-4o, GPT-3.5-turbo)
    - Anthropic (Claude-3)
    - Ollama (Local models)
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize with configurable LLM provider"""
        # Force load environment variables
        self._load_environment_variables()
        
        self.config_path = config_path
        self.config = self._load_config()
        
        # Get PDF analysis configuration
        self.pdf_config = self.config.get('llm', {}).get('pdf_analysis', {})
        self.provider = self.pdf_config.get('provider', 'openai')
        self.model = self.pdf_config.get('model', 'gpt-4o')
        self.temperature = self.pdf_config.get('temperature', 0.1)
        
        # Initialize the selected provider
        self._initialize_provider()
        
        print(f"🤖 LLM PDF Analyzer initialized with {self.provider.upper()} provider")
    
    def _load_environment_variables(self):
        """Force load environment variables from .env file"""
        try:
            from dotenv import load_dotenv
            
            # Try multiple possible locations for .env file
            possible_paths = [
                Path(".env"),  # Current working directory
                Path(__file__).parent.parent.parent / ".env",  # Project root
                Path("/app/.env"),  # Docker container path
            ]
            
            for env_path in possible_paths:
                if env_path.exists():
                    print(f"🔍 Loading environment from: {env_path}")
                    load_dotenv(env_path, override=True)
                    return
            
            print("⚠️  No .env file found in expected locations")
        except ImportError:
            print("⚠️  python-dotenv not available, relying on system environment variables")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file and substitute environment variables"""
        try:
            with open(self.config_path, 'r') as f:
                config_content = f.read()
            
            # Substitute environment variables
            import os
            import re
            
            def replace_env_vars(match):
                var_name = match.group(1)
                return os.getenv(var_name, match.group(0))
            
            # Replace ${VAR_NAME} with actual environment variable values
            config_content = re.sub(r'\$\{([^}]+)\}', replace_env_vars, config_content)
            
            # Parse the YAML after substitution
            import yaml
            return yaml.safe_load(config_content)
        except Exception as e:
            print(f"⚠️  Could not load config from {self.config_path}: {e}")
            return {}
    
    def _initialize_provider(self):
        """Initialize the selected LLM provider"""
        if self.provider == 'openai':
            self._initialize_openai()
        elif self.provider == 'anthropic':
            self._initialize_anthropic()
        elif self.provider == 'ollama':
            self._initialize_ollama()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not available. Install with: pip install openai")
        
        # BYPASS CONFIG FILE - Get API key directly from environment
        api_key = os.getenv('OPENAI_API_KEY')
        
        # Force load .env if API key not found
        if not api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv("/app/.env", override=True)
                load_dotenv(".env", override=True)
                api_key = os.getenv('OPENAI_API_KEY')
            except:
                pass
        
        print("🔍 Debug - API key status: FOUND" if api_key else "🔍 Debug - API key: NOT_FOUND")
        
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        if api_key.startswith('${'):
            print(f"🔍 Debug - Template detected: {api_key}")
            raise ValueError(f"API key is template variable: {api_key}")
        
        # Additional validation - check if it's a valid API key format
        if not api_key.startswith('sk-'):
            print(f"🔍 Debug - Invalid format: {api_key[:50]}...")
            raise ValueError(f"Invalid OpenAI API key format. Expected sk-*, got: {api_key[:50]}...")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o"
    
    def _initialize_anthropic(self):
        """Initialize Anthropic client"""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic package not available. Install with: pip install anthropic")
        
        api_config = self.config.get('api', {}).get('anthropic', {})
        api_key = api_config.get('api_key')
        
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError("Anthropic API key not found in config or environment")
        
        self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        self.model = api_config.get('model', self.model)
    
    def _initialize_ollama(self):
        """Initialize Ollama client"""
        if not OLLAMA_AVAILABLE:
            raise ImportError("Requests package required for Ollama")
        
        ollama_config = self.config.get('api', {}).get('ollama', {})
        self.ollama_base_url = ollama_config.get('base_url', 'http://localhost:11434')
        self.model = ollama_config.get('model', self.model)
    
    def analyze_multi_year_reports(self, symbol: str) -> Dict[str, Any]:
        """
        Extract financial data from multiple years of annual reports using AI
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Multi-year financial data dictionary
        """
        print(f"📊 Extracting Multi-Year Financial Data for {symbol} using {self.provider.upper()}")
        
        try:
            # Find available annual reports
            symbol_dir = Path(f"data/annual_reports/{symbol}")
            if not symbol_dir.exists():
                raise FileNotFoundError(f"No annual reports directory found for {symbol}. Please upload annual reports first.")
            
            # Get PDF files sorted by year (newest first)
            pdf_files = list(symbol_dir.glob("*.pdf"))
            if not pdf_files:
                raise FileNotFoundError(f"No PDF files found for {symbol}. Please upload annual reports first.")
            
            sorted_pdfs = sorted(pdf_files, key=lambda x: int(x.stem), reverse=True)[:3]
            print(f"📁 Found {len(sorted_pdfs)} annual reports: {[f.name for f in sorted_pdfs]}")
            
            # Extract financial data from PDFs
            financial_texts = []
            for pdf_file in sorted_pdfs:
                print(f"📄 Processing {pdf_file.name}...")
                extracted_text = self._extract_financial_text_from_pdf(str(pdf_file))
                if extracted_text:
                    financial_texts.append({
                        'year': pdf_file.stem,
                        'text': extracted_text
                    })
            
            if not financial_texts:
                raise ValueError("Could not extract text from any PDFs. Please check if the PDF files are valid.")
            
            # Use LLM to analyze extracted financial data
            print("🤖 Analyzing financial data with AI...")
            analysis_result = self._analyze_financial_data_with_llm(symbol, financial_texts)
            
            if analysis_result and analysis_result.get('data_quality') == 'AI_EXTRACTED':
                print("✅ AI-powered financial data extraction completed")
                return analysis_result
            else:
                raise RuntimeError("AI analysis failed to produce valid results. Please check API configuration.")
                
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            raise e  # Re-raise the exception instead of using fallback
    
    def _extract_financial_text_from_pdf(self, pdf_path: str) -> str:
        """Extract relevant financial text from PDF"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    full_text += page_text + "\n"
                
                # Extract key financial sections
                financial_sections = []
                patterns = [
                    r"profit.*loss|income.*statement|statement.*income",
                    r"balance.*sheet|financial.*position", 
                    r"cash.*flow|statement.*cash",
                    r"financial.*highlights|key.*metrics",
                    r"ratio.*analysis|financial.*ratios"
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, full_text, re.IGNORECASE | re.DOTALL)
                    for match in matches:
                        # Extract context around the match (500 chars before and after)
                        start = max(0, match.start() - 500)
                        end = min(len(full_text), match.end() + 1500)
                        section_text = full_text[start:end]
                        financial_sections.append(section_text)
                
                # If no specific sections found, return first 5000 characters
                if not financial_sections:
                    return full_text[:5000]
                
                return "\n\n".join(financial_sections[:3])  # Return top 3 sections
                
        except Exception as e:
            print(f"❌ Error extracting text from {pdf_path}: {e}")
            return ""
    
    def _analyze_financial_data_with_llm(self, symbol: str, financial_texts: List[Dict]) -> Optional[Dict[str, Any]]:
        """Use LLM to analyze extracted financial data"""
        try:
            # Prepare prompt for financial analysis
            prompt = self._create_financial_analysis_prompt(symbol, financial_texts)
            
            # Get LLM response based on provider
            if self.provider == 'openai':
                response = self._get_openai_analysis(prompt)
            elif self.provider == 'anthropic':
                response = self._get_anthropic_analysis(prompt)
            elif self.provider == 'ollama':
                response = self._get_ollama_analysis(prompt)
            else:
                return None
            
            # Parse and structure the response
            return self._parse_llm_response(response, symbol)
            
        except Exception as e:
            print(f"❌ Error in LLM analysis: {e}")
            return None
    
    def _create_financial_analysis_prompt(self, symbol: str, financial_texts: List[Dict]) -> str:
        """Create prompt for LLM financial analysis"""
        prompt = f"""
Analyze the following financial data for {symbol} and extract key metrics:

"""
        for text_data in financial_texts:
            prompt += f"\n--- Year {text_data['year']} ---\n"
            prompt += text_data['text'][:2000]  # Limit text length
            prompt += "\n"
        
        prompt += f"""

Please extract and calculate the following financial metrics for {symbol}:

1. Company Information:
   - Business description
   - Industry sector
   - Main products/services

2. Financial Performance (latest 3 years):
   - Revenue growth rate
   - Net profit margin
   - Return on Equity (ROE)
   - Return on Assets (ROA) 
   - Debt to Equity ratio
   - Current ratio
   - Quick ratio

3. Key Financial Numbers:
   - Latest revenue
   - Latest net profit
   - Total assets
   - Shareholders equity
   - Total debt
   - Cash and equivalents
   - Shares outstanding
   - Book value per share
   - Earnings per share (EPS)

4. Cash Flow Analysis:
   - Operating cash flow
   - Free cash flow
   - Cash flow growth rate

Provide the response in JSON format with numeric values where applicable.
"""
        return prompt
    
    def _get_openai_analysis(self, prompt: str) -> str:
        """Get analysis from OpenAI"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial analyst expert at extracting data from annual reports."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=2000
        )
        return response.choices[0].message.content
    
    def _get_anthropic_analysis(self, prompt: str) -> str:
        """Get analysis from Anthropic Claude"""
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=self.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _get_ollama_analysis(self, prompt: str) -> str:
        """Get analysis from Ollama"""
        response = requests.post(
            f"{self.ollama_base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature
                }
            }
        )
        return response.json().get('response', '')
    
    def _parse_llm_response(self, response: str, symbol: str) -> Dict[str, Any]:
        """Parse LLM response and structure financial data"""
        try:
            # Try to extract JSON from the response
            import json
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed_data = json.loads(json_str)
                
                # Structure the data for the analyzer
                return {
                    'company_name': parsed_data.get('company_name', f'{symbol} Limited'),
                    'symbol': symbol,
                    'latest_year': '2025',
                    'revenue': parsed_data.get('revenue', 0),
                    'revenue_growth_3yr': parsed_data.get('revenue_growth_rate', 0),
                    'net_profit': parsed_data.get('net_profit', 0),
                    'profit_margin': parsed_data.get('net_profit_margin', 0),
                    'free_cash_flow': parsed_data.get('free_cash_flow', 0),
                    'operating_cash_flow': parsed_data.get('operating_cash_flow', 0),
                    'total_assets': parsed_data.get('total_assets', 0),
                    'shareholders_equity': parsed_data.get('shareholders_equity', 0),
                    'total_debt': parsed_data.get('total_debt', 0),
                    'cash_and_equivalents': parsed_data.get('cash_and_equivalents', 0),
                    'shares_outstanding': parsed_data.get('shares_outstanding', 0),
                    'roe': parsed_data.get('roe', 0),
                    'roa': parsed_data.get('roa', 0),
                    'debt_to_equity': parsed_data.get('debt_to_equity', 0),
                    'current_ratio': parsed_data.get('current_ratio', 0),
                    'quick_ratio': parsed_data.get('quick_ratio', 0),
                    'book_value_per_share': parsed_data.get('book_value_per_share', 0),
                    'eps': parsed_data.get('eps', 0),
                    'data_quality': 'AI_EXTRACTED'
                }
            
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            print(f"Raw response: {response[:500]}...")
            raise RuntimeError(f"Failed to parse LLM response: {e}")
    
    def analyze_with_llm(self, prompt: str) -> str:
        """
        Analyze financial data or documents using the configured LLM provider
        
        Args:
            prompt: Analysis prompt for the LLM
            
        Returns:
            LLM analysis response
        """
        try:
            if self.provider == 'openai' and OPENAI_AVAILABLE:
                return self._analyze_with_openai(prompt)
            elif self.provider == 'anthropic' and ANTHROPIC_AVAILABLE:
                return self._analyze_with_anthropic(prompt)
            elif self.provider == 'ollama' and OLLAMA_AVAILABLE:
                return self._analyze_with_ollama(prompt)
            else:
                raise ValueError(f"No valid LLM provider available. Current provider: {self.provider}")
                
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {str(e)}")
            raise e  # Re-raise instead of falling back to fake data

    def _analyze_with_openai(self, prompt: str) -> str:
        """Analyze using OpenAI API"""
        try:
            response = self.client.chat.completions.create(
                model=self.config['api']['openai']['model'],
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in comprehensive fundamental analysis of Indian companies. Provide detailed, specific insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config['api']['openai']['max_tokens'],
                temperature=self.config['api']['openai']['temperature']
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI analysis failed: {str(e)}")

    def _analyze_with_anthropic(self, prompt: str) -> str:
        """Analyze using Anthropic Claude API"""
        try:
            response = self.anthropic_client.messages.create(
                model=self.config['api']['anthropic']['model'],
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": f"As a financial analyst, {prompt}"}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic analysis failed: {str(e)}")

    def _analyze_with_ollama(self, prompt: str) -> str:
        """Analyze using Ollama local model"""
        try:
            response = requests.post(
                f"{self.config['api']['ollama']['base_url']}/api/generate",
                json={
                    "model": self.config['api']['ollama']['model'],
                    "prompt": f"As a financial analyst specializing in Indian markets: {prompt}",
                    "stream": False,
                    "options": {
                        "temperature": self.config['api']['ollama']['temperature'],
                        "num_predict": self.config['api']['ollama']['max_tokens']
                    }
                }
            )
            return response.json()['response']
        except Exception as e:
            raise Exception(f"Ollama analysis failed: {str(e)}")