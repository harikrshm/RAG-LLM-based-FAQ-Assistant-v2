"""
Validation Test Suite Runner

This script runs all validation tests and generates a comprehensive report
of data quality issues.
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


def run_pytest_suite(test_file: str) -> dict:
    """
    Run a pytest test file and return results.
    
    Args:
        test_file: Path to test file
        
    Returns:
        Dictionary with test results
    """
    print(f"\n{'='*80}")
    print(f"Running: {test_file}")
    print('='*80)
    
    try:
        # Run pytest with JSON report
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=temp_report.json",
            ],
            capture_output=True,
            text=True,
        )
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        # Try to load JSON report
        try:
            with open("temp_report.json", "r") as f:
                report = json.load(f)
        except FileNotFoundError:
            report = {
                "summary": {
                    "total": 0,
                    "passed": 0,
                    "failed": 0,
                },
                "tests": [],
            }
        
        return {
            "test_file": test_file,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "report": report,
        }
        
    except Exception as e:
        print(f"Error running {test_file}: {e}")
        return {
            "test_file": test_file,
            "exit_code": -1,
            "error": str(e),
        }


def generate_report(results: list) -> dict:
    """
    Generate a comprehensive validation report.
    
    Args:
        results: List of test results
        
    Returns:
        Dictionary with report data
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_test_suites": len(results),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "skipped_tests": 0,
        },
        "test_suites": [],
        "issues": [],
    }
    
    for result in results:
        suite_name = Path(result["test_file"]).stem
        
        # Parse results
        if result["exit_code"] == 0:
            status = "PASSED"
        elif result["exit_code"] == -1:
            status = "ERROR"
        else:
            status = "FAILED"
        
        # Count tests from stdout
        stdout = result.get("stdout", "")
        passed = stdout.count(" PASSED")
        failed = stdout.count(" FAILED")
        skipped = stdout.count(" SKIPPED")
        
        report["summary"]["total_tests"] += passed + failed + skipped
        report["summary"]["passed_tests"] += passed
        report["summary"]["failed_tests"] += failed
        report["summary"]["skipped_tests"] += skipped
        
        suite_info = {
            "name": suite_name,
            "status": status,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "exit_code": result["exit_code"],
        }
        
        report["test_suites"].append(suite_info)
        
        # Extract issues
        if failed > 0:
            report["issues"].append({
                "suite": suite_name,
                "type": "test_failure",
                "count": failed,
                "details": "Check test output for details",
            })
    
    return report


def main():
    """Main function to run all validation tests."""
    print("\n" + "="*80)
    print("DATA VALIDATION TEST SUITE")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Define test files
    test_files = [
        "data_ingestion/validation/test_data_quality.py",
        "data_ingestion/validation/test_source_tracking.py",
        "data_ingestion/validation/test_embeddings.py",
        "data_ingestion/validation/test_metadata.py",
        "data_ingestion/validation/test_chunking.py",
        "data_ingestion/validation/test_groww_mapping.py",
    ]
    
    # Run all tests
    results = []
    for test_file in test_files:
        result = run_pytest_suite(test_file)
        results.append(result)
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    report_file = "data/validation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total test suites: {report['summary']['total_test_suites']}")
    print(f"Total tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed_tests']}")
    print(f"Failed: {report['summary']['failed_tests']}")
    print(f"Skipped: {report['summary']['skipped_tests']}")
    
    print("\nTest Suite Results:")
    for suite in report["test_suites"]:
        status_symbol = "✓" if suite["status"] == "PASSED" else "✗"
        print(f"  {status_symbol} {suite['name']}: {suite['status']} "
              f"({suite['passed']} passed, {suite['failed']} failed, "
              f"{suite['skipped']} skipped)")
    
    if report["issues"]:
        print(f"\n⚠ Found {len(report['issues'])} issue(s):")
        for issue in report["issues"]:
            print(f"  - {issue['suite']}: {issue['type']} (count: {issue['count']})")
    else:
        print("\n✓ No data quality issues found!")
    
    print(f"\nFull report saved to: {report_file}")
    print("="*80)
    
    # Return exit code based on results
    if report["summary"]["failed_tests"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

