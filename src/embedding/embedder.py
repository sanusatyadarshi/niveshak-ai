"""
Vector embedding and database interface module.

This module handles:
- Text embedding generation using various providers (OpenAI, etc.)
- Vector database operations (Qdrant, Weaviate, etc.)
- Similarity search and retrieval
- Knowledge base management
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np
import yaml
from dataclasses import dataclass
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, Range

from ..utils import logger


@dataclass
class Document:
    """Represents a document with its content and metadata."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        pass


class OpenAIEmbedder(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """Initialize OpenAI embedder."""
        self.api_key = api_key
        self.model = model
        
        # Initialize OpenAI client
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {str(e)}")
            raise


class OllamaEmbedder(EmbeddingProvider):
    """Ollama embedding provider for local embeddings."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "nomic-embed-text"):
        """Initialize Ollama embedder."""
        self.base_url = base_url
        self.model = model
        
        # Initialize Ollama client
        import ollama
        self.client = ollama.Client(host=base_url)
        
        # Test connection
        try:
            # Check if model is available
            models = self.client.list()
            model_names = [m.model for m in models.models]
            if self.model not in model_names and f"{self.model}:latest" not in model_names:
                logger.warning(f"Model {self.model} not found. Available models: {model_names}")
                # Try to pull the model
                logger.info(f"Attempting to pull model {self.model}...")
                self.client.pull(self.model)
        except Exception as e:
            logger.error(f"Failed to initialize Ollama embedder: {str(e)}")
            raise
        
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            return response.embedding
        except Exception as e:
            logger.error(f"Failed to generate Ollama embedding: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Failed to generate embedding for text batch: {str(e)}")
                raise
        return embeddings


class VectorStore(ABC):
    """Abstract base class for vector database operations."""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents."""
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        pass


class QdrantVectorStore(VectorStore):
    """Qdrant vector database implementation."""
    
    def __init__(self, host: str, port: int, collection_name: str, vector_size: int):
        """Initialize Qdrant vector store."""
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.vector_size = vector_size
        
        # Try to connect to remote Qdrant first, fallback to in-memory
        try:
            self.client = QdrantClient(host=host, port=port)
            # Test connection
            self.client.get_collections()
            logger.info(f"Connected to Qdrant at {host}:{port}")
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant server at {host}:{port}: {e}")
            logger.info("Falling back to in-memory Qdrant instance")
            # Use in-memory Qdrant instance
            self.client = QdrantClient(":memory:")
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()
        
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise
        
    def add_documents(self, documents: List[Document]) -> bool:
        """Add documents to Qdrant collection."""
        try:
            points = []
            for doc in documents:
                point = PointStruct(
                    id=str(uuid.uuid4()),  # Generate unique ID
                    vector=doc.embedding,
                    payload={
                        "content": doc.content,
                        "metadata": doc.metadata
                    }
                )
                points.append(point)
            
            # Upload points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(documents)} documents to Qdrant collection {self.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents to Qdrant: {str(e)}")
            return False
    
    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Document, float]]:
        """Search for similar documents in Qdrant."""
        try:
            # Search for similar vectors
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                with_payload=True,
                with_vectors=False  # We don't need vectors in response
            )
            
            # Convert results to Document objects
            results = []
            for scored_point in search_result:
                doc = Document(
                    id=str(scored_point.id),
                    content=scored_point.payload["content"],
                    metadata=scored_point.payload["metadata"],
                    embedding=None  # We don't need the embedding for search results
                )
                results.append((doc, scored_point.score))
            
            logger.info(f"Found {len(results)} similar documents in Qdrant")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search Qdrant: {str(e)}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from Qdrant."""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[doc_id]
            )
            logger.info(f"Deleted document {doc_id} from Qdrant")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document from Qdrant: {str(e)}")
            return False
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document from Qdrant."""
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id],
                with_payload=True,
                with_vectors=True
            )
            
            if result:
                point = result[0]
                return Document(
                    id=str(point.id),
                    content=point.payload["content"],
                    metadata=point.payload["metadata"],
                    embedding=point.vector
                )
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve document from Qdrant: {str(e)}")
            return None


class EmbeddingManager:
    """Manages embedding generation and vector store operations."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize embedding manager with configuration."""
        self.config = config
        self.embedder = self._create_embedder()
        self.vector_store = self._create_vector_store()
        
    def _create_embedder(self) -> EmbeddingProvider:
        """Create embedding provider based on configuration."""
        provider = self.config['embedding']['provider']
        
        if provider == 'openai':
            return OpenAIEmbedder(
                api_key=os.getenv('OPENAI_API_KEY'),
                model=self.config['embedding']['model']
            )
        elif provider == 'ollama':
            return OllamaEmbedder(
                base_url=self.config['embedding']['base_url'],
                model=self.config['embedding']['model']
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
    
    def _create_vector_store(self) -> VectorStore:
        """Create vector store based on configuration."""
        provider = self.config['vector_db']['provider']
        
        if provider == 'qdrant':
            config = self.config['vector_db']['qdrant']
            return QdrantVectorStore(
                host=config['host'],
                port=config['port'],
                collection_name=config['collection_name'],
                vector_size=config['vector_size']
            )
        else:
            raise ValueError(f"Unsupported vector store provider: {provider}")
    
    def add_text_documents(self, texts: List[str], metadata_list: List[Dict[str, Any]]) -> bool:
        """Add text documents to the knowledge base."""
        try:
            # Generate embeddings
            embeddings = self.embedder.embed_batch(texts)
            
            # Create document objects
            documents = []
            for i, (text, metadata, embedding) in enumerate(zip(texts, metadata_list, embeddings)):
                doc = Document(
                    id=f"doc_{i}_{hash(text)}",
                    content=text,
                    metadata=metadata,
                    embedding=embedding
                )
                documents.append(doc)
            
            # Add to vector store
            return self.vector_store.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Failed to add text documents: {str(e)}")
            return False
    
    def search_knowledge_base(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Search the knowledge base for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of tuples (content, metadata, score)
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_text(query)
            
            # Search vector store
            results = self.vector_store.search_similar(query_embedding, top_k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append((doc.content, doc.metadata, score))
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search knowledge base: {str(e)}")
            return []


def create_embedding_manager(config_path: str = "config/settings.yaml") -> EmbeddingManager:
    """
    Create and return an embedding manager instance.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        EmbeddingManager instance
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return EmbeddingManager(config)
