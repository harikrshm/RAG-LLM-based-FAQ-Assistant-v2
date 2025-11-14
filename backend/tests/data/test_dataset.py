"""
Test Dataset

Provides access to test queries and expected responses.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class TestDataset:
    """Manages test dataset with queries and expected responses."""
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize test dataset.
        
        Args:
            dataset_path: Path to test dataset JSON file
        """
        if dataset_path is None:
            # Default to test_queries.json in same directory
            current_dir = Path(__file__).parent
            dataset_path = current_dir / "test_queries.json"
        
        self.dataset_path = Path(dataset_path)
        self._data: Optional[Dict[str, Any]] = None
        self._load_dataset()
    
    def _load_dataset(self):
        """Load dataset from JSON file."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset file not found: {self.dataset_path}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            self._data = json.load(f)
    
    def get_all_queries(self) -> List[Dict[str, Any]]:
        """
        Get all test queries.
        
        Returns:
            List of query dictionaries
        """
        return self._data.get("queries", [])
    
    def get_query_by_id(self, query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific query by ID.
        
        Args:
            query_id: Query ID
            
        Returns:
            Query dictionary or None if not found
        """
        queries = self.get_all_queries()
        for query in queries:
            if query.get("id") == query_id:
                return query
        return None
    
    def get_queries_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get queries by category.
        
        Args:
            category: Category name
            
        Returns:
            List of queries in the category
        """
        queries = self.get_all_queries()
        return [q for q in queries if q.get("category") == category]
    
    def get_categories(self) -> Dict[str, str]:
        """
        Get all categories and their descriptions.
        
        Returns:
            Dictionary mapping category names to descriptions
        """
        return self._data.get("categories", {})
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get dataset metadata.
        
        Returns:
            Metadata dictionary
        """
        return self._data.get("metadata", {})
    
    def validate_query_response(
        self,
        query_id: str,
        response_text: str,
        sources: List[str] = None,
        confidence: float = None,
    ) -> Dict[str, Any]:
        """
        Validate a query response against expected criteria.
        
        Args:
            query_id: Query ID
            response_text: Response text to validate
            sources: List of source URLs
            confidence: Confidence score
            
        Returns:
            Validation results dictionary
        """
        query = self.get_query_by_id(query_id)
        if not query:
            return {
                "valid": False,
                "error": f"Query {query_id} not found",
            }
        
        validation = {
            "valid": True,
            "query_id": query_id,
            "query": query.get("query"),
            "checks": {},
            "warnings": [],
            "errors": [],
        }
        
        response_lower = response_text.lower()
        
        # Check expected keywords
        expected_keywords = query.get("expected_keywords", [])
        found_keywords = []
        missing_keywords = []
        
        for keyword in expected_keywords:
            if keyword.lower() in response_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        validation["checks"]["keywords"] = {
            "expected": expected_keywords,
            "found": found_keywords,
            "missing": missing_keywords,
            "coverage": len(found_keywords) / len(expected_keywords) if expected_keywords else 1.0,
        }
        
        if missing_keywords:
            validation["warnings"].append(
                f"Missing keywords: {', '.join(missing_keywords)}"
            )
        
        # Check should contain phrases
        should_contain = query.get("should_contain", [])
        found_phrases = []
        missing_phrases = []
        
        for phrase in should_contain:
            if phrase.lower() in response_lower:
                found_phrases.append(phrase)
            else:
                missing_phrases.append(phrase)
        
        validation["checks"]["should_contain"] = {
            "expected": should_contain,
            "found": found_phrases,
            "missing": missing_phrases,
        }
        
        if missing_phrases:
            validation["errors"].append(
                f"Missing required phrases: {', '.join(missing_phrases)}"
            )
            validation["valid"] = False
        
        # Check should not contain phrases (compliance)
        should_not_contain = query.get("should_not_contain", [])
        found_prohibited = []
        
        for phrase in should_not_contain:
            if phrase.lower() in response_lower:
                found_prohibited.append(phrase)
        
        validation["checks"]["should_not_contain"] = {
            "prohibited": should_not_contain,
            "found": found_prohibited,
        }
        
        if found_prohibited:
            validation["errors"].append(
                f"Found prohibited phrases: {', '.join(found_prohibited)}"
            )
            validation["valid"] = False
        
        # Check sources
        if sources:
            expected_sources = query.get("expected_sources", [])
            found_sources = []
            
            for source in sources:
                source_lower = source.lower()
                for expected in expected_sources:
                    if expected.lower() in source_lower:
                        found_sources.append(expected)
                        break
            
            validation["checks"]["sources"] = {
                "expected": expected_sources,
                "found": found_sources,
                "provided": sources,
            }
            
            if not found_sources and expected_sources:
                validation["warnings"].append(
                    f"Expected sources not found: {', '.join(expected_sources)}"
                )
        
        # Check confidence
        if confidence is not None:
            min_confidence = query.get("min_confidence", 0.0)
            validation["checks"]["confidence"] = {
                "provided": confidence,
                "minimum": min_confidence,
                "meets_threshold": confidence >= min_confidence,
            }
            
            if confidence < min_confidence:
                validation["warnings"].append(
                    f"Confidence {confidence:.2f} below minimum {min_confidence:.2f}"
                )
        
        return validation
    
    def get_sample_queries(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get a sample of queries.
        
        Args:
            count: Number of queries to return
            
        Returns:
            List of sample queries
        """
        queries = self.get_all_queries()
        return queries[:count]


# Singleton instance
_dataset_instance: Optional[TestDataset] = None


def get_test_dataset(dataset_path: Optional[str] = None) -> TestDataset:
    """
    Get or create the singleton TestDataset instance.
    
    Args:
        dataset_path: Optional path to dataset file
        
    Returns:
        TestDataset instance
    """
    global _dataset_instance
    
    if _dataset_instance is None:
        _dataset_instance = TestDataset(dataset_path)
    
    return _dataset_instance

