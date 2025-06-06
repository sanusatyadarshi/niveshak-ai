"""
Tests for the embedding module.
"""
import pytest
from unittest.mock import Mock, patch
import numpy as np
from src.embedding.embedder import VectorDB, OpenAIEmbedder


class TestVectorDB:
    """Test cases for VectorDB class."""
    
    @patch('src.embedding.embedder.qdrant_client')
    def test_connect_qdrant(self, mock_qdrant):
        """Test Qdrant connection."""
        # Setup
        config = {
            'provider': 'qdrant',
            'host': 'localhost',
            'port': 6333
        }
        
        # Execute
        vector_db = VectorDB(config)
        
        # Assert
        assert vector_db.provider == 'qdrant'
        mock_qdrant.QdrantClient.assert_called_once()
    
    @patch('src.embedding.embedder.weaviate')
    def test_connect_weaviate(self, mock_weaviate):
        """Test Weaviate connection."""
        # Setup
        config = {
            'provider': 'weaviate',
            'url': 'http://localhost:8080'
        }
        
        # Execute
        vector_db = VectorDB(config)
        
        # Assert
        assert vector_db.provider == 'weaviate'
        mock_weaviate.Client.assert_called_once()
    
    def test_invalid_provider(self):
        """Test invalid provider raises error."""
        config = {'provider': 'invalid'}
        
        with pytest.raises(ValueError, match="Unsupported vector database provider"):
            VectorDB(config)
    
    @patch('src.embedding.embedder.qdrant_client')
    def test_store_embeddings_qdrant(self, mock_qdrant):
        """Test storing embeddings in Qdrant."""
        # Setup
        config = {'provider': 'qdrant', 'host': 'localhost', 'port': 6333}
        vector_db = VectorDB(config)
        
        embeddings = [
            {'id': '1', 'vector': [0.1, 0.2, 0.3], 'metadata': {'text': 'test1'}},
            {'id': '2', 'vector': [0.4, 0.5, 0.6], 'metadata': {'text': 'test2'}}
        ]
        
        # Execute
        vector_db.store_embeddings(embeddings, 'test_collection')
        
        # Assert
        mock_qdrant.QdrantClient.return_value.upsert.assert_called_once()
    
    @patch('src.embedding.embedder.qdrant_client')
    def test_search_similar_qdrant(self, mock_qdrant):
        """Test similarity search in Qdrant."""
        # Setup
        config = {'provider': 'qdrant', 'host': 'localhost', 'port': 6333}
        vector_db = VectorDB(config)
        
        # Mock search results
        mock_result = Mock()
        mock_result.id = '1'
        mock_result.score = 0.95
        mock_result.payload = {'text': 'test result'}
        mock_qdrant.QdrantClient.return_value.search.return_value = [mock_result]
        
        query_vector = [0.1, 0.2, 0.3]
        
        # Execute
        results = vector_db.search_similar(query_vector, 'test_collection', top_k=5)
        
        # Assert
        assert len(results) == 1
        assert results[0]['id'] == '1'
        assert results[0]['score'] == 0.95
        assert results[0]['metadata']['text'] == 'test result'


class TestOpenAIEmbedder:
    """Test cases for OpenAIEmbedder class."""
    
    @patch('src.embedding.embedder.openai')
    def test_initialization(self, mock_openai):
        """Test embedder initialization."""
        # Setup
        api_key = "test_api_key"
        
        # Execute
        embedder = OpenAIEmbedder(api_key)
        
        # Assert
        assert embedder.model == "text-embedding-3-small"
        mock_openai.OpenAI.assert_called_once_with(api_key=api_key)
    
    @patch('src.embedding.embedder.openai')
    def test_generate_embedding(self, mock_openai):
        """Test embedding generation."""
        # Setup
        embedder = OpenAIEmbedder("test_api_key")
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4]
        mock_openai.OpenAI.return_value.embeddings.create.return_value = mock_response
        
        # Execute
        result = embedder.generate_embedding("Test text")
        
        # Assert
        assert result == [0.1, 0.2, 0.3, 0.4]
        mock_openai.OpenAI.return_value.embeddings.create.assert_called_once_with(
            input="Test text",
            model="text-embedding-3-small"
        )
    
    @patch('src.embedding.embedder.openai')
    def test_generate_embeddings_batch(self, mock_openai):
        """Test batch embedding generation."""
        # Setup
        embedder = OpenAIEmbedder("test_api_key")
        
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock(), Mock()]
        mock_response.data[0].embedding = [0.1, 0.2, 0.3]
        mock_response.data[1].embedding = [0.4, 0.5, 0.6]
        mock_openai.OpenAI.return_value.embeddings.create.return_value = mock_response
        
        texts = ["Text 1", "Text 2"]
        
        # Execute
        results = embedder.generate_embeddings(texts)
        
        # Assert
        assert len(results) == 2
        assert results[0] == [0.1, 0.2, 0.3]
        assert results[1] == [0.4, 0.5, 0.6]
    
    @patch('src.embedding.embedder.openai')
    def test_api_error_handling(self, mock_openai):
        """Test API error handling."""
        # Setup
        embedder = OpenAIEmbedder("test_api_key")
        mock_openai.OpenAI.return_value.embeddings.create.side_effect = Exception("API Error")
        
        # Execute & Assert
        with pytest.raises(Exception, match="API Error"):
            embedder.generate_embedding("Test text")


@pytest.fixture
def sample_embeddings():
    """Sample embeddings for testing."""
    return [
        {'id': 'doc1', 'vector': [0.1, 0.2, 0.3], 'metadata': {'source': 'book', 'chapter': 1}},
        {'id': 'doc2', 'vector': [0.4, 0.5, 0.6], 'metadata': {'source': 'report', 'company': 'AAPL'}},
        {'id': 'doc3', 'vector': [0.7, 0.8, 0.9], 'metadata': {'source': 'book', 'chapter': 2}}
    ]


def test_embedding_dimension_consistency():
    """Test that all embeddings have consistent dimensions."""
    embedder = OpenAIEmbedder("test_api_key")
    
    # Mock consistent dimensions
    with patch.object(embedder, 'generate_embeddings') as mock_gen:
        mock_gen.return_value = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]
        
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = embedder.generate_embeddings(texts)
        
        # Assert all embeddings have same dimension
        dimensions = [len(emb) for emb in embeddings]
        assert all(d == dimensions[0] for d in dimensions)
        assert dimensions[0] == 1536  # OpenAI text-embedding-3-small dimension


def test_search_relevance_filtering():
    """Test filtering search results by relevance score."""
    config = {'provider': 'qdrant', 'host': 'localhost', 'port': 6333}
    
    with patch('src.embedding.embedder.qdrant_client'):
        vector_db = VectorDB(config)
        
        # Mock search results with varying scores
        mock_results = [
            Mock(id='1', score=0.95, payload={'text': 'highly relevant'}),
            Mock(id='2', score=0.85, payload={'text': 'somewhat relevant'}),
            Mock(id='3', score=0.60, payload={'text': 'less relevant'})
        ]
        
        with patch.object(vector_db.client, 'search', return_value=mock_results):
            results = vector_db.search_similar([0.1, 0.2, 0.3], 'test_collection', 
                                               top_k=5, score_threshold=0.8)
            
            # Should only return results with score >= 0.8
            assert len(results) == 2
            assert all(r['score'] >= 0.8 for r in results)
