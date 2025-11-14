"""
Unit tests for Vector Store Service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import chromadb
from chromadb.config import Settings

from backend.services.vector_store import VectorStoreService
from backend.models.knowledge import KnowledgeChunk, ChunkMetadata, RetrievalResult
from backend.exceptions import (
    VectorStoreConnectionError,
    VectorStoreQueryError,
    VectorStoreNotInitializedError,
    EmbeddingGenerationError,
)


@pytest.fixture
def mock_chromadb_collection():
    """Create a mock ChromaDB collection."""
    mock_collection = Mock()
    mock_collection.count.return_value = 100
    mock_collection.query.return_value = {
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }
    mock_collection.get.return_value = {
        "ids": [],
        "documents": [],
        "metadatas": [],
    }
    return mock_collection


@pytest.fixture
def mock_chromadb_client(mock_chromadb_collection):
    """Create a mock ChromaDB client."""
    mock_client = Mock()
    mock_client.get_collection.return_value = mock_chromadb_collection
    return mock_client


@pytest.fixture
def mock_embedding_model():
    """Create a mock embedding model."""
    mock_model = Mock()
    mock_model.encode.return_value = [0.1] * 384  # Mock embedding vector
    mock_model.get_sentence_embedding_dimension.return_value = 384
    return mock_model


@pytest.fixture
def vector_store(mock_chromadb_client, mock_embedding_model):
    """Create a vector store service with mocked dependencies."""
    with patch("backend.services.vector_store.chromadb.PersistentClient", return_value=mock_chromadb_client):
        with patch("backend.services.vector_store.SentenceTransformer", return_value=mock_embedding_model):
            with patch("backend.services.vector_store.settings") as mock_settings:
                mock_settings.VECTORDB_PATH = "test/path"
                mock_settings.VECTORDB_COLLECTION = "test_collection"
                mock_settings.EMBEDDING_MODEL = "test-model"
                mock_settings.RAG_SIMILARITY_THRESHOLD = 0.5
                
                store = VectorStoreService(
                    persist_directory="test/path",
                    collection_name="test_collection",
                    embedding_model="test-model",
                )
                store.collection = mock_chromadb_client.get_collection.return_value
                return store


class TestVectorStoreInitialization:
    """Test vector store initialization."""
    
    def test_init_success(self, mock_chromadb_client, mock_embedding_model):
        """Test successful initialization."""
        with patch("backend.services.vector_store.chromadb.PersistentClient", return_value=mock_chromadb_client):
            with patch("backend.services.vector_store.SentenceTransformer", return_value=mock_embedding_model):
                with patch("backend.services.vector_store.settings") as mock_settings:
                    mock_settings.VECTORDB_PATH = "test/path"
                    mock_settings.VECTORDB_COLLECTION = "test_collection"
                    mock_settings.EMBEDDING_MODEL = "test-model"
                    
                    store = VectorStoreService()
                    
                    assert store.persist_directory == "test/path"
                    assert store.collection_name == "test_collection"
                    assert store.embedding_model_name == "test-model"
    
    def test_init_collection_not_found(self, mock_chromadb_client):
        """Test initialization when collection doesn't exist."""
        mock_chromadb_client.get_collection.side_effect = ValueError("Collection not found")
        
        with patch("backend.services.vector_store.chromadb.PersistentClient", return_value=mock_chromadb_client):
            with patch("backend.services.vector_store.settings") as mock_settings:
                mock_settings.VECTORDB_PATH = "test/path"
                mock_settings.VECTORDB_COLLECTION = "test_collection"
                
                with pytest.raises(VectorStoreNotInitializedError):
                    VectorStoreService()
    
    def test_init_connection_error(self):
        """Test initialization with connection error."""
        with patch("backend.services.vector_store.chromadb.PersistentClient") as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            with patch("backend.services.vector_store.settings") as mock_settings:
                mock_settings.VECTORDB_PATH = "test/path"
                mock_settings.VECTORDB_COLLECTION = "test_collection"
                
                with pytest.raises(VectorStoreConnectionError):
                    VectorStoreService()
    
    def test_init_embedding_model_error(self, mock_chromadb_client):
        """Test initialization when embedding model fails to load."""
        with patch("backend.services.vector_store.chromadb.PersistentClient", return_value=mock_chromadb_client):
            with patch("backend.services.vector_store.SentenceTransformer") as mock_transformer:
                mock_transformer.side_effect = Exception("Model load failed")
                
                with patch("backend.services.vector_store.settings") as mock_settings:
                    mock_settings.VECTORDB_PATH = "test/path"
                    mock_settings.VECTORDB_COLLECTION = "test_collection"
                    mock_settings.EMBEDDING_MODEL = "test-model"
                    
                    with pytest.raises(EmbeddingGenerationError):
                        VectorStoreService()


class TestVectorStoreEncoding:
    """Test query encoding functionality."""
    
    def test_encode_query(self, vector_store, mock_embedding_model):
        """Test query encoding."""
        embedding = vector_store.encode_query("test query")
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        mock_embedding_model.encode.assert_called_once()
    
    def test_encode_query_no_model(self, vector_store):
        """Test encoding when model is not initialized."""
        vector_store.embedding_model = None
        
        with pytest.raises(VectorStoreNotInitializedError):
            vector_store.encode_query("test")
    
    def test_encode_query_error(self, vector_store, mock_embedding_model):
        """Test encoding error handling."""
        mock_embedding_model.encode.side_effect = Exception("Encoding failed")
        
        with pytest.raises(EmbeddingGenerationError):
            vector_store.encode_query("test")


class TestVectorStoreSearch:
    """Test search functionality."""
    
    def test_search_basic(self, vector_store, mock_chromadb_collection, mock_embedding_model):
        """Test basic search."""
        # Setup mock return value
        mock_chromadb_collection.query.return_value = {
            "ids": [["chunk1", "chunk2"]],
            "documents": [
                ["Content 1", "Content 2"],
            ],
            "metadatas": [
                [
                    {"source_url": "https://example.com/1", "amc_name": "Test AMC"},
                    {"source_url": "https://example.com/2", "amc_name": "Test AMC"},
                ],
            ],
            "distances": [[0.2, 0.3]],  # Similarity = 1 - distance
        }
        
        result = vector_store.search("test query", top_k=2)
        
        assert isinstance(result, RetrievalResult)
        assert len(result.chunks) == 2
        assert len(result.similarity_scores) == 2
        assert result.similarity_scores[0] == 0.8  # 1 - 0.2
        assert result.similarity_scores[1] == 0.7  # 1 - 0.3
        mock_chromadb_collection.query.assert_called_once()
    
    def test_search_with_filters(self, vector_store, mock_chromadb_collection):
        """Test search with metadata filters."""
        mock_chromadb_collection.query.return_value = {
            "ids": [["chunk1"]],
            "documents": [["Content"]],
            "metadatas": [[{"source_url": "https://example.com", "amc_name": "Test AMC"}]],
            "distances": [[0.2]],
        }
        
        filters = {"amc_name": "Test AMC"}
        result = vector_store.search("test", filters=filters)
        
        call_args = mock_chromadb_collection.query.call_args
        assert call_args[1]["where"] == filters
    
    def test_search_with_threshold(self, vector_store, mock_chromadb_collection):
        """Test search with similarity threshold."""
        mock_chromadb_collection.query.return_value = {
            "ids": [["chunk1", "chunk2", "chunk3"]],
            "documents": [["Content 1", "Content 2", "Content 3"]],
            "metadatas": [
                [
                    {"source_url": "https://example.com/1"},
                    {"source_url": "https://example.com/2"},
                    {"source_url": "https://example.com/3"},
                ],
            ],
            "distances": [[0.2, 0.6, 0.4]],  # Only first passes threshold of 0.5
        }
        
        result = vector_store.search("test", similarity_threshold=0.5)
        
        # Only chunk1 should pass (similarity 0.8 > 0.5)
        assert len(result.chunks) == 1
    
    def test_search_no_results(self, vector_store, mock_chromadb_collection):
        """Test search with no results."""
        mock_chromadb_collection.query.return_value = {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
        
        result = vector_store.search("test")
        
        assert len(result.chunks) == 0
        assert len(result.similarity_scores) == 0
    
    def test_search_exception(self, vector_store, mock_chromadb_collection):
        """Test search exception handling."""
        mock_chromadb_collection.query.side_effect = Exception("Query failed")
        
        with pytest.raises(VectorStoreQueryError):
            vector_store.search("test")
    
    def test_search_by_embedding(self, vector_store, mock_chromadb_collection):
        """Test search using pre-computed embedding."""
        mock_chromadb_collection.query.return_value = {
            "ids": [["chunk1"]],
            "documents": [["Content"]],
            "metadatas": [[{"source_url": "https://example.com"}]],
            "distances": [[0.2]],
        }
        
        embedding = [0.1] * 384
        result = vector_store.search_by_embedding(embedding, top_k=1)
        
        assert len(result.chunks) == 1
        call_args = mock_chromadb_collection.query.call_args
        assert call_args[1]["query_embeddings"] == [embedding]


class TestVectorStoreRetrieval:
    """Test chunk retrieval functionality."""
    
    def test_get_chunk_by_id(self, vector_store, mock_chromadb_collection):
        """Test retrieving chunk by ID."""
        mock_chromadb_collection.get.return_value = {
            "ids": ["chunk1"],
            "documents": ["Test content"],
            "metadatas": [{"source_url": "https://example.com", "amc_name": "Test AMC"}],
        }
        
        chunk = vector_store.get_chunk_by_id("chunk1")
        
        assert isinstance(chunk, KnowledgeChunk)
        assert chunk.chunk_id == "chunk1"
        assert chunk.content == "Test content"
    
    def test_get_chunk_by_id_not_found(self, vector_store, mock_chromadb_collection):
        """Test retrieving non-existent chunk."""
        mock_chromadb_collection.get.return_value = {
            "ids": [],
            "documents": [],
            "metadatas": [],
        }
        
        chunk = vector_store.get_chunk_by_id("nonexistent")
        
        assert chunk is None
    
    def test_get_chunks_by_source(self, vector_store, mock_chromadb_collection):
        """Test retrieving chunks by source URL."""
        mock_chromadb_collection.get.return_value = {
            "ids": ["chunk1", "chunk2"],
            "documents": ["Content 1", "Content 2"],
            "metadatas": [
                {"source_url": "https://example.com"},
                {"source_url": "https://example.com"},
            ],
        }
        
        chunks = vector_store.get_chunks_by_source("https://example.com")
        
        assert len(chunks) == 2
        assert all(chunk.source_url == "https://example.com" for chunk in chunks)
    
    def test_get_chunks_by_amc(self, vector_store, mock_chromadb_collection):
        """Test retrieving chunks by AMC name."""
        mock_chromadb_collection.get.return_value = {
            "ids": ["chunk1"],
            "documents": ["Content"],
            "metadatas": [{"source_url": "https://example.com", "amc_name": "Test AMC"}],
        }
        
        chunks = vector_store.get_chunks_by_amc("Test AMC")
        
        assert len(chunks) == 1
        assert chunks[0].metadata.amc_name == "Test AMC"


class TestVectorStoreHelpers:
    """Test helper methods."""
    
    def test_create_knowledge_chunk(self, vector_store):
        """Test knowledge chunk creation."""
        chunk = vector_store._create_knowledge_chunk(
            chunk_id="test",
            content="Test content",
            metadata={
                "source_url": "https://example.com",
                "amc_name": "Test AMC",
                "title": "Test Title",
                "content_type": "fund_page",
            },
        )
        
        assert isinstance(chunk, KnowledgeChunk)
        assert chunk.chunk_id == "test"
        assert chunk.content == "Test content"
        assert chunk.metadata.amc_name == "Test AMC"
        assert chunk.metadata.title == "Test Title"
    
    def test_get_collection_stats(self, vector_store, mock_chromadb_collection):
        """Test collection statistics."""
        mock_chromadb_collection.get.return_value = {
            "ids": ["chunk1"],
            "metadatas": [{"source_url": "https://example.com", "amc_name": "Test AMC"}],
        }
        
        stats = vector_store.get_collection_stats()
        
        assert stats["collection_name"] == "test_collection"
        assert stats["total_chunks"] == 100
        assert stats["embedding_dimension"] == 384
        assert "metadata_fields" in stats
    
    def test_health_check_healthy(self, vector_store, mock_chromadb_collection):
        """Test health check when healthy."""
        health = vector_store.health_check()
        
        assert health["status"] == "healthy"
        assert health["collection_accessible"] is True
        assert health["document_count"] == 100
        assert health["embedding_model_loaded"] is True
    
    def test_health_check_unhealthy(self, vector_store, mock_chromadb_collection):
        """Test health check when unhealthy."""
        mock_chromadb_collection.count.side_effect = Exception("Connection failed")
        
        health = vector_store.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health


class TestVectorStoreSingleton:
    """Test singleton pattern."""
    
    def test_get_vector_store_singleton(self, mock_chromadb_client, mock_embedding_model):
        """Test that get_vector_store returns singleton."""
        with patch("backend.services.vector_store.chromadb.PersistentClient", return_value=mock_chromadb_client):
            with patch("backend.services.vector_store.SentenceTransformer", return_value=mock_embedding_model):
                with patch("backend.services.vector_store.settings") as mock_settings:
                    mock_settings.VECTORDB_PATH = "test/path"
                    mock_settings.VECTORDB_COLLECTION = "test_collection"
                    mock_settings.EMBEDDING_MODEL = "test-model"
                    
                    from backend.services.vector_store import get_vector_store
                    
                    instance1 = get_vector_store()
                    instance2 = get_vector_store()
                    
                    assert instance1 is instance2

