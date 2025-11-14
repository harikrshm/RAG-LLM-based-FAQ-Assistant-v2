"""
Load Testing Script

Tests system performance under various load conditions.
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/chat"

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


class LoadTestResult:
    """Represents the result of a load test."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times: List[float] = []
        self.error_messages: List[str] = []
        self.status_codes: Dict[int, int] = {}
        self.start_time: float = 0
        self.end_time: float = 0
    
    def add_result(self, success: bool, response_time: float, status_code: int = 200, error: str = None):
        """Add a test result."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
            self.response_times.append(response_time)
        else:
            self.failed_requests += 1
            if error:
                self.error_messages.append(error)
        
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from test results."""
        if not self.response_times:
            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": 0.0,
                "duration_seconds": self.end_time - self.start_time if self.end_time > self.start_time else 0,
                "status_codes": self.status_codes,
                "errors": self.error_messages[:10],  # First 10 errors
            }
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0,
            "duration_seconds": self.end_time - self.start_time if self.end_time > self.start_time else 0,
            "requests_per_second": self.total_requests / (self.end_time - self.start_time) if self.end_time > self.start_time else 0,
            "response_time_ms": {
                "mean": statistics.mean(self.response_times),
                "median": statistics.median(self.response_times),
                "p95": self._percentile(self.response_times, 95),
                "p99": self._percentile(self.response_times, 99),
                "min": min(self.response_times),
                "max": max(self.response_times),
            },
            "status_codes": self.status_codes,
            "errors": self.error_messages[:10],  # First 10 errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


async def make_request(
    session: aiohttp.ClientSession,
    query: str,
    session_id: str = None,
) -> tuple[bool, float, int, str]:
    """
    Make a single API request.
    
    Args:
        session: aiohttp session
        query: Query to send
        session_id: Optional session ID
        
    Returns:
        Tuple of (success, response_time_ms, status_code, error_message)
    """
    start_time = time.time()
    
    try:
        payload = {
            "query": query,
            "session_id": session_id or f"load_test_{int(time.time())}",
        }
        
        async with session.post(
            API_ENDPOINT,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            status_code = response.status
            
            if status_code == 200:
                data = await response.json()
                return True, response_time, status_code, None
            else:
                error_text = await response.text()
                return False, response_time, status_code, error_text[:200]
    
    except asyncio.TimeoutError:
        response_time = (time.time() - start_time) * 1000
        return False, response_time, 0, "Request timeout"
    
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return False, response_time, 0, str(e)[:200]


async def run_concurrent_requests(
    num_requests: int,
    concurrency: int,
    queries: List[str],
) -> LoadTestResult:
    """
    Run concurrent requests.
    
    Args:
        num_requests: Total number of requests
        concurrency: Number of concurrent requests
        queries: List of test queries
        
    Returns:
        LoadTestResult with test results
    """
    result = LoadTestResult()
    result.start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(concurrency)
        
        async def bounded_request(query: str, request_num: int):
            """Make a request with concurrency limit."""
            async with semaphore:
                success, response_time, status_code, error = await make_request(
                    session,
                    query,
                    session_id=f"load_test_{request_num}",
                )
                result.add_result(success, response_time, status_code, error)
        
        # Create tasks
        tasks = []
        for i in range(num_requests):
            query = queries[i % len(queries)]
            tasks.append(bounded_request(query, i))
        
        # Run all tasks
        await asyncio.gather(*tasks)
    
    result.end_time = time.time()
    return result


async def run_ramp_up_test(
    initial_users: int,
    max_users: int,
    ramp_up_seconds: int,
    requests_per_user: int,
    queries: List[str],
) -> LoadTestResult:
    """
    Run a ramp-up load test.
    
    Args:
        initial_users: Initial number of concurrent users
        max_users: Maximum number of concurrent users
        ramp_up_seconds: Time to ramp up to max users
        requests_per_user: Number of requests per user
        queries: List of test queries
        
    Returns:
        LoadTestResult with test results
    """
    result = LoadTestResult()
    result.start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async def user_simulation(user_id: int):
            """Simulate a user making requests."""
            for i in range(requests_per_user):
                query = queries[i % len(queries)]
                success, response_time, status_code, error = await make_request(
                    session,
                    query,
                    session_id=f"user_{user_id}",
                )
                result.add_result(success, response_time, status_code, error)
                # Small delay between requests
                await asyncio.sleep(0.1)
        
        # Ramp up users gradually
        current_users = initial_users
        ramp_up_interval = ramp_up_seconds / (max_users - initial_users) if max_users > initial_users else 1
        
        tasks = []
        user_id = 0
        
        while current_users <= max_users:
            # Add new users
            for _ in range(current_users - len(tasks)):
                tasks.append(user_simulation(user_id))
                user_id += 1
            
            # Wait for ramp-up interval
            await asyncio.sleep(ramp_up_interval)
            current_users += 1
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    
    result.end_time = time.time()
    return result


def print_results(result: LoadTestResult, test_name: str):
    """Print test results."""
    stats = result.get_statistics()
    
    print(f"\n{'='*60}")
    print(f"Load Test Results: {test_name}")
    print(f"{'='*60}")
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful_requests']}")
    print(f"Failed: {stats['failed_requests']}")
    print(f"Success Rate: {stats['success_rate']:.2f}%")
    print(f"Duration: {stats['duration_seconds']:.2f} seconds")
    print(f"Requests/Second: {stats.get('requests_per_second', 0):.2f}")
    
    if 'response_time_ms' in stats:
        rt = stats['response_time_ms']
        print(f"\nResponse Time (ms):")
        print(f"  Mean: {rt['mean']:.2f}")
        print(f"  Median: {rt['median']:.2f}")
        print(f"  P95: {rt['p95']:.2f}")
        print(f"  P99: {rt['p99']:.2f}")
        print(f"  Min: {rt['min']:.2f}")
        print(f"  Max: {rt['max']:.2f}")
    
    print(f"\nStatus Codes: {stats['status_codes']}")
    
    if stats.get('errors'):
        print(f"\nSample Errors:")
        for error in stats['errors'][:5]:
            print(f"  - {error[:100]}")
    
    print(f"{'='*60}\n")


async def main():
    """Run load tests."""
    print("Starting Load Tests...")
    print(f"Base URL: {BASE_URL}")
    print(f"API Endpoint: {API_ENDPOINT}\n")
    
    # Test 1: Low concurrency
    print("Test 1: Low Concurrency (10 requests, 2 concurrent)")
    result1 = await run_concurrent_requests(
        num_requests=10,
        concurrency=2,
        queries=TEST_QUERIES,
    )
    print_results(result1, "Low Concurrency")
    
    # Test 2: Medium concurrency
    print("Test 2: Medium Concurrency (50 requests, 10 concurrent)")
    result2 = await run_concurrent_requests(
        num_requests=50,
        concurrency=10,
        queries=TEST_QUERIES,
    )
    print_results(result2, "Medium Concurrency")
    
    # Test 3: High concurrency
    print("Test 3: High Concurrency (100 requests, 25 concurrent)")
    result3 = await run_concurrent_requests(
        num_requests=100,
        concurrency=25,
        queries=TEST_QUERIES,
    )
    print_results(result3, "High Concurrency")
    
    # Test 4: Ramp-up test
    print("Test 4: Ramp-Up Test (1-20 users over 30 seconds)")
    result4 = await run_ramp_up_test(
        initial_users=1,
        max_users=20,
        ramp_up_seconds=30,
        requests_per_user=5,
        queries=TEST_QUERIES,
    )
    print_results(result4, "Ramp-Up")
    
    # Summary
    print("\n" + "="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (Low): {result1.get_statistics()['success_rate']:.2f}% success")
    print(f"Test 2 (Medium): {result2.get_statistics()['success_rate']:.2f}% success")
    print(f"Test 3 (High): {result3.get_statistics()['success_rate']:.2f}% success")
    print(f"Test 4 (Ramp-Up): {result4.get_statistics()['success_rate']:.2f}% success")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

