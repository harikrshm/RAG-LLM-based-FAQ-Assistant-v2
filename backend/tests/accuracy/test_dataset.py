"""
Test Dataset for Response Accuracy Testing

Contains known queries and expected responses for accuracy validation.
"""

from typing import Dict, List, Any

# Test dataset structure
# Each entry contains:
# - query: The user's question
# - expected_keywords: Keywords that should appear in the response
# - expected_sources: Source types/keywords that should be present
# - min_confidence: Minimum confidence score threshold
# - should_have_sources: Whether sources are required
# - expected_answer_template: Template or pattern for expected answer

ACCURACY_TEST_DATASET: List[Dict[str, Any]] = [
    {
        "id": "expense_ratio_hdfc",
        "query": "What is the expense ratio of HDFC Equity Fund?",
        "expected_keywords": ["expense ratio", "1.5", "1.5%", "HDFC", "Equity Fund"],
        "expected_sources": ["hdfc", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
        "expected_answer_template": "expense ratio.*1.5.*%",
        "category": "fund_details",
    },
    {
        "id": "sip_amount_sbi",
        "query": "What is the minimum SIP amount for SBI Bluechip Fund?",
        "expected_keywords": ["minimum", "SIP", "500", "Rs", "SBI", "Bluechip"],
        "expected_sources": ["sbi", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
        "expected_answer_template": "minimum.*SIP.*500",
        "category": "fund_details",
    },
    {
        "id": "exit_load_icici",
        "query": "What is the exit load for ICICI Prudential Technology Fund?",
        "expected_keywords": ["exit load", "ICICI", "Technology", "1%"],
        "expected_sources": ["icici", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
        "expected_answer_template": "exit load.*1.*%",
        "category": "fund_details",
    },
    {
        "id": "mutual_fund_definition",
        "query": "What is a mutual fund?",
        "expected_keywords": ["mutual fund", "investment", "pool", "money", "securities"],
        "expected_sources": [],
        "min_confidence": 0.6,
        "should_have_sources": False,
        "expected_answer_template": "pool.*money.*invest",
        "category": "general_info",
    },
    {
        "id": "elss_lockin",
        "query": "What is the lock-in period for ELSS funds?",
        "expected_keywords": ["lock-in", "ELSS", "3 years", "3 year", "mandatory"],
        "expected_sources": ["elss", "groww"],
        "min_confidence": 0.8,
        "should_have_sources": True,
        "expected_answer_template": "lock.*in.*3.*year",
        "category": "fund_details",
    },
    {
        "id": "amc_overview",
        "query": "Tell me about HDFC Mutual Fund",
        "expected_keywords": ["HDFC", "Mutual Fund", "AMC"],
        "expected_sources": ["hdfc", "groww"],
        "min_confidence": 0.6,
        "should_have_sources": True,
        "expected_answer_template": "HDFC.*Mutual Fund",
        "category": "amc_overview",
    },
    {
        "id": "fund_manager",
        "query": "Who is the fund manager of Axis Bluechip Fund?",
        "expected_keywords": ["fund manager", "Axis", "Bluechip"],
        "expected_sources": ["axis", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
        "expected_answer_template": "fund manager",
        "category": "fund_details",
    },
    {
        "id": "benchmark",
        "query": "What is the benchmark for Kotak Standard Multicap Fund?",
        "expected_keywords": ["benchmark", "Kotak", "Multicap"],
        "expected_sources": ["kotak", "groww"],
        "min_confidence": 0.7,
        "should_have_sources": True,
        "expected_answer_template": "benchmark",
        "category": "fund_details",
    },
]


def get_test_cases_by_category(category: str) -> List[Dict[str, Any]]:
    """Get test cases filtered by category."""
    return [tc for tc in ACCURACY_TEST_DATASET if tc.get("category") == category]


def get_test_case_by_id(test_id: str) -> Dict[str, Any]:
    """Get a specific test case by ID."""
    for tc in ACCURACY_TEST_DATASET:
        if tc.get("id") == test_id:
            return tc
    raise ValueError(f"Test case with ID '{test_id}' not found")


def get_all_test_queries() -> List[str]:
    """Get all test queries."""
    return [tc["query"] for tc in ACCURACY_TEST_DATASET]


def validate_response_accuracy(
    response: str,
    sources: List[Dict[str, Any]],
    confidence_score: float,
    test_case: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate response accuracy against a test case.
    
    Returns:
        Dictionary with validation results
    """
    response_lower = response.lower()
    
    # Check keywords
    keywords_found = sum(
        1 for keyword in test_case["expected_keywords"]
        if keyword.lower() in response_lower
    )
    keyword_accuracy = keywords_found / len(test_case["expected_keywords"])
    
    # Check confidence
    confidence_met = confidence_score >= test_case["min_confidence"]
    
    # Check sources
    sources_met = (
        not test_case["should_have_sources"] or
        len(sources) > 0
    )
    
    # Check source relevance
    source_relevance = True
    if test_case["should_have_sources"] and sources:
        source_urls = " ".join([s.get("url", "") for s in sources]).lower()
        expected_source_keywords = test_case.get("expected_sources", [])
        if expected_source_keywords:
            source_relevance = any(
                keyword.lower() in source_urls
                for keyword in expected_source_keywords
            )
    
    # Overall accuracy
    overall_accurate = (
        keyword_accuracy >= 0.5 and
        confidence_met and
        sources_met and
        source_relevance
    )
    
    return {
        "test_case_id": test_case["id"],
        "query": test_case["query"],
        "keyword_accuracy": keyword_accuracy,
        "keywords_found": keywords_found,
        "total_keywords": len(test_case["expected_keywords"]),
        "confidence_met": confidence_met,
        "confidence_score": confidence_score,
        "sources_met": sources_met,
        "source_relevance": source_relevance,
        "overall_accurate": overall_accurate,
    }

