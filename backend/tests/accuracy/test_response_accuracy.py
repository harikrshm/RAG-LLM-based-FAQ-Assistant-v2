"""
Response Accuracy Tests

Tests to validate that responses are accurate and match expected answers
for known queries.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, List, Any

from backend.services.response_generator import ResponseGenerator
from backend.models.knowledge import KnowledgeChunk, ChunkMetadata, RetrievalResult


# Test dataset with known queries and expected responses
TEST_QUERIES = [
    {
        "query": "What is the expense ratio of HDFC Equity Fund?",
        "expected_keywords": ["expense ratio", "1.5", "1.5%", "HDFC"],
        "expected_sources": ["hdfc", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
    },
    {
        "query": "What is the minimum SIP amount for SBI Bluechip Fund?",
        "expected_keywords": ["minimum", "SIP", "500", "Rs", "SBI"],
        "expected_sources": ["sbi", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
    },
    {
        "query": "What is the exit load for ICICI Prudential Technology Fund?",
        "expected_keywords": ["exit load", "ICICI", "technology"],
        "expected_sources": ["icici", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
    },
    {
        "query": "What is a mutual fund?",
        "expected_keywords": ["mutual fund", "investment", "pool", "money"],
        "expected_sources": [],
        "min_confidence": 0.6,
        "should_have_sources": False,  # General knowledge question
    },
    {
        "query": "What is the lock-in period for ELSS funds?",
        "expected_keywords": ["lock-in", "ELSS", "3 years", "3 year"],
        "expected_sources": ["elss", "groww"],
        "min_confidence": 0.8,
        "should_have_sources": True,
    },
]


@pytest.fixture
def mock_vector_store():
    """Create mock vector store with sample chunks."""
    mock_store = Mock()
    
    # Sample chunks for different queries
    sample_chunks = {
        "expense_ratio": [
            KnowledgeChunk(
                chunk_id="chunk1",
                content="HDFC Equity Fund has an expense ratio of 1.5% per annum. This includes management fees and other operational expenses.",
                source_url="https://groww.in/mutual-funds/hdfc-equity-fund",
                chunk_index=0,
                metadata=ChunkMetadata(
                    source_url="https://groww.in/mutual-funds/hdfc-equity-fund",
                    amc_name="HDFC Mutual Fund",
                    title="HDFC Equity Fund",
                    content_type="fund_page",
                ),
                groww_page_url="https://groww.in/mutual-funds/hdfc-equity-fund",
            ),
        ],
        "sip_amount": [
            KnowledgeChunk(
                chunk_id="chunk2",
                content="The minimum SIP amount for SBI Bluechip Fund is Rs. 500 per month. Investors can start with this amount and increase it later.",
                source_url="https://groww.in/mutual-funds/sbi-bluechip-fund",
                chunk_index=0,
                metadata=ChunkMetadata(
                    source_url="https://groww.in/mutual-funds/sbi-bluechip-fund",
                    amc_name="SBI Mutual Fund",
                    title="SBI Bluechip Fund",
                    content_type="fund_page",
                ),
                groww_page_url="https://groww.in/mutual-funds/sbi-bluechip-fund",
            ),
        ],
        "exit_load": [
            KnowledgeChunk(
                chunk_id="chunk3",
                content="ICICI Prudential Technology Fund has an exit load of 1% if redeemed within 1 year. No exit load after 1 year.",
                source_url="https://groww.in/mutual-funds/icici-technology-fund",
                chunk_index=0,
                metadata=ChunkMetadata(
                    source_url="https://groww.in/mutual-funds/icici-technology-fund",
                    amc_name="ICICI Prudential Mutual Fund",
                    title="ICICI Prudential Technology Fund",
                    content_type="fund_page",
                ),
                groww_page_url="https://groww.in/mutual-funds/icici-technology-fund",
            ),
        ],
        "mutual_fund": [
            KnowledgeChunk(
                chunk_id="chunk4",
                content="A mutual fund is a pool of money collected from multiple investors and invested in stocks, bonds, and other securities.",
                source_url="https://groww.in/learn/mutual-funds",
                chunk_index=0,
                metadata=ChunkMetadata(
                    source_url="https://groww.in/learn/mutual-funds",
                    content_type="blog_article",
                ),
                groww_page_url="https://groww.in/learn/mutual-funds",
            ),
        ],
        "elss_lockin": [
            KnowledgeChunk(
                chunk_id="chunk5",
                content="ELSS (Equity Linked Savings Scheme) funds have a mandatory lock-in period of 3 years from the date of investment.",
                source_url="https://groww.in/learn/elss-funds",
                chunk_index=0,
                metadata=ChunkMetadata(
                    source_url="https://groww.in/learn/elss-funds",
                    content_type="blog_article",
                ),
                groww_page_url="https://groww.in/learn/elss-funds",
            ),
        ],
    }
    
    def search_side_effect(query, **kwargs):
        """Return appropriate chunks based on query."""
        query_lower = query.lower()
        
        if "expense ratio" in query_lower and "hdfc" in query_lower:
            chunks = sample_chunks["expense_ratio"]
        elif "sip" in query_lower and "sbi" in query_lower:
            chunks = sample_chunks["sip_amount"]
        elif "exit load" in query_lower and "icici" in query_lower:
            chunks = sample_chunks["exit_load"]
        elif "mutual fund" in query_lower and "what is" in query_lower:
            chunks = sample_chunks["mutual_fund"]
        elif "elss" in query_lower and "lock-in" in query_lower:
            chunks = sample_chunks["elss_lockin"]
        else:
            chunks = []
        
        return RetrievalResult(
            chunks=chunks,
            similarity_scores=[0.9] * len(chunks) if chunks else [],
            total_retrieved=len(chunks),
            query=query,
            retrieval_time_ms=30.0,
        )
    
    mock_store.search.side_effect = search_side_effect
    return mock_store


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service with accurate responses."""
    mock_llm = Mock()
    
    def generate_side_effect(prompt, **kwargs):
        """Return appropriate response based on prompt."""
        prompt_lower = prompt.lower()
        mock_result = Mock()
        
        if "expense ratio" in prompt_lower and "hdfc" in prompt_lower:
            mock_result.text = "The expense ratio of HDFC Equity Fund is 1.5% per annum. This includes management fees and operational expenses."
        elif "sip" in prompt_lower and "sbi" in prompt_lower:
            mock_result.text = "The minimum SIP amount for SBI Bluechip Fund is Rs. 500 per month."
        elif "exit load" in prompt_lower and "icici" in prompt_lower:
            mock_result.text = "ICICI Prudential Technology Fund has an exit load of 1% if redeemed within 1 year."
        elif "mutual fund" in prompt_lower and "what is" in prompt_lower:
            mock_result.text = "A mutual fund is a pool of money collected from multiple investors and invested in stocks, bonds, and other securities."
        elif "elss" in prompt_lower and "lock-in" in prompt_lower:
            mock_result.text = "ELSS funds have a mandatory lock-in period of 3 years from the date of investment."
        else:
            mock_result.text = "I don't have specific information about this topic."
        
        mock_result.provider = "gemini"
        mock_result.model = "gemini-pro"
        mock_result.finish_reason = "STOP"
        mock_result.prompt_tokens = 100
        mock_result.completion_tokens = 25
        mock_result.total_tokens = 125
        
        return mock_result
    
    mock_llm.generate.side_effect = generate_side_effect
    return mock_llm


class TestResponseAccuracy:
    """Test response accuracy against known queries."""
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_expense_ratio_accuracy(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test accuracy of expense ratio query response."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: []
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        test_case = TEST_QUERIES[0]
        
        result = generator.generate_response(
            query=test_case["query"],
            session_id="test-session",
        )
        
        # Check response contains expected keywords
        response_lower = result["response"].lower()
        assert any(keyword.lower() in response_lower for keyword in test_case["expected_keywords"])
        
        # Check confidence score
        assert result.get("confidence_score", 0) >= test_case["min_confidence"]
        
        # Check sources if required
        if test_case["should_have_sources"]:
            assert len(result.get("sources", [])) > 0
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_sip_amount_accuracy(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test accuracy of SIP amount query response."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: []
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        test_case = TEST_QUERIES[1]
        
        result = generator.generate_response(
            query=test_case["query"],
            session_id="test-session",
        )
        
        response_lower = result["response"].lower()
        assert any(keyword.lower() in response_lower for keyword in test_case["expected_keywords"])
        assert result.get("confidence_score", 0) >= test_case["min_confidence"]
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_all_test_queries_accuracy(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test accuracy for all test queries."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: []
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        accuracy_results = []
        
        for test_case in TEST_QUERIES:
            result = generator.generate_response(
                query=test_case["query"],
                session_id="test-session",
            )
            
            # Check keywords
            response_lower = result["response"].lower()
            keywords_found = sum(
                1 for keyword in test_case["expected_keywords"]
                if keyword.lower() in response_lower
            )
            keyword_accuracy = keywords_found / len(test_case["expected_keywords"])
            
            # Check confidence
            confidence_met = result.get("confidence_score", 0) >= test_case["min_confidence"]
            
            # Check sources
            sources_met = (
                not test_case["should_have_sources"] or
                len(result.get("sources", [])) > 0
            )
            
            accuracy_results.append({
                "query": test_case["query"],
                "keyword_accuracy": keyword_accuracy,
                "confidence_met": confidence_met,
                "sources_met": sources_met,
                "overall_accurate": keyword_accuracy >= 0.5 and confidence_met and sources_met,
            })
        
        # Calculate overall accuracy
        overall_accuracy = sum(
            1 for r in accuracy_results if r["overall_accurate"]
        ) / len(accuracy_results)
        
        # Assert minimum accuracy threshold
        assert overall_accuracy >= 0.8, f"Overall accuracy {overall_accuracy} below threshold 0.8"
        
        # Print results for debugging
        print("\nAccuracy Results:")
        for result in accuracy_results:
            print(f"Query: {result['query']}")
            print(f"  Keyword Accuracy: {result['keyword_accuracy']:.2%}")
            print(f"  Confidence Met: {result['confidence_met']}")
            print(f"  Sources Met: {result['sources_met']}")
            print(f"  Overall Accurate: {result['overall_accurate']}")
            print()


class TestResponseCompleteness:
    """Test that responses are complete and contain necessary information."""
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_response_contains_fund_name(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test that response contains the fund name when querying about a specific fund."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: []
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="What is the expense ratio of HDFC Equity Fund?",
            session_id="test-session",
        )
        
        response_lower = result["response"].lower()
        assert "hdfc" in response_lower, "Response should contain fund name"
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_response_contains_numerical_value(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test that response contains numerical values when querying about metrics."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: []
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="What is the expense ratio of HDFC Equity Fund?",
            session_id="test-session",
        )
        
        response = result["response"]
        # Check for numerical value (1.5 or 1.5%)
        import re
        numbers = re.findall(r'\d+\.?\d*', response)
        assert len(numbers) > 0, "Response should contain numerical value"


class TestSourceAccuracy:
    """Test that sources are accurate and relevant."""
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_sources_match_query_topic(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test that sources are relevant to the query topic."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: [
            {"url": "https://groww.in/mutual-funds/hdfc-equity-fund", "title": "HDFC Equity Fund"}
        ]
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="What is the expense ratio of HDFC Equity Fund?",
            session_id="test-session",
        )
        
        sources = result.get("sources", [])
        if sources:
            # Check that source URL contains relevant keywords
            source_urls = " ".join([s.get("url", "") for s in sources]).lower()
            assert "hdfc" in source_urls or "equity" in source_urls


class TestResponseConsistency:
    """Test that responses are consistent across multiple runs."""
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_response_consistency(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
        mock_vector_store,
        mock_llm_service,
    ):
        """Test that responses are consistent for the same query."""
        mock_get_rag.return_value = Mock()
        mock_get_rag.return_value.retrieve = mock_vector_store.search
        mock_get_rag.return_value.get_context_window = lambda chunks, **kwargs: "Context"
        mock_get_rag.return_value.get_sources = lambda chunks: []
        mock_get_llm.return_value = mock_llm_service
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        mock_get_guardrails.return_value = Mock()
        mock_get_guardrails.return_value.check_query = lambda q: (True, None)
        mock_get_guardrails.return_value.check_response = lambda r: (True, [])
        
        generator = ResponseGenerator()
        query = "What is the expense ratio of HDFC Equity Fund?"
        
        # Run query multiple times
        results = []
        for _ in range(3):
            result = generator.generate_response(
                query=query,
                session_id="test-session",
            )
            results.append(result)
        
        # Check that all responses contain key information
        for result in results:
            response_lower = result["response"].lower()
            assert "expense ratio" in response_lower or "1.5" in response_lower
            assert result.get("confidence_score", 0) > 0

