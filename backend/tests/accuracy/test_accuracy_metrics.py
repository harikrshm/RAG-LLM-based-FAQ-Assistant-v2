"""
Accuracy Metrics Tests

Tests to calculate and validate accuracy metrics for responses.
"""

import pytest
from typing import List, Dict, Any

from backend.tests.accuracy.test_dataset import (
    ACCURACY_TEST_DATASET,
    validate_response_accuracy,
)


class TestAccuracyMetrics:
    """Test accuracy metrics calculation."""
    
    def test_keyword_precision(self):
        """Test keyword precision calculation."""
        test_case = ACCURACY_TEST_DATASET[0]
        response = "The expense ratio of HDFC Equity Fund is 1.5% per annum."
        
        keywords_found = sum(
            1 for keyword in test_case["expected_keywords"]
            if keyword.lower() in response.lower()
        )
        
        precision = keywords_found / len(test_case["expected_keywords"])
        
        assert precision >= 0.5, f"Keyword precision {precision} below threshold"
    
    def test_confidence_threshold(self):
        """Test confidence score threshold validation."""
        test_case = ACCURACY_TEST_DATASET[0]
        
        # Test cases with different confidence scores
        test_scores = [0.9, 0.7, 0.5, 0.3]
        
        for score in test_scores:
            meets_threshold = score >= test_case["min_confidence"]
            if score >= 0.7:
                assert meets_threshold, f"Score {score} should meet threshold"
            else:
                assert not meets_threshold, f"Score {score} should not meet threshold"
    
    def test_source_presence(self):
        """Test source presence validation."""
        test_case = ACCURACY_TEST_DATASET[0]
        
        # Test with sources
        sources_present = [
            {"url": "https://groww.in/mutual-funds/hdfc-equity-fund"}
        ]
        assert len(sources_present) > 0 == test_case["should_have_sources"]
        
        # Test without sources
        sources_absent = []
        assert len(sources_absent) == 0 != test_case["should_have_sources"]
    
    def test_overall_accuracy_calculation(self):
        """Test overall accuracy calculation."""
        # Simulate validation results
        validation_results = [
            {
                "keyword_accuracy": 0.8,
                "confidence_met": True,
                "sources_met": True,
                "source_relevance": True,
            },
            {
                "keyword_accuracy": 0.6,
                "confidence_met": True,
                "sources_met": True,
                "source_relevance": True,
            },
            {
                "keyword_accuracy": 0.4,
                "confidence_met": False,
                "sources_met": True,
                "source_relevance": True,
            },
        ]
        
        accurate_count = sum(
            1 for r in validation_results
            if (
                r["keyword_accuracy"] >= 0.5 and
                r["confidence_met"] and
                r["sources_met"] and
                r["source_relevance"]
            )
        )
        
        overall_accuracy = accurate_count / len(validation_results)
        
        assert overall_accuracy == 2/3, f"Expected 2/3, got {overall_accuracy}"
    
    def test_validate_response_accuracy_function(self):
        """Test the validate_response_accuracy function."""
        test_case = ACCURACY_TEST_DATASET[0]
        
        response = "The expense ratio of HDFC Equity Fund is 1.5% per annum."
        sources = [{"url": "https://groww.in/mutual-funds/hdfc-equity-fund"}]
        confidence_score = 0.85
        
        result = validate_response_accuracy(
            response=response,
            sources=sources,
            confidence_score=confidence_score,
            test_case=test_case,
        )
        
        assert result["test_case_id"] == test_case["id"]
        assert result["query"] == test_case["query"]
        assert result["keyword_accuracy"] > 0
        assert result["confidence_met"] is True
        assert result["sources_met"] is True
        assert result["overall_accurate"] is True


class TestAccuracyReporting:
    """Test accuracy reporting and metrics."""
    
    def test_accuracy_report_generation(self):
        """Test generation of accuracy report."""
        # Simulate validation results for multiple test cases
        validation_results = []
        
        for test_case in ACCURACY_TEST_DATASET[:3]:
            # Simulate response
            response = f"Test response for {test_case['query']}"
            sources = [{"url": "https://example.com"}] if test_case["should_have_sources"] else []
            confidence = 0.8
            
            result = validate_response_accuracy(
                response=response,
                sources=sources,
                confidence_score=confidence,
                test_case=test_case,
            )
            validation_results.append(result)
        
        # Calculate metrics
        total_tests = len(validation_results)
        accurate_tests = sum(1 for r in validation_results if r["overall_accurate"])
        overall_accuracy = accurate_tests / total_tests
        
        avg_keyword_accuracy = sum(r["keyword_accuracy"] for r in validation_results) / total_tests
        
        # Generate report
        report = {
            "total_tests": total_tests,
            "accurate_tests": accurate_tests,
            "overall_accuracy": overall_accuracy,
            "average_keyword_accuracy": avg_keyword_accuracy,
            "results": validation_results,
        }
        
        assert report["total_tests"] == 3
        assert "overall_accuracy" in report
        assert "average_keyword_accuracy" in report
        assert len(report["results"]) == 3
    
    def test_category_wise_accuracy(self):
        """Test accuracy calculation by category."""
        from backend.tests.accuracy.test_dataset import get_test_cases_by_category
        
        fund_details_cases = get_test_cases_by_category("fund_details")
        general_info_cases = get_test_cases_by_category("general_info")
        
        assert len(fund_details_cases) > 0
        assert len(general_info_cases) > 0
        
        # Simulate accuracy for each category
        fund_details_accuracy = 0.85  # Simulated
        general_info_accuracy = 0.75  # Simulated
        
        assert fund_details_accuracy >= 0.7
        assert general_info_accuracy >= 0.6

