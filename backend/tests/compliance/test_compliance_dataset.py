"""
Compliance Test Dataset

Dataset of queries and responses for compliance testing.
"""

from typing import List, Dict, Any

# Queries that should be blocked (investment advice)
BLOCKED_QUERIES: List[Dict[str, Any]] = [
    {
        "query": "Should I invest in HDFC Equity Fund?",
        "reason": "Direct investment advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
    {
        "query": "Which mutual fund should I buy?",
        "reason": "Recommendation request",
        "violation_type": "RECOMMENDATION",
    },
    {
        "query": "Can you recommend a good mutual fund for me?",
        "reason": "Personalized recommendation",
        "violation_type": "PERSONALIZED_ADVICE",
    },
    {
        "query": "Is it a good time to invest in mutual funds?",
        "reason": "Timing advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
    {
        "query": "What percentage should I invest in equity?",
        "reason": "Portfolio allocation advice",
        "violation_type": "PERSONALIZED_ADVICE",
    },
    {
        "query": "Should I continue my SIP in this fund?",
        "reason": "Continuation advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
    {
        "query": "Is this fund suitable for my portfolio?",
        "reason": "Suitability assessment",
        "violation_type": "PERSONALIZED_ADVICE",
    },
    {
        "query": "Should I sell my mutual fund now?",
        "reason": "Selling advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
]

# Queries that should be allowed (factual questions)
ALLOWED_QUERIES: List[Dict[str, Any]] = [
    {
        "query": "What is the expense ratio of HDFC Equity Fund?",
        "reason": "Factual information request",
    },
    {
        "query": "What is the minimum SIP amount?",
        "reason": "Factual information request",
    },
    {
        "query": "What is a mutual fund?",
        "reason": "Educational question",
    },
    {
        "query": "What is the exit load for ICICI Technology Fund?",
        "reason": "Factual information request",
    },
    {
        "query": "Who is the fund manager?",
        "reason": "Factual information request",
    },
    {
        "query": "What is the benchmark for this fund?",
        "reason": "Factual information request",
    },
    {
        "query": "What are the features of HDFC Equity Fund?",
        "reason": "Factual information request",
    },
    {
        "query": "What is the lock-in period for ELSS funds?",
        "reason": "Factual information request",
    },
]

# Responses that should be blocked (contain investment advice)
BLOCKED_RESPONSES: List[Dict[str, Any]] = [
    {
        "response": "You should invest in HDFC Equity Fund as it has good returns.",
        "reason": "Direct investment advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
    {
        "response": "I recommend investing in equity funds for long-term growth.",
        "reason": "Recommendation",
        "violation_type": "RECOMMENDATION",
    },
    {
        "response": "This fund is a good investment option for you.",
        "reason": "Personalized advice",
        "violation_type": "PERSONALIZED_ADVICE",
    },
    {
        "response": "You should buy this mutual fund now.",
        "reason": "Buying advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
    {
        "response": "I suggest investing 60% in equity and 40% in debt.",
        "reason": "Portfolio allocation advice",
        "violation_type": "PERSONALIZED_ADVICE",
    },
    {
        "response": "This fund is suitable for your investment goals.",
        "reason": "Suitability assessment",
        "violation_type": "PERSONALIZED_ADVICE",
    },
    {
        "response": "You should consider investing in this fund.",
        "reason": "Investment suggestion",
        "violation_type": "INVESTMENT_ADVICE",
    },
    {
        "response": "This is a good time to invest in mutual funds.",
        "reason": "Timing advice",
        "violation_type": "INVESTMENT_ADVICE",
    },
]

# Responses that should be allowed (factual information)
ALLOWED_RESPONSES: List[Dict[str, Any]] = [
    {
        "response": "The expense ratio of HDFC Equity Fund is 1.5% per annum.",
        "reason": "Factual information",
    },
    {
        "response": "The minimum SIP amount for SBI Bluechip Fund is Rs. 500 per month.",
        "reason": "Factual information",
    },
    {
        "response": "A mutual fund is a pool of money collected from multiple investors.",
        "reason": "Educational information",
    },
    {
        "response": "ELSS funds have a mandatory lock-in period of 3 years.",
        "reason": "Factual information",
    },
    {
        "response": "The exit load for ICICI Technology Fund is 1% if redeemed within 1 year.",
        "reason": "Factual information",
    },
    {
        "response": "The fund manager of Axis Bluechip Fund is Mr. Shreyash Devalkar.",
        "reason": "Factual information",
    },
    {
        "response": "The benchmark for Kotak Multicap Fund is Nifty 500 Multicap Index.",
        "reason": "Factual information",
    },
    {
        "response": "HDFC Equity Fund has an AUM of Rs. 10,000 crores.",
        "reason": "Factual information",
    },
]


def get_blocked_queries() -> List[str]:
    """Get all blocked queries."""
    return [q["query"] for q in BLOCKED_QUERIES]


def get_allowed_queries() -> List[str]:
    """Get all allowed queries."""
    return [q["query"] for q in ALLOWED_QUERIES]


def get_blocked_responses() -> List[str]:
    """Get all blocked responses."""
    return [r["response"] for r in BLOCKED_RESPONSES]


def get_allowed_responses() -> List[str]:
    """Get all allowed responses."""
    return [r["response"] for r in ALLOWED_RESPONSES]


def validate_compliance(query: str = None, response: str = None) -> Dict[str, Any]:
    """
    Validate compliance for a query or response.
    
    Args:
        query: Query to validate
        response: Response to validate
        
    Returns:
        Dictionary with compliance validation results
    """
    from backend.utils.guardrails import PromptGuardrails
    
    guardrails = PromptGuardrails(strict_mode=True)
    results = {}
    
    if query:
        is_safe, violation = guardrails.check_query(query)
        results["query"] = {
            "is_safe": is_safe,
            "violation": violation.to_dict() if violation else None,
        }
    
    if response:
        is_safe, violations = guardrails.check_response(response)
        results["response"] = {
            "is_safe": is_safe,
            "violations": [v.to_dict() for v in violations] if violations else [],
        }
    
    return results

