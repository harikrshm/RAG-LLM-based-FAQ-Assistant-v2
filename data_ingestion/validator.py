"""
Data Validation Module

This module implements validation and quality checks for scraped and processed data,
including duplicate detection, content validation, and data integrity checks.
"""

import logging
import re
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates data quality throughout the ingestion pipeline.
    """

    def __init__(
        self,
        min_content_length: int = 50,
        max_content_length: int = 100000,
        duplicate_threshold: float = 0.9,
    ):
        """
        Initialize the data validator.

        Args:
            min_content_length: Minimum acceptable content length
            max_content_length: Maximum acceptable content length
            duplicate_threshold: Similarity threshold for duplicate detection (0-1)
        """
        self.min_content_length = min_content_length
        self.max_content_length = max_content_length
        self.duplicate_threshold = duplicate_threshold

        self.validation_results = {
            "total_items_validated": 0,
            "passed_validations": 0,
            "failed_validations": 0,
            "warnings": [],
            "errors": [],
            "duplicates_found": 0,
            "quality_issues": [],
        }

    def validate_scraped_data(self, scraped_data: List[Dict]) -> Dict:
        """
        Validate scraped data quality.

        Args:
            scraped_data: List of scraped document dictionaries

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating {len(scraped_data)} scraped documents")

        issues = []
        duplicates = self._detect_duplicates(scraped_data)

        for i, doc in enumerate(scraped_data):
            # Check required fields
            if not self._validate_required_fields(doc, ["url", "content"]):
                issues.append(
                    {
                        "type": "missing_fields",
                        "index": i,
                        "url": doc.get("url", "unknown"),
                    }
                )
                continue

            # Validate URL
            if not self._validate_url(doc.get("url")):
                issues.append(
                    {
                        "type": "invalid_url",
                        "index": i,
                        "url": doc.get("url"),
                    }
                )

            # Validate content length
            content = doc.get("content", "")
            if not self._validate_content_length(content):
                issues.append(
                    {
                        "type": "invalid_content_length",
                        "index": i,
                        "url": doc.get("url"),
                        "length": len(content),
                    }
                )

            # Check for empty or low-quality content
            if self._is_low_quality_content(content):
                issues.append(
                    {
                        "type": "low_quality_content",
                        "index": i,
                        "url": doc.get("url"),
                    }
                )

        results = {
            "total_documents": len(scraped_data),
            "valid_documents": len(scraped_data) - len(issues),
            "issues": issues,
            "duplicates": duplicates,
            "duplicate_count": len(duplicates),
        }

        logger.info(
            f"Validation complete: {results['valid_documents']}/{results['total_documents']} valid"
        )
        if len(issues) > 0:
            logger.warning(f"Found {len(issues)} issues")
        if len(duplicates) > 0:
            logger.warning(f"Found {len(duplicates)} duplicate documents")

        return results

    def validate_processed_documents(self, processed_docs: List[Dict]) -> Dict:
        """
        Validate processed documents.

        Args:
            processed_docs: List of processed document dictionaries

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating {len(processed_docs)} processed documents")

        issues = []

        for i, doc in enumerate(processed_docs):
            # Check required fields
            if not self._validate_required_fields(doc, ["content", "metadata"]):
                issues.append(
                    {
                        "type": "missing_fields",
                        "index": i,
                    }
                )
                continue

            # Validate content
            content = doc.get("content", "")
            if not content or len(content) < self.min_content_length:
                issues.append(
                    {
                        "type": "insufficient_content",
                        "index": i,
                        "length": len(content),
                    }
                )

            # Check for structured info extraction
            structured_info = doc.get("structured_info", {})
            if not structured_info or len(structured_info) == 0:
                self.validation_results["warnings"].append(
                    f"Document {i} has no structured info extracted"
                )

        results = {
            "total_documents": len(processed_docs),
            "valid_documents": len(processed_docs) - len(issues),
            "issues": issues,
        }

        logger.info(
            f"Validation complete: {results['valid_documents']}/{results['total_documents']} valid"
        )

        return results

    def validate_chunks(self, chunks: List[Dict]) -> Dict:
        """
        Validate text chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating {len(chunks)} chunks")

        issues = []
        chunk_duplicates = self._detect_duplicate_chunks(chunks)

        for i, chunk in enumerate(chunks):
            # Check required fields
            required_fields = ["chunk_id", "content", "source_url"]
            if not self._validate_required_fields(chunk, required_fields):
                issues.append(
                    {
                        "type": "missing_fields",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )
                continue

            # Validate chunk ID uniqueness
            chunk_id = chunk.get("chunk_id")
            if not chunk_id or not isinstance(chunk_id, str):
                issues.append(
                    {
                        "type": "invalid_chunk_id",
                        "index": i,
                        "chunk_id": chunk_id,
                    }
                )

            # Validate content
            content = chunk.get("content", "")
            if not content:
                issues.append(
                    {
                        "type": "empty_content",
                        "index": i,
                        "chunk_id": chunk_id,
                    }
                )

        results = {
            "total_chunks": len(chunks),
            "valid_chunks": len(chunks) - len(issues),
            "issues": issues,
            "duplicate_chunks": chunk_duplicates,
            "duplicate_count": len(chunk_duplicates),
        }

        logger.info(f"Validation complete: {results['valid_chunks']}/{results['total_chunks']} valid")

        return results

    def validate_embeddings(self, chunks_with_embeddings: List[Dict]) -> Dict:
        """
        Validate embeddings quality.

        Args:
            chunks_with_embeddings: List of chunks with embeddings

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating embeddings for {len(chunks_with_embeddings)} chunks")

        issues = []
        embedding_dimensions = set()

        for i, chunk in enumerate(chunks_with_embeddings):
            # Check for embedding field
            if "embedding" not in chunk:
                issues.append(
                    {
                        "type": "missing_embedding",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )
                continue

            embedding = chunk["embedding"]

            # Validate embedding type and structure
            if not isinstance(embedding, (list, tuple)):
                issues.append(
                    {
                        "type": "invalid_embedding_type",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )
                continue

            # Check embedding dimension
            embedding_dimensions.add(len(embedding))

            # Check for all-zero embeddings (likely an error)
            if all(v == 0 for v in embedding):
                issues.append(
                    {
                        "type": "zero_embedding",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )

            # Check for NaN or infinite values
            if any(v != v or abs(v) == float("inf") for v in embedding):
                issues.append(
                    {
                        "type": "invalid_embedding_values",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )

        # Check dimension consistency
        if len(embedding_dimensions) > 1:
            self.validation_results["warnings"].append(
                f"Inconsistent embedding dimensions: {embedding_dimensions}"
            )

        results = {
            "total_chunks": len(chunks_with_embeddings),
            "valid_embeddings": len(chunks_with_embeddings) - len(issues),
            "issues": issues,
            "embedding_dimensions": list(embedding_dimensions),
        }

        logger.info(
            f"Validation complete: {results['valid_embeddings']}/{results['total_chunks']} valid"
        )

        return results

    def validate_metadata(self, chunks: List[Dict]) -> Dict:
        """
        Validate metadata completeness and accuracy.

        Args:
            chunks: List of chunks with metadata

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating metadata for {len(chunks)} chunks")

        issues = []
        urls_found = set()
        amcs_found = set()

        for i, chunk in enumerate(chunks):
            metadata = chunk.get("metadata", {})

            # Check for metadata field
            if not metadata or not isinstance(metadata, dict):
                issues.append(
                    {
                        "type": "missing_or_invalid_metadata",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )
                continue

            # Track source URLs
            source_url = chunk.get("source_url") or metadata.get("url")
            if source_url:
                urls_found.add(source_url)
            else:
                issues.append(
                    {
                        "type": "missing_source_url",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )

            # Track AMC names
            amc_name = metadata.get("amc_name")
            if amc_name:
                amcs_found.add(amc_name)

        results = {
            "total_chunks": len(chunks),
            "valid_metadata": len(chunks) - len(issues),
            "issues": issues,
            "unique_sources": len(urls_found),
            "unique_amcs": len(amcs_found),
            "sources": list(urls_found),
            "amcs": list(amcs_found),
        }

        logger.info(
            f"Validation complete: {results['valid_metadata']}/{results['total_chunks']} valid"
        )
        logger.info(f"Found {results['unique_sources']} unique sources")
        logger.info(f"Found {results['unique_amcs']} unique AMCs")

        return results

    def validate_source_urls(self, chunks: List[Dict]) -> Dict:
        """
        Validate that source URLs are correctly stored and accessible.

        Args:
            chunks: List of chunks with source URLs

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating source URLs for {len(chunks)} chunks")

        issues = []
        url_stats = defaultdict(int)

        for i, chunk in enumerate(chunks):
            source_url = chunk.get("source_url")

            if not source_url:
                issues.append(
                    {
                        "type": "missing_source_url",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                    }
                )
                continue

            # Validate URL format
            if not self._validate_url(source_url):
                issues.append(
                    {
                        "type": "invalid_url_format",
                        "index": i,
                        "chunk_id": chunk.get("chunk_id"),
                        "url": source_url,
                    }
                )

            # Track URL frequency
            url_stats[source_url] += 1

        results = {
            "total_chunks": len(chunks),
            "valid_urls": len(chunks) - len(issues),
            "issues": issues,
            "unique_urls": len(url_stats),
            "url_distribution": dict(url_stats),
        }

        logger.info(f"Validation complete: {results['valid_urls']}/{results['total_chunks']} valid")
        logger.info(f"Found {results['unique_urls']} unique URLs")

        return results

    def validate_groww_mappings(self, chunks: List[Dict]) -> Dict:
        """
        Validate Groww page mappings.

        Args:
            chunks: List of chunks with Groww mappings

        Returns:
            Validation results dictionary
        """
        logger.info(f"Validating Groww mappings for {len(chunks)} chunks")

        issues = []
        chunks_with_mapping = 0
        chunks_from_groww = 0

        for i, chunk in enumerate(chunks):
            groww_url = chunk.get("groww_page_url")
            source_url = chunk.get("source_url", "")

            # Check if chunk is from Groww
            if "groww.in" in source_url:
                chunks_from_groww += 1

            # Check if mapping exists
            if groww_url:
                chunks_with_mapping += 1

                # Validate Groww URL format
                if not self._validate_url(groww_url):
                    issues.append(
                        {
                            "type": "invalid_groww_url",
                            "index": i,
                            "chunk_id": chunk.get("chunk_id"),
                            "groww_url": groww_url,
                        }
                    )

                # Verify it's actually a Groww URL
                if "groww.in" not in groww_url:
                    issues.append(
                        {
                            "type": "non_groww_mapping",
                            "index": i,
                            "chunk_id": chunk.get("chunk_id"),
                            "groww_url": groww_url,
                        }
                    )

        results = {
            "total_chunks": len(chunks),
            "chunks_with_mapping": chunks_with_mapping,
            "chunks_from_groww_source": chunks_from_groww,
            "mapping_rate": (chunks_with_mapping / len(chunks) * 100) if chunks else 0,
            "issues": issues,
        }

        logger.info(
            f"Validation complete: {chunks_with_mapping}/{len(chunks)} chunks have Groww mappings"
        )
        logger.info(f"Mapping rate: {results['mapping_rate']:.2f}%")

        return results

    def _validate_required_fields(self, item: Dict, required_fields: List[str]) -> bool:
        """Check if all required fields are present."""
        return all(field in item for field in required_fields)

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        if not url or not isinstance(url, str):
            return False

        # Basic URL validation
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
            r"localhost|"  # localhost
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IP
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return bool(url_pattern.match(url))

    def _validate_content_length(self, content: str) -> bool:
        """Validate content length."""
        if not content:
            return False

        length = len(content)
        return self.min_content_length <= length <= self.max_content_length

    def _is_low_quality_content(self, content: str) -> bool:
        """Check if content is low quality."""
        if not content:
            return True

        # Check for mostly whitespace
        if len(content.strip()) < len(content) * 0.5:
            return True

        # Check for very repetitive content
        words = content.split()
        if len(words) > 0:
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:
                return True

        return False

    def _detect_duplicates(self, documents: List[Dict]) -> List[Tuple[int, int]]:
        """
        Detect duplicate documents using content hashing.

        Args:
            documents: List of document dictionaries

        Returns:
            List of (index1, index2) tuples for duplicate pairs
        """
        duplicates = []
        content_hashes = {}

        for i, doc in enumerate(documents):
            content = doc.get("content", "")
            content_hash = self._compute_content_hash(content)

            if content_hash in content_hashes:
                duplicates.append((content_hashes[content_hash], i))
            else:
                content_hashes[content_hash] = i

        return duplicates

    def _detect_duplicate_chunks(self, chunks: List[Dict]) -> List[Tuple[str, str]]:
        """
        Detect duplicate chunks.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            List of (chunk_id1, chunk_id2) tuples for duplicate pairs
        """
        duplicates = []
        content_hashes = {}

        for chunk in chunks:
            content = chunk.get("content", "")
            chunk_id = chunk.get("chunk_id", "")
            content_hash = self._compute_content_hash(content)

            if content_hash in content_hashes:
                duplicates.append((content_hashes[content_hash], chunk_id))
            else:
                content_hashes[content_hash] = chunk_id

        return duplicates

    def _compute_content_hash(self, content: str) -> str:
        """Compute hash of content for duplicate detection."""
        # Normalize content
        normalized = content.lower().strip()
        normalized = re.sub(r"\s+", " ", normalized)

        # Compute hash
        return hashlib.md5(normalized.encode()).hexdigest()

    def run_full_validation(
        self,
        scraped_data: Optional[List[Dict]] = None,
        processed_docs: Optional[List[Dict]] = None,
        chunks: Optional[List[Dict]] = None,
        chunks_with_embeddings: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        Run full validation pipeline on all data.

        Args:
            scraped_data: Scraped documents
            processed_docs: Processed documents
            chunks: Text chunks
            chunks_with_embeddings: Chunks with embeddings

        Returns:
            Complete validation results
        """
        logger.info("Running full validation pipeline")

        all_results = {}

        if scraped_data:
            all_results["scraped_data"] = self.validate_scraped_data(scraped_data)

        if processed_docs:
            all_results["processed_docs"] = self.validate_processed_documents(processed_docs)

        if chunks:
            all_results["chunks"] = self.validate_chunks(chunks)
            all_results["metadata"] = self.validate_metadata(chunks)
            all_results["source_urls"] = self.validate_source_urls(chunks)
            all_results["groww_mappings"] = self.validate_groww_mappings(chunks)

        if chunks_with_embeddings:
            all_results["embeddings"] = self.validate_embeddings(chunks_with_embeddings)

        logger.info("Full validation complete")

        return all_results


def main():
    """Main function for testing validator."""
    import json

    validator = DataValidator()

    # Load data
    try:
        with open("data/scraped_content.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            scraped_data = data.get("scraped_content", [])

        with open("data/processed_content.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            processed_docs = data.get("processed_documents", [])

        with open("data/chunks_with_embeddings.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])

        # Run full validation
        results = validator.run_full_validation(
            scraped_data=scraped_data,
            processed_docs=processed_docs,
            chunks=chunks,
            chunks_with_embeddings=chunks,
        )

        # Save results
        with open("data/validation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\nValidation Results Summary:")
        print("=" * 80)
        for stage, stage_results in results.items():
            print(f"\n{stage.upper()}:")
            if "issues" in stage_results:
                print(f"  Issues found: {len(stage_results['issues'])}")
            if "duplicate_count" in stage_results:
                print(f"  Duplicates found: {stage_results['duplicate_count']}")

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
    except Exception as e:
        logger.error(f"Validation failed: {e}")


if __name__ == "__main__":
    main()

