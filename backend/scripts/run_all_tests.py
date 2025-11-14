#!/usr/bin/env python3
"""
Test Runner Script

Runs all test suites and generates reports.
"""

import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """
    Run a command and return success status and output.
    
    Args:
        cmd: Command to run
        description: Description of what's being run
        
    Returns:
        Tuple of (success, output)
    """
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return False, str(e)


def run_unit_tests(verbose: bool = False, coverage: bool = False) -> bool:
    """Run unit tests."""
    cmd = ["pytest"]
    
    # Add test paths
    cmd.extend([
        "backend/services/*.test.py",
        "backend/api/routes/*.test.py",
        "backend/main.test.py",
        "data_ingestion/*.test.py",
    ])
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=backend",
            "--cov=data_ingestion",
            "--cov-report=term",
        ])
    
    success, _ = run_command(cmd, "Unit Tests")
    return success


def run_integration_tests(verbose: bool = False) -> bool:
    """Run integration tests."""
    cmd = ["pytest", "backend/tests/integration/"]
    
    if verbose:
        cmd.append("-v")
    
    success, _ = run_command(cmd, "Integration Tests")
    return success


def run_accuracy_tests(verbose: bool = False) -> bool:
    """Run accuracy tests."""
    cmd = ["pytest", "backend/tests/accuracy/"]
    
    if verbose:
        cmd.append("-v")
    
    success, _ = run_command(cmd, "Accuracy Tests")
    return success


def run_compliance_tests(verbose: bool = False) -> bool:
    """Run compliance tests."""
    cmd = ["pytest", "backend/tests/compliance/"]
    
    if verbose:
        cmd.append("-v")
    
    success, _ = run_command(cmd, "Compliance Tests")
    return success


def run_load_tests(scenario: str = "medium_load") -> bool:
    """Run load tests."""
    cmd = [
        "python", "-m", "backend.tests.load.run_load_tests",
        "--scenario", scenario,
    ]
    
    success, _ = run_command(cmd, f"Load Tests ({scenario})")
    return success


def check_code_quality() -> bool:
    """Check code quality with linters."""
    print("\n" + "="*60)
    print("Code Quality Checks")
    print("="*60 + "\n")
    
    # Check if tools are available
    tools = {
        "flake8": ["flake8", "backend/", "--max-line-length=100", "--exclude=venv,__pycache__"],
        "black": ["black", "--check", "backend/"],
    }
    
    all_passed = True
    
    for tool_name, cmd in tools.items():
        print(f"\nRunning {tool_name}...")
        success, output = run_command(cmd, tool_name)
        if not success:
            print(f"⚠ {tool_name} found issues")
            all_passed = False
        else:
            print(f"✓ {tool_name} passed")
    
    return all_passed


def generate_coverage_report() -> bool:
    """Generate coverage report."""
    cmd = [
        "pytest",
        "backend/tests/",
        "--cov=backend",
        "--cov-report=html",
        "--cov-report=term",
    ]
    
    success, _ = run_command(cmd, "Coverage Report")
    
    if success:
        print("\nCoverage report generated in htmlcov/index.html")
    
    return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run all test suites")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run unit tests only",
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests only",
    )
    parser.add_argument(
        "--accuracy",
        action="store_true",
        help="Run accuracy tests only",
    )
    parser.add_argument(
        "--compliance",
        action="store_true",
        help="Run compliance tests only",
    )
    parser.add_argument(
        "--load",
        action="store_true",
        help="Run load tests only",
    )
    parser.add_argument(
        "--quality",
        action="store_true",
        help="Run code quality checks only",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--load-scenario",
        default="medium_load",
        help="Load test scenario (default: medium_load)",
    )
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Skip load tests",
    )
    
    args = parser.parse_args()
    
    # Change to backend directory
    backend_dir = Path(__file__).parent.parent
    import os
    os.chdir(backend_dir)
    
    results = {}
    
    # Run tests based on flags
    if args.unit or (not any([args.unit, args.integration, args.accuracy, args.compliance, args.load, args.quality])):
        results["unit"] = run_unit_tests(verbose=args.verbose, coverage=args.coverage)
    
    if args.integration or (not any([args.unit, args.integration, args.accuracy, args.compliance, args.load, args.quality])):
        results["integration"] = run_integration_tests(verbose=args.verbose)
    
    if args.accuracy or (not any([args.unit, args.integration, args.accuracy, args.compliance, args.load, args.quality])):
        results["accuracy"] = run_accuracy_tests(verbose=args.verbose)
    
    if args.compliance or (not any([args.unit, args.integration, args.accuracy, args.compliance, args.load, args.quality])):
        results["compliance"] = run_compliance_tests(verbose=args.verbose)
    
    if args.load or (not any([args.unit, args.integration, args.accuracy, args.compliance, args.load, args.quality]) and not args.skip_load):
        results["load"] = run_load_tests(scenario=args.load_scenario)
    
    if args.quality or (not any([args.unit, args.integration, args.accuracy, args.compliance, args.load, args.quality])):
        results["quality"] = check_code_quality()
    
    # Generate coverage report if requested
    if args.coverage:
        results["coverage"] = generate_coverage_report()
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

