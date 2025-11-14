"""
Load Test Runner

Main script to run load tests with different scenarios.
"""

import asyncio
import sys
import argparse
from typing import List, Dict, Any

from backend.tests.load.test_load import (
    run_concurrent_requests,
    run_ramp_up_test,
    print_results,
    LoadTestResult,
)
from backend.tests.load.load_test_config import (
    LoadTestConfig,
    get_scenario,
    list_scenarios,
)


async def run_scenario(scenario_name: str) -> LoadTestResult:
    """
    Run a specific test scenario.
    
    Args:
        scenario_name: Name of the scenario to run
        
    Returns:
        LoadTestResult
    """
    scenario = get_scenario(scenario_name)
    
    if not scenario:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    
    print(f"\nRunning scenario: {scenario['name']}")
    print(f"Description: {scenario['description']}")
    
    if scenario_name == "ramp_up":
        result = await run_ramp_up_test(
            initial_users=scenario["initial_users"],
            max_users=scenario["max_users"],
            ramp_up_seconds=scenario["ramp_up_seconds"],
            requests_per_user=scenario["requests_per_user"],
            queries=LoadTestConfig.TEST_QUERIES,
        )
    else:
        result = await run_concurrent_requests(
            num_requests=scenario["num_requests"],
            concurrency=scenario["concurrency"],
            queries=LoadTestConfig.TEST_QUERIES,
        )
    
    return result


def validate_results(result: LoadTestResult, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate test results against expected thresholds.
    
    Args:
        result: Test result
        scenario: Scenario configuration
        
    Returns:
        Validation results
    """
    stats = result.get_statistics()
    validation = {
        "passed": True,
        "warnings": [],
        "failures": [],
    }
    
    # Check success rate
    success_rate = stats.get("success_rate", 0.0)
    expected_success_rate = scenario.get("expected_success_rate", 95.0)
    
    if success_rate < expected_success_rate:
        validation["passed"] = False
        validation["failures"].append(
            f"Success rate {success_rate:.2f}% below expected {expected_success_rate:.2f}%"
        )
    elif success_rate < expected_success_rate + 5:
        validation["warnings"].append(
            f"Success rate {success_rate:.2f}% close to threshold {expected_success_rate:.2f}%"
        )
    
    # Check response time
    if "response_time_ms" in stats:
        rt = stats["response_time_ms"]
        expected_max = scenario.get("expected_max_response_time_ms", 10000.0)
        
        if rt["p95"] > expected_max:
            validation["warnings"].append(
                f"P95 response time {rt['p95']:.2f}ms exceeds expected {expected_max:.2f}ms"
            )
        
        if rt["max"] > expected_max * 2:
            validation["warnings"].append(
                f"Max response time {rt['max']:.2f}ms is very high"
            )
    
    # Check thresholds
    thresholds = LoadTestConfig.THRESHOLDS
    
    if "response_time_ms" in stats:
        rt = stats["response_time_ms"]
        
        if rt["p95"] > thresholds["response_time_p95_ms"]:
            validation["warnings"].append(
                f"P95 response time {rt['p95']:.2f}ms exceeds threshold {thresholds['response_time_p95_ms']:.2f}ms"
            )
        
        if rt["p99"] > thresholds["response_time_p99_ms"]:
            validation["warnings"].append(
                f"P99 response time {rt['p99']:.2f}ms exceeds threshold {thresholds['response_time_p99_ms']:.2f}ms"
            )
    
    error_rate = 100.0 - success_rate
    if error_rate > thresholds["error_rate_percent"]:
        validation["warnings"].append(
            f"Error rate {error_rate:.2f}% exceeds threshold {thresholds['error_rate_percent']:.2f}%"
        )
    
    return validation


async def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(description="Run load tests")
    parser.add_argument(
        "--scenario",
        type=str,
        help=f"Scenario to run: {', '.join(list_scenarios())}",
        default=None,
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all scenarios",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API",
    )
    
    args = parser.parse_args()
    
    # Update base URL if provided
    if args.base_url:
        LoadTestConfig.BASE_URL = args.base_url
        LoadTestConfig.API_ENDPOINT = f"{args.base_url}/api/chat"
    
    print("="*60)
    print("LOAD TEST RUNNER")
    print("="*60)
    print(f"Base URL: {LoadTestConfig.BASE_URL}")
    print(f"API Endpoint: {LoadTestConfig.API_ENDPOINT}\n")
    
    scenarios_to_run = []
    
    if args.all:
        scenarios_to_run = list_scenarios()
    elif args.scenario:
        if args.scenario not in list_scenarios():
            print(f"Error: Unknown scenario '{args.scenario}'")
            print(f"Available scenarios: {', '.join(list_scenarios())}")
            sys.exit(1)
        scenarios_to_run = [args.scenario]
    else:
        # Default: run medium load test
        scenarios_to_run = ["medium_load"]
    
    results = {}
    validations = {}
    
    for scenario_name in scenarios_to_run:
        try:
            scenario = get_scenario(scenario_name)
            result = await run_scenario(scenario_name)
            validation = validate_results(result, scenario)
            
            results[scenario_name] = result
            validations[scenario_name] = validation
            
            print_results(result, scenario["name"])
            
            # Print validation results
            print("Validation Results:")
            if validation["passed"] and not validation["warnings"]:
                print("  ✓ All checks passed")
            else:
                if validation["failures"]:
                    print("  ✗ Failures:")
                    for failure in validation["failures"]:
                        print(f"    - {failure}")
                if validation["warnings"]:
                    print("  ⚠ Warnings:")
                    for warning in validation["warnings"]:
                        print(f"    - {warning}")
            print()
        
        except Exception as e:
            print(f"Error running scenario {scenario_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("="*60)
    print("LOAD TEST SUMMARY")
    print("="*60)
    
    for scenario_name in scenarios_to_run:
        if scenario_name in results:
            stats = results[scenario_name].get_statistics()
            validation = validations[scenario_name]
            
            status = "✓ PASS" if validation["passed"] and not validation["warnings"] else "⚠ WARN" if validation["passed"] else "✗ FAIL"
            
            print(f"{scenario_name}: {status}")
            print(f"  Success Rate: {stats['success_rate']:.2f}%")
            if "response_time_ms" in stats:
                print(f"  P95 Response Time: {stats['response_time_ms']['p95']:.2f}ms")
            print()
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

