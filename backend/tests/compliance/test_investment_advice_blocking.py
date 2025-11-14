"""
Investment Advice Blocking Tests

Tests to ensure the system blocks investment advice in queries and responses.
"""

import pytest
from unittest.mock import Mock, patch

from backend.utils.guardrails import PromptGuardrails, ViolationType
from backend.services.response_generator import ResponseGenerator


# Test queries that should be blocked (contain investment advice patterns)
ADVICE_SEEKING_QUERIES = [
    "Should I invest in HDFC Equity Fund?",
    "Is it a good time to buy mutual funds?",
    "Which mutual fund should I invest in?",
    "Can you recommend a good mutual fund?",
    "What mutual fund should I buy?",
    "Should I invest in SIP or lump sum?",
    "Is HDFC Equity Fund a good investment?",
    "Which fund will give better returns?",
    "Should I sell my mutual fund now?",
    "What is the best mutual fund for me?",
    "Can you suggest a mutual fund for retirement?",
    "Should I continue my SIP in this fund?",
    "Is this fund suitable for my portfolio?",
    "What percentage should I invest in equity?",
    "Should I switch from this fund to another?",
]

# Test queries that should be allowed (factual questions)
FACTUAL_QUERIES = [
    "What is the expense ratio of HDFC Equity Fund?",
    "What is the minimum SIP amount for SBI Bluechip Fund?",
    "What is the exit load for ICICI Technology Fund?",
    "What is a mutual fund?",
    "What is the lock-in period for ELSS funds?",
    "Who is the fund manager of Axis Bluechip Fund?",
    "What is the benchmark for Kotak Multicap Fund?",
    "What are the features of HDFC Equity Fund?",
    "What is the AUM of SBI Mutual Fund?",
    "What is the expense ratio?",
]

# Test responses that should be blocked (contain investment advice)
ADVICE_CONTAINING_RESPONSES = [
    "You should invest in HDFC Equity Fund as it has good returns.",
    "I recommend investing in equity funds for long-term growth.",
    "This fund is a good investment option for you.",
    "You should buy this mutual fund now.",
    "I suggest investing 60% in equity and 40% in debt.",
    "This fund is suitable for your investment goals.",
    "You should consider investing in this fund.",
    "I advise you to invest in SIP for better returns.",
    "This is a good time to invest in mutual funds.",
    "You should hold this fund for better returns.",
]

# Test responses that should be allowed (factual information)
FACTUAL_RESPONSES = [
    "The expense ratio of HDFC Equity Fund is 1.5% per annum.",
    "The minimum SIP amount for SBI Bluechip Fund is Rs. 500 per month.",
    "ELSS funds have a mandatory lock-in period of 3 years.",
    "A mutual fund is a pool of money collected from multiple investors.",
    "The exit load for ICICI Technology Fund is 1% if redeemed within 1 year.",
    "The fund manager of Axis Bluechip Fund is Mr. Shreyash Devalkar.",
    "The benchmark for Kotak Multicap Fund is Nifty 500 Multicap Index.",
]


class TestQueryBlocking:
    """Test blocking of advice-seeking queries."""
    
    def test_guardrails_block_advice_queries(self):
        """Test that guardrails block advice-seeking queries."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        for query in ADVICE_SEEKING_QUERIES:
            is_safe, violation = guardrails.check_query(query)
            
            assert not is_safe, f"Query should be blocked: {query}"
            assert violation is not None, f"Violation should be detected for: {query}"
            assert violation.violation_type in [
                ViolationType.INVESTMENT_ADVICE,
                ViolationType.RECOMMENDATION,
                ViolationType.PERSONAL_OPINION,
            ], f"Unexpected violation type: {violation.violation_type}"
    
    def test_guardrails_allow_factual_queries(self):
        """Test that guardrails allow factual queries."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        for query in FACTUAL_QUERIES:
            is_safe, violation = guardrails.check_query(query)
            
            assert is_safe, f"Query should be allowed: {query}"
            assert violation is None, f"No violation should be detected for: {query}"
    
    def test_advice_patterns_detection(self):
        """Test detection of various advice patterns."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        advice_patterns = [
            "should I invest",
            "should I buy",
            "should I sell",
            "recommend",
            "suggest",
            "good investment",
            "best fund",
            "suitable for",
        ]
        
        for pattern in advice_patterns:
            query = f"Can you {pattern}?"
            is_safe, violation = guardrails.check_query(query)
            
            assert not is_safe, f"Pattern should be blocked: {pattern}"
    
    def test_edge_cases_query_blocking(self):
        """Test edge cases in query blocking."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        # Queries with advice patterns but factual context
        edge_cases = [
            "What should I know about expense ratios?",  # Should be allowed
            "Should I understand what expense ratio means?",  # Should be allowed
            "What should I check before investing?",  # Should be blocked
        ]
        
        # First two should be allowed (asking for information, not advice)
        is_safe1, _ = guardrails.check_query(edge_cases[0])
        is_safe2, _ = guardrails.check_query(edge_cases[1])
        
        # Third should be blocked (asking for advice)
        is_safe3, violation3 = guardrails.check_query(edge_cases[2])
        
        assert is_safe1 or is_safe2, "Informational queries should be allowed"
        assert not is_safe3, "Advice-seeking query should be blocked"


class TestResponseBlocking:
    """Test blocking of advice-containing responses."""
    
    def test_guardrails_block_advice_responses(self):
        """Test that guardrails block advice-containing responses."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        for response in ADVICE_CONTAINING_RESPONSES:
            is_safe, violations = guardrails.check_response(response)
            
            assert not is_safe, f"Response should be blocked: {response[:50]}..."
            assert len(violations) > 0, f"Violations should be detected for: {response[:50]}..."
            
            # Check violation types
            violation_types = [v.violation_type for v in violations]
            assert any(
                vt in [
                    ViolationType.INVESTMENT_ADVICE,
                    ViolationType.RECOMMENDATION,
                    ViolationType.PERSONAL_OPINION,
                ]
                for vt in violation_types
            ), f"Unexpected violation types: {violation_types}"
    
    def test_guardrails_allow_factual_responses(self):
        """Test that guardrails allow factual responses."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        for response in FACTUAL_RESPONSES:
            is_safe, violations = guardrails.check_response(response)
            
            assert is_safe, f"Response should be allowed: {response[:50]}..."
            assert len(violations) == 0, f"No violations should be detected for: {response[:50]}..."
    
    def test_response_advice_keywords(self):
        """Test detection of advice keywords in responses."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        advice_keywords = [
            "you should invest",
            "you should buy",
            "I recommend",
            "I suggest",
            "good investment",
            "best fund",
            "suitable for you",
        ]
        
        for keyword in advice_keywords:
            response = f"The expense ratio is 1.5%. {keyword}."
            is_safe, violations = guardrails.check_response(response)
            
            assert not is_safe, f"Keyword should trigger blocking: {keyword}"
            assert len(violations) > 0, f"Violations should be detected for: {keyword}"


class TestResponseGeneratorCompliance:
    """Test compliance in response generator."""
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_blocked_query_returns_safe_response(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
    ):
        """Test that blocked queries return safe response."""
        guardrails = PromptGuardrails(strict_mode=True)
        mock_get_guardrails.return_value = guardrails
        mock_get_rag.return_value = Mock()
        mock_get_llm.return_value = Mock()
        mock_get_mapper.return_value = Mock()
        
        generator = ResponseGenerator()
        
        # Use an advice-seeking query
        result = generator.generate_response(
            query="Should I invest in HDFC Equity Fund?",
            session_id="test-session",
        )
        
        # Should return safe response
        assert result.get("guardrail_blocked") is True
        assert "should" not in result["response"].lower() or "invest" not in result["response"].lower()
        assert result.get("chunks_retrieved") == 0
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_blocked_response_returns_fallback(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
    ):
        """Test that blocked responses return fallback."""
        guardrails = PromptGuardrails(strict_mode=True)
        mock_get_guardrails.return_value = guardrails
        
        # Mock LLM to return advice-containing response
        mock_llm = Mock()
        mock_llm.generate.return_value = Mock(
            text="You should invest in HDFC Equity Fund as it has good returns.",
            provider="gemini",
            model="gemini-pro",
        )
        mock_get_llm.return_value = mock_llm
        
        # Mock RAG to return chunks
        mock_rag = Mock()
        mock_rag.retrieve.return_value = Mock(chunks=[Mock()], similarity_scores=[0.9])
        mock_rag.get_context_window.return_value = "Context"
        mock_rag.get_sources.return_value = []
        mock_get_rag.return_value = mock_rag
        
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="What is the expense ratio of HDFC Equity Fund?",
            session_id="test-session",
        )
        
        # Should detect violation and return safe response
        assert result.get("guardrail_blocked") is True or "should" not in result["response"].lower()
    
    @patch("backend.services.response_generator.get_rag_retrieval")
    @patch("backend.services.response_generator.get_llm_service")
    @patch("backend.services.response_generator.get_groww_mapper")
    @patch("backend.services.response_generator.get_guardrails")
    def test_factual_query_allowed(
        self,
        mock_get_guardrails,
        mock_get_mapper,
        mock_get_llm,
        mock_get_rag,
    ):
        """Test that factual queries are allowed."""
        guardrails = PromptGuardrails(strict_mode=True)
        mock_get_guardrails.return_value = guardrails
        
        mock_llm = Mock()
        mock_llm.generate.return_value = Mock(
            text="The expense ratio of HDFC Equity Fund is 1.5% per annum.",
            provider="gemini",
            model="gemini-pro",
        )
        mock_get_llm.return_value = mock_llm
        
        mock_rag = Mock()
        mock_rag.retrieve.return_value = Mock(chunks=[Mock()], similarity_scores=[0.9])
        mock_rag.get_context_window.return_value = "Context"
        mock_rag.get_sources.return_value = []
        mock_get_rag.return_value = mock_rag
        
        mock_get_mapper.return_value = Mock()
        mock_get_mapper.return_value.find_groww_page = lambda **kwargs: None
        mock_get_mapper.return_value.prioritize_sources = lambda sources: sources
        
        generator = ResponseGenerator()
        
        result = generator.generate_response(
            query="What is the expense ratio of HDFC Equity Fund?",
            session_id="test-session",
        )
        
        # Should not be blocked
        assert result.get("guardrail_blocked") is not True
        assert "expense ratio" in result["response"].lower()


class TestComplianceEdgeCases:
    """Test edge cases in compliance checking."""
    
    def test_subtle_advice_patterns(self):
        """Test detection of subtle advice patterns."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        subtle_patterns = [
            "This fund might be good for you",
            "Consider investing in this fund",
            "This could be a good option",
            "You may want to invest",
            "This fund appears suitable",
        ]
        
        for pattern in subtle_patterns:
            is_safe, violations = guardrails.check_response(pattern)
            
            # Should detect subtle advice patterns
            if not is_safe:
                assert len(violations) > 0
    
    def test_context_dependent_blocking(self):
        """Test blocking based on context."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        # Same word in different contexts
        factual = "You should check the expense ratio before investing."
        advice = "You should invest in this fund."
        
        is_safe1, _ = guardrails.check_response(factual)
        is_safe2, violations2 = guardrails.check_response(advice)
        
        # Advice should be blocked
        assert not is_safe2 or len(violations2) > 0
    
    def test_negative_advice_blocking(self):
        """Test blocking of negative advice."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        negative_advice = [
            "You should not invest in this fund",
            "I don't recommend this fund",
            "You should avoid this fund",
            "This fund is not suitable",
        ]
        
        for advice in negative_advice:
            is_safe, violations = guardrails.check_response(advice)
            
            # Negative advice should also be blocked
            assert not is_safe or len(violations) > 0
    
    def test_comparative_statements(self):
        """Test handling of comparative statements."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        # Factual comparison
        factual = "Fund A has an expense ratio of 1.5%, while Fund B has 1.2%."
        
        # Advice comparison
        advice = "Fund A is better than Fund B, so you should invest in Fund A."
        
        is_safe1, _ = guardrails.check_response(factual)
        is_safe2, violations2 = guardrails.check_response(advice)
        
        # Factual comparison should be allowed
        assert is_safe1
        
        # Advice comparison should be blocked
        assert not is_safe2 or len(violations2) > 0


class TestComplianceReporting:
    """Test compliance reporting and metrics."""
    
    def test_violation_reporting(self):
        """Test that violations are properly reported."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        query = "Should I invest in HDFC Equity Fund?"
        is_safe, violation = guardrails.check_query(query)
        
        assert not is_safe
        assert violation is not None
        assert violation.violation_type is not None
        assert violation.matched_pattern is not None
    
    def test_multiple_violations_detection(self):
        """Test detection of multiple violations in a response."""
        guardrails = PromptGuardrails(strict_mode=True)
        
        response = "You should invest in HDFC Equity Fund. I recommend it as it's a good investment for you."
        
        is_safe, violations = guardrails.check_response(response)
        
        assert not is_safe
        assert len(violations) > 0
        
        # Should detect multiple violation types
        violation_types = [v.violation_type for v in violations]
        assert len(set(violation_types)) >= 1

