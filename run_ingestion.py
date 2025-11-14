#!/usr/bin/env python3
"""
Ingestion Pipeline Runner Script

This script runs the complete data ingestion pipeline to process
AMC source URLs and build the knowledge base for the FAQ chatbot.

Usage:
    python run_ingestion.py                    # Run full pipeline
    python run_ingestion.py --skip-scraping    # Skip scraping, use existing data
    python run_ingestion.py --reset-db         # Reset database before ingestion
    python run_ingestion.py --validate-only    # Only run validation on existing data
"""

import argparse
import logging
import sys
import os
import json
from pathlib import Path

# Add data_ingestion to path
sys.path.insert(0, str(Path(__file__).parent / "data_ingestion"))

from pipeline import IngestionPipeline
from validator import DataValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("ingestion_pipeline.log"),
    ],
)
logger = logging.getLogger(__name__)


def load_source_urls(filepath: str) -> dict:
    """
    Load and validate source URLs file.

    Args:
        filepath: Path to source URLs JSON file

    Returns:
        Source URLs dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Source URLs file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded source URLs for {len(data)} AMCs")
    for amc, urls in data.items():
        logger.info(f"  - {amc}: {len(urls)} URLs")

    return data


def validate_existing_data(output_dir: str = "data") -> None:
    """
    Run validation on existing data files.

    Args:
        output_dir: Output directory containing data files
    """
    logger.info("Running validation on existing data")

    validator = DataValidator()

    # Load data files
    scraped_data = None
    processed_docs = None
    chunks = None

    try:
        with open(os.path.join(output_dir, "scraped_content.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            scraped_data = data.get("scraped_content", [])
            logger.info(f"Loaded {len(scraped_data)} scraped documents")
    except FileNotFoundError:
        logger.warning("Scraped content file not found, skipping")

    try:
        with open(os.path.join(output_dir, "processed_content.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            processed_docs = data.get("processed_documents", [])
            logger.info(f"Loaded {len(processed_docs)} processed documents")
    except FileNotFoundError:
        logger.warning("Processed content file not found, skipping")

    try:
        with open(os.path.join(output_dir, "chunks_with_embeddings.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            chunks = data.get("chunks", [])
            logger.info(f"Loaded {len(chunks)} chunks")
    except FileNotFoundError:
        logger.warning("Chunks file not found, skipping")

    # Run validation
    results = validator.run_full_validation(
        scraped_data=scraped_data,
        processed_docs=processed_docs,
        chunks=chunks,
        chunks_with_embeddings=chunks,
    )

    # Save validation results
    with open(os.path.join(output_dir, "validation_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS SUMMARY")
    print("=" * 80)

    for stage, stage_results in results.items():
        print(f"\n{stage.upper()}:")

        if "total_documents" in stage_results:
            print(f"  Total documents: {stage_results['total_documents']}")
            print(f"  Valid documents: {stage_results['valid_documents']}")

        if "total_chunks" in stage_results:
            print(f"  Total chunks: {stage_results['total_chunks']}")
            if "valid_chunks" in stage_results:
                print(f"  Valid chunks: {stage_results['valid_chunks']}")

        if "issues" in stage_results:
            print(f"  Issues found: {len(stage_results['issues'])}")
            if len(stage_results["issues"]) > 0:
                print("  Issue types:")
                issue_types = {}
                for issue in stage_results["issues"]:
                    issue_type = issue.get("type", "unknown")
                    issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
                for issue_type, count in issue_types.items():
                    print(f"    - {issue_type}: {count}")

        if "duplicate_count" in stage_results:
            print(f"  Duplicates found: {stage_results['duplicate_count']}")

        if "unique_sources" in stage_results:
            print(f"  Unique sources: {stage_results['unique_sources']}")

        if "unique_amcs" in stage_results:
            print(f"  Unique AMCs: {stage_results['unique_amcs']}")

        if "mapping_rate" in stage_results:
            print(f"  Mapping rate: {stage_results['mapping_rate']:.2f}%")

    print("\n" + "=" * 80)
    logger.info(f"Validation results saved to {output_dir}/validation_results.json")


def run_pipeline(args: argparse.Namespace) -> int:
    """
    Run the ingestion pipeline.

    Args:
        args: Command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Validate source URLs file exists
        logger.info(f"Using source URLs file: {args.source_urls}")
        source_data = load_source_urls(args.source_urls)

        total_urls = sum(len(urls) for urls in source_data.values())
        logger.info(f"Total URLs to process: {total_urls}")

        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Initialize pipeline
        logger.info("Initializing ingestion pipeline...")
        pipeline = IngestionPipeline(
            source_urls_file=args.source_urls,
            output_dir=args.output_dir,
            vectordb_dir=args.vectordb_dir,
            collection_name=args.collection_name,
        )

        # Run pipeline
        logger.info("Starting pipeline execution...")
        stats = pipeline.run(
            skip_scraping=args.skip_scraping,
            reset_database=args.reset_db,
        )

        # Check for errors
        if stats.get("errors"):
            logger.error(f"Pipeline completed with {len(stats['errors'])} errors")
            return 1

        logger.info("Pipeline completed successfully!")
        return 0

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in source URLs file: {e}")
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}", exc_info=True)
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run the data ingestion pipeline for the FAQ chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python run_ingestion.py

  # Skip scraping and use existing scraped data
  python run_ingestion.py --skip-scraping

  # Reset database before ingestion
  python run_ingestion.py --reset-db

  # Only validate existing data
  python run_ingestion.py --validate-only

  # Use custom source URLs file
  python run_ingestion.py --source-urls custom_urls.json

  # Use custom output directory
  python run_ingestion.py --output-dir custom_data/
        """,
    )

    parser.add_argument(
        "--source-urls",
        default="data/source_urls.json",
        help="Path to source URLs JSON file (default: data/source_urls.json)",
    )

    parser.add_argument(
        "--output-dir",
        default="data",
        help="Output directory for processed data (default: data)",
    )

    parser.add_argument(
        "--vectordb-dir",
        default="data/vectordb",
        help="Vector database directory (default: data/vectordb)",
    )

    parser.add_argument(
        "--collection-name",
        default="mutual_funds_faq",
        help="Vector database collection name (default: mutual_funds_faq)",
    )

    parser.add_argument(
        "--skip-scraping",
        action="store_true",
        help="Skip scraping step and use existing scraped data",
    )

    parser.add_argument(
        "--reset-db",
        action="store_true",
        help="Reset the vector database before ingestion",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only run validation on existing data, don't run pipeline",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging (DEBUG level)",
    )

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Print banner
    print("\n" + "=" * 80)
    print("MUTUAL FUNDS FAQ CHATBOT - DATA INGESTION PIPELINE")
    print("=" * 80)
    print()

    # Run validation only if requested
    if args.validate_only:
        validate_existing_data(args.output_dir)
        return 0

    # Run pipeline
    exit_code = run_pipeline(args)

    # Run validation after pipeline
    if exit_code == 0 and not args.skip_scraping:
        logger.info("\nRunning post-pipeline validation...")
        try:
            validate_existing_data(args.output_dir)
        except Exception as e:
            logger.warning(f"Post-pipeline validation failed: {e}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

