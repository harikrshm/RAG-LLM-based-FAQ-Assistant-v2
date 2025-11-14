"""
Load Test Configuration

Configuration for load testing scenarios.
"""

from typing import List, Dict, Any


class LoadTestConfig:
    """Configuration for load tests."""
    
    # Base configuration
    BASE_URL = "http://localhost:8000"
    API_ENDPOINT = f"{BASE_URL}/api/chat"
    TIMEOUT_SECONDS = 30
    
    # Test queries
    TEST_QUERIES = [
        "What is the expense ratio of HDFC Equity Fund?",
        "How much should I invest in SIP?",
        "What is a mutual fund?",
        "Explain the difference between equity and debt funds",
        "What are the tax benefits of ELSS funds?",
        "How to calculate returns on mutual funds?",
        "What is NAV in mutual funds?",
        "Explain systematic investment plan",
        "What are the risks of investing in mutual funds?",
        "How to choose a mutual fund?",
    ]
    
    # Test scenarios
    SCENARIOS = {
        "low_load": {
            "name": "Low Load",
            "description": "Light load test with minimal concurrency",
            "num_requests": 10,
            "concurrency": 2,
            "expected_success_rate": 100.0,
            "expected_max_response_time_ms": 5000.0,
        },
        "medium_load": {
            "name": "Medium Load",
            "description": "Moderate load test",
            "num_requests": 50,
            "concurrency": 10,
            "expected_success_rate": 95.0,
            "expected_max_response_time_ms": 10000.0,
        },
        "high_load": {
            "name": "High Load",
            "description": "Heavy load test",
            "num_requests": 100,
            "concurrency": 25,
            "expected_success_rate": 90.0,
            "expected_max_response_time_ms": 15000.0,
        },
        "stress_test": {
            "name": "Stress Test",
            "description": "Stress test to find breaking point",
            "num_requests": 200,
            "concurrency": 50,
            "expected_success_rate": 80.0,
            "expected_max_response_time_ms": 30000.0,
        },
        "ramp_up": {
            "name": "Ramp-Up Test",
            "description": "Gradually increase load",
            "initial_users": 1,
            "max_users": 20,
            "ramp_up_seconds": 30,
            "requests_per_user": 5,
            "expected_success_rate": 95.0,
            "expected_max_response_time_ms": 10000.0,
        },
        "sustained_load": {
            "name": "Sustained Load",
            "description": "Sustained load over time",
            "num_requests": 500,
            "concurrency": 20,
            "expected_success_rate": 95.0,
            "expected_max_response_time_ms": 10000.0,
        },
    }
    
    # Performance thresholds
    THRESHOLDS = {
        "response_time_p95_ms": 5000.0,  # 95th percentile should be under 5 seconds
        "response_time_p99_ms": 10000.0,  # 99th percentile should be under 10 seconds
        "error_rate_percent": 5.0,  # Error rate should be under 5%
        "success_rate_percent": 95.0,  # Success rate should be at least 95%
    }


def get_scenario(name: str) -> Dict[str, Any]:
    """
    Get a test scenario by name.
    
    Args:
        name: Scenario name
        
    Returns:
        Scenario configuration
    """
    return LoadTestConfig.SCENARIOS.get(name, {})


def list_scenarios() -> List[str]:
    """
    List all available test scenarios.
    
    Returns:
        List of scenario names
    """
    return list(LoadTestConfig.SCENARIOS.keys())

