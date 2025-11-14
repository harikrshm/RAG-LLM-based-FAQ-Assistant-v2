"""
Data Ingestion Pipeline Orchestrator

This module orchestrates the entire data ingestion pipeline, processing
AMC source links through scraping, processing, chunking, embedding, and storage.
"""

import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

from scraper import MutualFundScraper
from processor import DocumentProcessor
from chunker import TextChunker
from embedder import EmbeddingGenerator
from vectordb import VectorDatabase
from metadata_manager import MetadataManager
from groww_mapper import GrowwMapper

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IngestionPipeline:
    """
    Orchestrates the data ingestion pipeline.
    """

    def __init__(
        self,
        source_urls_file: str = "data/source_urls.json",
        output_dir: str = "data",
        vectordb_dir: str = "data/vectordb",
        collection_name: str = "mutual_funds_faq",
    ):
        """
        Initialize the ingestion pipeline.

        Args:
            source_urls_file: Path to source URLs JSON file
            output_dir: Directory for output files
            vectordb_dir: Directory for vector database
            collection_name: Name of the vector database collection
        """
        self.source_urls_file = source_urls_file
        self.output_dir = output_dir
        self.vectordb_dir = vectordb_dir
        self.collection_name = collection_name

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize pipeline components
        logger.info("Initializing pipeline components...")

        self.scraper = MutualFundScraper(source_urls_file=source_urls_file)

        self.processor = DocumentProcessor(
            remove_html=True,
            remove_extra_whitespace=True,
            lowercase=False,
            min_content_length=50,
        )

        self.chunker = TextChunker(
            chunk_size=500,
            chunk_overlap=50,
            chunking_strategy="sentence",
            min_chunk_size=100,
        )

        self.embedder = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2",
            batch_size=32,
            normalize_embeddings=True,
        )

        self.vectordb = VectorDatabase(
            persist_directory=vectordb_dir, collection_name=collection_name
        )

        self.metadata_manager = MetadataManager(
            metadata_file=os.path.join(output_dir, "metadata_index.json")
        )

        self.groww_mapper = GrowwMapper()

        logger.info("Pipeline components initialized successfully")

        # Pipeline statistics
        self.stats = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "urls_processed": 0,
            "documents_scraped": 0,
            "documents_processed": 0,
            "chunks_created": 0,
            "chunks_embedded": 0,
            "chunks_stored": 0,
            "chunks_mapped_to_groww": 0,
            "errors": [],
        }

    def run(self, skip_scraping: bool = False, reset_database: bool = False) -> Dict:
        """
        Run the complete ingestion pipeline.

        Args:
            skip_scraping: Skip scraping if data already exists
            reset_database: Reset the vector database before ingestion

        Returns:
            Pipeline execution statistics
        """
        logger.info("=" * 80)
        logger.info("Starting Data Ingestion Pipeline")
        logger.info("=" * 80)

        self.stats["start_time"] = datetime.now().isoformat()

        try:
            # Step 1: Scrape data
            if skip_scraping:
                logger.info("Skipping scraping step (using existing data)")
                scraped_data = self._load_scraped_data()
            else:
                scraped_data = self._scrape_data()

            # Step 2: Process documents
            processed_docs = self._process_documents(scraped_data)

            # Step 3: Create chunks
            chunks = self._create_chunks(processed_docs)

            # Step 4: Generate embeddings
            chunks_with_embeddings = self._generate_embeddings(chunks)

            # Step 5: Map to Groww pages
            chunks_with_mappings = self._map_to_groww(chunks_with_embeddings)

            # Step 6: Store in vector database
            if reset_database:
                logger.info("Resetting vector database...")
                self.vectordb.reset()

            self._store_in_vectordb(chunks_with_mappings)

            # Step 7: Update metadata manager
            self._update_metadata(scraped_data, chunks_with_mappings)

            # Step 8: Save intermediate outputs
            self._save_outputs(
                scraped_data, processed_docs, chunks_with_embeddings, chunks_with_mappings
            )

            # Finalize statistics
            self.stats["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(self.stats["start_time"])
            end_time = datetime.fromisoformat(self.stats["end_time"])
            self.stats["duration_seconds"] = (end_time - start_time).total_seconds()

            logger.info("=" * 80)
            logger.info("Pipeline completed successfully!")
            logger.info("=" * 80)

            self._print_statistics()

            return self.stats

        except Exception as e:
            logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            self.stats["errors"].append(str(e))
            raise

    def _scrape_data(self) -> List[Dict]:
        """Scrape data from source URLs."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 1: Scraping Data")
        logger.info("=" * 80)

        try:
            scraped_data = self.scraper.scrape_all_amcs()
            self.stats["documents_scraped"] = len(scraped_data)
            logger.info(f"Successfully scraped {len(scraped_data)} documents")
            return scraped_data
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            self.stats["errors"].append(f"Scraping: {str(e)}")
            raise

    def _load_scraped_data(self) -> List[Dict]:
        """Load previously scraped data."""
        try:
            filepath = os.path.join(self.output_dir, "scraped_content.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                scraped_data = data.get("scraped_content", [])
                logger.info(f"Loaded {len(scraped_data)} scraped documents")
                self.stats["documents_scraped"] = len(scraped_data)
                return scraped_data
        except Exception as e:
            logger.error(f"Failed to load scraped data: {e}")
            raise

    def _process_documents(self, scraped_data: List[Dict]) -> List[Dict]:
        """Process scraped documents."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 2: Processing Documents")
        logger.info("=" * 80)

        try:
            processed_docs = self.processor.process_scraped_content(scraped_data)
            self.stats["documents_processed"] = len(processed_docs)
            logger.info(f"Successfully processed {len(processed_docs)} documents")
            return processed_docs
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            self.stats["errors"].append(f"Processing: {str(e)}")
            raise

    def _create_chunks(self, processed_docs: List[Dict]) -> List:
        """Create chunks from processed documents."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 3: Creating Chunks")
        logger.info("=" * 80)

        try:
            chunks = self.chunker.process_documents(processed_docs)
            self.stats["chunks_created"] = len(chunks)
            logger.info(f"Successfully created {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Chunking failed: {e}")
            self.stats["errors"].append(f"Chunking: {str(e)}")
            raise

    def _generate_embeddings(self, chunks: List) -> List[Dict]:
        """Generate embeddings for chunks."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 4: Generating Embeddings")
        logger.info("=" * 80)

        try:
            # Convert TextChunk objects to dictionaries
            chunks_dict = [
                {
                    "chunk_id": chunk.chunk_id,
                    "content": chunk.content,
                    "source_url": chunk.source_url,
                    "chunk_index": chunk.chunk_index,
                    "metadata": chunk.metadata,
                }
                for chunk in chunks
            ]

            chunks_with_embeddings = self.embedder.embed_chunks(chunks_dict)
            self.stats["chunks_embedded"] = len(chunks_with_embeddings)
            logger.info(f"Successfully generated embeddings for {len(chunks_with_embeddings)} chunks")
            return chunks_with_embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            self.stats["errors"].append(f"Embedding: {str(e)}")
            raise

    def _map_to_groww(self, chunks: List[Dict]) -> List[Dict]:
        """Map chunks to Groww pages."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 5: Mapping to Groww Pages")
        logger.info("=" * 80)

        try:
            chunks_with_mappings = self.groww_mapper.process_chunks_with_mapping(chunks)
            mapped_count = sum(1 for c in chunks_with_mappings if c.get("groww_page_url"))
            self.stats["chunks_mapped_to_groww"] = mapped_count
            logger.info(f"Successfully mapped {mapped_count} chunks to Groww pages")
            return chunks_with_mappings
        except Exception as e:
            logger.error(f"Groww mapping failed: {e}")
            self.stats["errors"].append(f"Groww Mapping: {str(e)}")
            raise

    def _store_in_vectordb(self, chunks: List[Dict]) -> None:
        """Store chunks in vector database."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 6: Storing in Vector Database")
        logger.info("=" * 80)

        try:
            self.vectordb.add_chunks(chunks)
            self.stats["chunks_stored"] = self.vectordb.count()
            logger.info(f"Successfully stored {self.stats['chunks_stored']} chunks in vector database")
        except Exception as e:
            logger.error(f"Vector database storage failed: {e}")
            self.stats["errors"].append(f"VectorDB Storage: {str(e)}")
            raise

    def _update_metadata(self, scraped_data: List[Dict], chunks: List[Dict]) -> None:
        """Update metadata manager."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 7: Updating Metadata")
        logger.info("=" * 80)

        try:
            # Register sources
            processed_urls = set()
            for doc in scraped_data:
                url = doc.get("url")
                if url and url not in processed_urls:
                    self.metadata_manager.register_source(
                        {
                            "url": url,
                            "amc_name": doc.get("amc_name"),
                            "amc_id": doc.get("amc_id"),
                            "title": doc.get("title"),
                            "scraped_at": doc.get("scraped_at"),
                        }
                    )
                    processed_urls.add(url)

            # Register chunks
            for chunk in chunks:
                self.metadata_manager.register_chunk(chunk)

                # Register Groww mapping if exists
                if chunk.get("groww_page_url"):
                    self.metadata_manager.register_groww_mapping(
                        chunk["chunk_id"], chunk["groww_page_url"]
                    )

            # Save metadata
            self.metadata_manager.save_metadata()

            logger.info("Metadata updated successfully")
        except Exception as e:
            logger.error(f"Metadata update failed: {e}")
            self.stats["errors"].append(f"Metadata: {str(e)}")
            raise

    def _save_outputs(
        self,
        scraped_data: List[Dict],
        processed_docs: List[Dict],
        chunks_with_embeddings: List[Dict],
        chunks_with_mappings: List[Dict],
    ) -> None:
        """Save intermediate outputs."""
        logger.info("\n" + "=" * 80)
        logger.info("Step 8: Saving Outputs")
        logger.info("=" * 80)

        try:
            # Save scraped data
            with open(
                os.path.join(self.output_dir, "scraped_content.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(
                    {
                        "scraped_content": scraped_data,
                        "metadata": {"total_documents": len(scraped_data)},
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save processed documents
            with open(
                os.path.join(self.output_dir, "processed_content.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(
                    {
                        "processed_documents": processed_docs,
                        "metadata": {"total_documents": len(processed_docs)},
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save chunks with embeddings
            with open(
                os.path.join(self.output_dir, "chunks_with_embeddings.json"),
                "w",
                encoding="utf-8",
            ) as f:
                json.dump(
                    {
                        "chunks": chunks_with_embeddings,
                        "metadata": {"total_chunks": len(chunks_with_embeddings)},
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save final chunks with mappings
            with open(
                os.path.join(self.output_dir, "chunks_final.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(
                    {
                        "chunks": chunks_with_mappings,
                        "metadata": {"total_chunks": len(chunks_with_mappings)},
                    },
                    f,
                    indent=2,
                    ensure_ascii=False,
                )

            # Save pipeline statistics
            with open(
                os.path.join(self.output_dir, "pipeline_stats.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)

            logger.info("Outputs saved successfully")
        except Exception as e:
            logger.error(f"Saving outputs failed: {e}")
            self.stats["errors"].append(f"Saving Outputs: {str(e)}")
            raise

    def _print_statistics(self) -> None:
        """Print pipeline statistics."""
        print("\n" + "=" * 80)
        print("PIPELINE STATISTICS")
        print("=" * 80)
        print(f"Duration: {self.stats['duration_seconds']:.2f} seconds")
        print(f"\nData Processing:")
        print(f"  - Documents scraped: {self.stats['documents_scraped']}")
        print(f"  - Documents processed: {self.stats['documents_processed']}")
        print(f"  - Chunks created: {self.stats['chunks_created']}")
        print(f"  - Chunks embedded: {self.stats['chunks_embedded']}")
        print(f"  - Chunks stored: {self.stats['chunks_stored']}")
        print(f"  - Chunks mapped to Groww: {self.stats['chunks_mapped_to_groww']}")

        if self.stats["errors"]:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"  - {error}")

        print("=" * 80)


def main():
    """Main function to run the ingestion pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the data ingestion pipeline")
    parser.add_argument(
        "--skip-scraping",
        action="store_true",
        help="Skip scraping and use existing data",
    )
    parser.add_argument(
        "--reset-db", action="store_true", help="Reset the vector database before ingestion"
    )
    parser.add_argument(
        "--source-urls",
        default="data/source_urls.json",
        help="Path to source URLs file",
    )
    parser.add_argument("--output-dir", default="data", help="Output directory")

    args = parser.parse_args()

    # Initialize and run pipeline
    pipeline = IngestionPipeline(
        source_urls_file=args.source_urls,
        output_dir=args.output_dir,
    )

    try:
        pipeline.run(skip_scraping=args.skip_scraping, reset_database=args.reset_db)
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()

