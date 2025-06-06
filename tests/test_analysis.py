"""
Tests for the analysis module.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.analysis.valuation import DCFAnalyzer, MultipleValuation
from src.analysis.query import QueryEngine, AnalysisResponse


class TestDCFAnalyzer:
    """Test cases for DCF analysis."""
    
    def test_dcf_initialization(self):
        """Test DCF analyzer initialization."""
        analyzer = DCFAnalyzer(
            company_symbol="AAPL",
            discount_rate=0.10,
            terminal_growth_rate=0.03
        )
        
        assert analyzer.company_symbol == "AAPL"
        assert analyzer.discount_rate == 0.10
        assert analyzer.terminal_growth_rate == 0.03
    
    def test_project_cash_flows(self):
        """Test cash flow projection."""
        analyzer = DCFAnalyzer("AAPL", 0.10, 0.03)
        
        historical_cf = [10000, 9500, 9000]  # Most recent first
        growth_rates = [0.05, 0.04, 0.03, 0.03, 0.03]
        
        projected = analyzer.project_cash_flows(historical_cf, growth_rates)
        
        assert len(projected) == 5
        assert projected[0] == 10000 * 1.05  # First year growth
        assert projected[1] == projected[0] * 1.04  # Second year growth
    
    def test_calculate_terminal_value(self):
        """Test terminal value calculation."""
        analyzer = DCFAnalyzer("AAPL", 0.10, 0.03)
        
        final_cf = 12000
        terminal_value = analyzer.calculate_terminal_value(final_cf)
        
        # Terminal value = final_cf * (1 + growth) / (discount - growth)
        expected = final_cf * 1.03 / (0.10 - 0.03)
        assert abs(terminal_value - expected) < 0.01
    
    def test_calculate_present_value(self):
        """Test present value calculation."""
        analyzer = DCFAnalyzer("AAPL", 0.10, 0.03)
        
        cash_flows = [1000, 1100, 1200]
        terminal_value = 15000
        
        pv = analyzer.calculate_present_value(cash_flows, terminal_value)
        
        # Should be positive and reasonable
        assert pv > 0
        assert pv > sum(cash_flows)  # PV should be higher due to terminal value
    
    def test_invalid_discount_rate(self):
        """Test invalid discount rate handling."""
        with pytest.raises(ValueError, match="Discount rate must be greater than terminal growth rate"):
            DCFAnalyzer("AAPL", 0.02, 0.03)  # Discount < Growth
    
    def test_perform_analysis(self):
        """Test complete DCF analysis."""
        # Mock financial data
        financial_data = {
            'free_cash_flow': [10000, 9500, 9000],
            'revenue_growth': [0.15, 0.12, 0.10],
            'wacc': 0.09
        }
        
        analyzer = DCFAnalyzer("AAPL", 0.09, 0.025)
        
        with patch.object(analyzer, '_get_financial_data', return_value=financial_data):
            result = analyzer.perform_analysis()
            
            assert 'intrinsic_value' in result
            assert 'current_price' in result
            assert 'recommendation' in result
            assert result['intrinsic_value'] > 0


class TestMultipleValuation:
    """Test cases for multiple-based valuation."""
    
    def test_pe_valuation(self):
        """Test P/E ratio valuation."""
        valuation = MultipleValuation("AAPL")
        
        # Mock data
        company_data = {'eps': 6.15, 'growth_rate': 0.08}
        peer_data = [
            {'symbol': 'MSFT', 'pe_ratio': 28.5},
            {'symbol': 'GOOGL', 'pe_ratio': 22.1},
            {'symbol': 'META', 'pe_ratio': 24.7}
        ]
        
        result = valuation.calculate_pe_valuation(company_data, peer_data)
        
        assert 'target_price' in result
        assert 'current_pe' in result
        assert 'peer_average_pe' in result
        assert result['target_price'] > 0
    
    def test_pb_valuation(self):
        """Test P/B ratio valuation."""
        valuation = MultipleValuation("AAPL")
        
        # Mock data
        company_data = {'book_value_per_share': 4.25, 'roe': 0.18}
        peer_data = [
            {'symbol': 'MSFT', 'pb_ratio': 13.2},
            {'symbol': 'GOOGL', 'pb_ratio': 6.1},
            {'symbol': 'META', 'pb_ratio': 7.8}
        ]
        
        result = valuation.calculate_pb_valuation(company_data, peer_data)
        
        assert 'target_price' in result
        assert 'current_pb' in result
        assert 'peer_average_pb' in result
        assert result['target_price'] > 0
    
    def test_empty_peer_data(self):
        """Test handling of empty peer data."""
        valuation = MultipleValuation("AAPL")
        
        company_data = {'eps': 6.15}
        peer_data = []
        
        result = valuation.calculate_pe_valuation(company_data, peer_data)
        
        # Should return None or handle gracefully
        assert result is None or 'error' in result


class TestQueryEngine:
    """Test cases for query engine."""
    
    @patch('src.analysis.query.VectorDB')
    @patch('src.analysis.query.OpenAI')
    def test_query_engine_initialization(self, mock_openai, mock_vector_db):
        """Test query engine initialization."""
        config_path = "test_config.yaml"
        
        with patch('builtins.open'), patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {
                'openai': {'api_key': 'test_key'},
                'vector_db': {'provider': 'qdrant'}
            }
            
            engine = QueryEngine(config_path)
            
            assert engine.config is not None
            mock_vector_db.assert_called_once()
            mock_openai.assert_called_once()
    
    @patch('src.analysis.query.VectorDB')
    @patch('src.analysis.query.OpenAI')
    def test_process_query(self, mock_openai, mock_vector_db):
        """Test query processing."""
        # Setup mocks
        mock_vector_instance = Mock()
        mock_vector_db.return_value = mock_vector_instance
        
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance
        
        # Mock search results
        mock_vector_instance.search_similar.return_value = [
            {'id': '1', 'score': 0.95, 'metadata': {'text': 'Apple is a great investment'}},
            {'id': '2', 'score': 0.90, 'metadata': {'text': 'Strong financial performance'}}
        ]
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Apple shows strong fundamentals..."
        mock_openai_instance.chat.completions.create.return_value = mock_response
        
        with patch('builtins.open'), patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {
                'openai': {'api_key': 'test_key'},
                'vector_db': {'provider': 'qdrant'}
            }
            
            engine = QueryEngine("test_config.yaml")
            response = engine.process_query("Is Apple a good investment?")
            
            assert isinstance(response, AnalysisResponse)
            assert response.query == "Is Apple a good investment?"
            assert response.answer == "Apple shows strong fundamentals..."
            assert response.confidence_score > 0
    
    def test_analysis_response_structure(self):
        """Test AnalysisResponse data structure."""
        response = AnalysisResponse(
            query="Test query",
            answer="Test answer",
            reasoning="Test reasoning",
            recommendations=["Buy", "Hold"],
            confidence_score=0.85,
            sources=["source1", "source2"],
            timestamp=datetime.now()
        )
        
        assert response.query == "Test query"
        assert response.answer == "Test answer"
        assert response.confidence_score == 0.85
        assert len(response.recommendations) == 2
        assert len(response.sources) == 2
    
    @patch('src.analysis.query.VectorDB')
    @patch('src.analysis.query.OpenAI')
    def test_query_with_company_context(self, mock_openai, mock_vector_db):
        """Test query processing with specific company context."""
        # Setup similar to test_process_query but with company symbol
        mock_vector_instance = Mock()
        mock_vector_db.return_value = mock_vector_instance
        
        mock_openai_instance = Mock()
        mock_openai.return_value = mock_openai_instance
        
        # Mock company-specific search results
        mock_vector_instance.search_similar.return_value = [
            {'id': '1', 'score': 0.95, 'metadata': {'text': 'AAPL financial data', 'company': 'AAPL'}}
        ]
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "AAPL specific analysis..."
        mock_openai_instance.chat.completions.create.return_value = mock_response
        
        with patch('builtins.open'), patch('yaml.safe_load') as mock_yaml:
            mock_yaml.return_value = {
                'openai': {'api_key': 'test_key'},
                'vector_db': {'provider': 'qdrant'}
            }
            
            engine = QueryEngine("test_config.yaml")
            response = engine.process_query("What is the valuation?", company_symbol="AAPL")
            
            assert "AAPL" in response.answer or response.answer == "AAPL specific analysis..."


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing."""
    return {
        'revenue': 365000000000,  # $365B
        'net_income': 25000000000,  # $25B
        'free_cash_flow': [20000000000, 18000000000, 16000000000],  # FCF history
        'total_debt': 30000000000,  # $30B
        'cash': 50000000000,  # $50B
        'shares_outstanding': 16000000000,  # 16B shares
        'current_price': 150.0,
        'beta': 1.2,
        'eps': 6.15
    }


@pytest.fixture
def sample_peer_data():
    """Sample peer comparison data for testing."""
    return [
        {'symbol': 'MSFT', 'pe_ratio': 28.5, 'pb_ratio': 13.2, 'market_cap': 2800000000000},
        {'symbol': 'GOOGL', 'pe_ratio': 22.1, 'pb_ratio': 6.1, 'market_cap': 1600000000000},
        {'symbol': 'META', 'pe_ratio': 24.7, 'pb_ratio': 7.8, 'market_cap': 800000000000}
    ]


def test_valuation_integration(sample_financial_data, sample_peer_data):
    """Integration test for valuation methods."""
    # Test that DCF and multiples valuation can work together
    dcf_analyzer = DCFAnalyzer("AAPL", 0.09, 0.025)
    multiple_valuation = MultipleValuation("AAPL")
    
    # Mock the financial data retrieval
    with patch.object(dcf_analyzer, '_get_financial_data', return_value=sample_financial_data):
        dcf_result = dcf_analyzer.perform_analysis()
        
        company_data = {'eps': sample_financial_data['eps']}
        pe_result = multiple_valuation.calculate_pe_valuation(company_data, sample_peer_data)
        
        # Both methods should provide valuation estimates
        assert dcf_result['intrinsic_value'] > 0
        assert pe_result['target_price'] > 0


if __name__ == "__main__":
    pytest.main([__file__])
