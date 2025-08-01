"""
Query module for RAG-based AI analysis with persona integration.

This module handles:
- Query processing and embedding
- Retrieval from knowledge base (books + reports)
- LLM prompt generation with persona context
- Response generation and formatting
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import yaml
from openai import OpenAI
import ollama

from ..embedding.embedder import EmbeddingManager
from ..utils import logger


@dataclass
class QueryContext:
    """Context for a user query."""
    query: str
    user_persona: Dict[str, Any]
    retrieved_documents: List[Dict[str, Any]]
    company_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResponse:
    """Response from AI analysis."""
    query: str
    answer: str
    reasoning: str
    confidence_score: float
    sources: List[str]
    recommendations: List[str]
    timestamp: datetime


class PersonaManager:
    """Manages user investment persona and preferences."""
    
    def __init__(self, persona_config_path: str = "config/persona.yaml"):
        """Initialize persona manager."""
        with open(persona_config_path, 'r') as f:
            self.persona_config = yaml.safe_load(f)
    
    def get_persona_prompt(self) -> str:
        """Generate persona-based prompt for LLM."""
        persona = self.persona_config
        
        prompt = f"""
You are an AI investment advisor customized for this investor profile:

INVESTOR PROFILE:
- Name: {persona.get('name', 'Investor')}
- Experience Level: {persona.get('investing_experience', 'Unknown')}
- Risk Tolerance: {persona.get('risk_tolerance', 'Unknown')}
- Investment Style: {persona['philosophy']['style']}
- Time Horizon: {persona['philosophy']['time_horizon']}

INVESTMENT PHILOSOPHY:
- Key Principles: {', '.join(persona['philosophy']['key_principles'])}
- Preferred Sectors: {', '.join(persona['philosophy']['preferred_sectors'])}
- Primary Valuation Method: {persona['valuation_methods']['primary']}
- Margin of Safety: {persona['valuation_methods']['margin_of_safety'] * 100}%

RISK MANAGEMENT:
- Max Position Size: {persona['risk_management']['max_position_size'] * 100}%
- Stop Loss: {persona['risk_management']['stop_loss_threshold'] * 100}%

INVESTMENT CRITERIA:
- Min Market Cap: ${persona['custom_criteria']['min_market_cap']:,}
- Min ROE: {persona['custom_criteria']['min_roe'] * 100}%
- Max Debt-to-Equity: {persona['custom_criteria']['max_debt_to_equity']}

When providing investment advice, always consider these preferences and provide reasoning 
that aligns with this investor's philosophy and risk tolerance.
"""
        return prompt.strip()
    
    def get_investment_criteria(self) -> Dict[str, Any]:
        """Get structured investment criteria."""
        return self.persona_config.get('custom_criteria', {})
    
    def get_risk_preferences(self) -> Dict[str, Any]:
        """Get risk management preferences."""
        return self.persona_config.get('risk_management', {})


class QueryEngine:
    """Main query processing engine with RAG capabilities."""
    
    def __init__(self, 
                 config_path: str = "config/settings.yaml",
                 persona_path: str = "config/persona.yaml"):
        """Initialize query engine."""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.embedding_manager = EmbeddingManager(self.config)
        self.persona_manager = PersonaManager(persona_path)
        self.llm_client = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize LLM client (OpenAI, Ollama, Anthropic, etc.)."""
        llm_config = self.config.get('llm', {})
        provider = llm_config.get('provider', 'openai')
        
        if provider == 'ollama':
            # Initialize Ollama client
            ollama_config = self.config['api']['ollama']
            self.llm_provider = 'ollama'
            self.model = ollama_config.get('model', 'deepseek-r1:7b')
            self.temperature = ollama_config.get('temperature', 0.1)
            self.max_tokens = ollama_config.get('max_tokens', 2000)
            logger.info(f"Initialized Ollama client with model: {self.model}")
            return None  # Ollama uses direct API calls
            
        elif provider == 'openai':
            # Initialize OpenAI client
            openai_config = self.config['api'].get('openai', {})
            api_key = openai_config.get('api_key')
            
            if api_key and api_key.startswith('${') and api_key.endswith('}'):
                # Extract environment variable name
                env_var = api_key[2:-1]  # Remove ${ and }
                api_key = os.getenv(env_var)
            
            if not api_key:
                raise ValueError("OpenAI API key not found in config or environment")
            
            self.llm_provider = 'openai'
            self.openai_client = OpenAI(api_key=api_key)
            self.model = openai_config.get('model', 'gpt-3.5-turbo')
            self.temperature = openai_config.get('temperature', 0.1)
            self.max_tokens = openai_config.get('max_tokens', 2000)
            logger.info(f"Initialized OpenAI client with model: {self.model}")
            return self.openai_client
            
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def process_query(self, query: str, company_symbol: Optional[str] = None) -> AnalysisResponse:
        """
        Process a user query and generate AI-powered response.
        
        Args:
            query: User's investment question
            company_symbol: Optional company symbol for context
            
        Returns:
            AnalysisResponse with detailed analysis
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Retrieve relevant context from knowledge base
            retrieved_docs = self._retrieve_context(query, company_symbol)
            
            # Get company-specific data if symbol provided
            company_data = self._get_company_data(company_symbol) if company_symbol else None
            
            # Create query context
            context = QueryContext(
                query=query,
                user_persona=self.persona_manager.persona_config,
                retrieved_documents=retrieved_docs,
                company_data=company_data
            )
            
            # Generate response using LLM
            response = self._generate_response(context)
            
            logger.info(f"Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            raise
    
    def _retrieve_context(self, query: str, company_symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents from knowledge base."""
        # Search for relevant content
        results = self.embedding_manager.search_knowledge_base(query, top_k=5)
        
        # If company symbol provided, also search for company-specific content
        if company_symbol:
            company_query = f"{company_symbol} financial analysis annual report"
            company_results = self.embedding_manager.search_knowledge_base(company_query, top_k=3)
            results.extend(company_results)
        
        # Format results
        formatted_results = []
        for content, metadata, score in results:
            formatted_results.append({
                'content': content,
                'metadata': metadata,
                'relevance_score': score
            })
        
        return formatted_results
    
    def _get_company_data(self, company_symbol: str) -> Optional[Dict[str, Any]]:
        """Retrieve company-specific financial data."""
        # TODO: Load structured financial data for the company
        # This could come from processed annual reports, APIs, etc.
        return None
    
    def _generate_response(self, context: QueryContext) -> AnalysisResponse:
        """Generate LLM response based on context."""
        try:
            # Build sources list
            sources = [doc['metadata'].get('source', 'Unknown source') for doc in context.retrieved_documents]
            
            # Build prompt
            prompt = f"""You are an expert investment analyst. Answer the following question based on the provided context.
            If you cannot answer from the context, say so.

            Question: {context.query}

            Context:
            {context.retrieved_documents}

            Sources: {', '.join(sources)}

            Provide a detailed, well-structured response that:
            1. Directly answers the question
            2. Cites specific information from the sources
            3. Explains the reasoning behind your analysis
            4. Highlights any important caveats or limitations

            Response:"""
            
            # Call appropriate LLM API based on provider
            if self.llm_provider == 'ollama':
                ai_response = self._call_ollama(prompt)
            elif self.llm_provider == 'openai':
                ai_response = self._call_openai(prompt)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
            
            # Format sources to include content
            sources = []
            for doc in context.retrieved_documents[:3]:
                source = f"{doc['metadata'].get('source', 'Knowledge Base')}: {doc['content'][:150]}..."
                sources.append(source)
            
            return AnalysisResponse(
                query=context.query,
                answer=ai_response,
                reasoning="Analysis based on retrieved knowledge and investment persona",
                confidence_score=0.85,  # Could be calculated based on retrieval scores
                sources=sources,
                recommendations=self._extract_recommendations(ai_response),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {str(e)}")
            # Fallback response
            return AnalysisResponse(
                query=context.query,
                answer="I apologize, but I encountered an error generating the analysis. Please check your API configuration and try again.",
                reasoning="Error in response generation",
                confidence_score=0.0,
                sources=[],
                recommendations=[],
                timestamp=datetime.now()
            )
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API for LLM response."""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are NiveshakAI, an expert investment advisor with deep knowledge of fundamental analysis. Provide detailed, actionable investment advice based on the user's persona and available data."
                    },
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama API call failed: {str(e)}")
            raise
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API for LLM response."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are NiveshakAI, an expert investment advisor with deep knowledge of fundamental analysis. Provide detailed, actionable investment advice based on the user's persona and available data."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise
    
    def _extract_recommendations(self, ai_response: str) -> List[str]:
        """Extract recommendations from AI response."""
        # Simple extraction - look for recommendation keywords
        recommendations = []
        lines = ai_response.split('\n')
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommendation', 'suggest', 'consider']):
                in_recommendations = True
            elif in_recommendations and line.startswith(('•', '-', '1.', '2.', '3.')):
                recommendations.append(line.lstrip('•-123456789. '))
            elif in_recommendations and line == '':
                continue
            elif in_recommendations and not line.startswith(('•', '-', '1.', '2.', '3.')):
                in_recommendations = False
        
        return recommendations[:5]  # Return max 5 recommendations
    
    def _build_prompt(self, context: QueryContext) -> str:
        """Build comprehensive prompt for LLM."""
        persona_prompt = self.persona_manager.get_persona_prompt()
        
        # Add retrieved context
        context_text = "\n\nRELEVANT KNOWLEDGE:\n"
        for i, doc in enumerate(context.retrieved_documents[:3]):  # Top 3 most relevant
            context_text += f"{i+1}. {doc['content'][:500]}...\n"
        
        # Add company data if available
        company_context = ""
        if context.company_data:
            company_context = f"\n\nCOMPANY DATA:\n{context.company_data}"
        
        prompt = f"""
{persona_prompt}

{context_text}
{company_context}

USER QUESTION: {context.query}

Please provide a comprehensive investment analysis that:
1. Directly answers the user's question
2. Incorporates relevant information from the knowledge base
3. Aligns with the investor's personal philosophy and risk tolerance
4. Provides clear reasoning for any recommendations
5. Mentions specific sources when referencing data

Format your response with clear sections for:
- Analysis
- Reasoning
- Recommendations (if applicable)
- Risk Considerations
"""
        
        return prompt.strip()


class AnalysisReportGenerator:
    """Generates formatted analysis reports."""
    
    def __init__(self, query_engine: QueryEngine):
        """Initialize report generator."""
        self.query_engine = query_engine
    
    def generate_company_analysis_report(self, company_symbol: str) -> Dict[str, Any]:
        """Generate comprehensive company analysis report."""
        queries = [
            f"What is the financial health of {company_symbol}?",
            f"What are the key risks for investing in {company_symbol}?",
            f"Is {company_symbol} undervalued or overvalued?",
            f"What is the competitive position of {company_symbol}?"
        ]
        
        report = {
            'company_symbol': company_symbol,
            'generation_date': datetime.now().isoformat(),
            'sections': {}
        }
        
        for query in queries:
            response = self.query_engine.process_query(query, company_symbol)
            section_name = query.split('?')[0].replace(f'{company_symbol}', '').strip()
            report['sections'][section_name] = {
                'analysis': response.answer,
                'reasoning': response.reasoning,
                'confidence': response.confidence_score,
                'sources': response.sources
            }
        
        return report
    
    def save_report(self, report: Dict[str, Any], output_dir: str = "data/reports") -> str:
        """Save analysis report to file."""
        import os
        import json
        
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{report['company_symbol']}_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath


def create_query_engine(config_path: str = "config/settings.yaml") -> QueryEngine:
    """Create and return a query engine instance."""
    return QueryEngine(config_path)
