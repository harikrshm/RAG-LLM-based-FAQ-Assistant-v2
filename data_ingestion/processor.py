"""
Document Processor Module

This module cleans, parses, and prepares HTML/text content for chunking.
"""

import re
import logging
from typing import Dict, List, Optional
from bs4 import BeautifulSoup, NavigableString

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Processes documents by cleaning, parsing, and preparing content for chunking.
    """

    def __init__(
        self,
        remove_html: bool = True,
        remove_extra_whitespace: bool = True,
        lowercase: bool = False,
        remove_special_chars: bool = False,
        min_content_length: int = 50,
    ):
        """
        Initialize the document processor.

        Args:
            remove_html: Remove HTML tags
            remove_extra_whitespace: Normalize whitespace
            lowercase: Convert text to lowercase
            remove_special_chars: Remove special characters
            min_content_length: Minimum content length to keep
        """
        self.remove_html = remove_html
        self.remove_extra_whitespace = remove_extra_whitespace
        self.lowercase = lowercase
        self.remove_special_chars = remove_special_chars
        self.min_content_length = min_content_length

        # Elements to remove from HTML
        self.remove_tags = [
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "iframe",
            "noscript",
            "svg",
            "button",
        ]

    def process_document(self, content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Process a document and return cleaned content with metadata.

        Args:
            content: Raw document content
            metadata: Additional metadata

        Returns:
            Dictionary with processed content and metadata
        """
        logger.debug(f"Processing document ({len(content)} chars)")

        # Clean HTML
        if self.remove_html:
            content = self._clean_html(content)

        # Clean text
        content = self._clean_text(content)

        # Extract structured information
        structured_info = self._extract_structured_info(content)

        # Filter short content
        if len(content) < self.min_content_length:
            logger.warning(f"Content too short ({len(content)} chars), skipping")
            return None

        result = {
            "content": content,
            "content_length": len(content),
            "structured_info": structured_info,
            "metadata": metadata or {},
        }

        logger.debug(f"Processed document ({len(content)} chars)")
        return result

    def _clean_html(self, html_content: str) -> str:
        """
        Clean HTML content and extract text.

        Args:
            html_content: Raw HTML content

        Returns:
            Cleaned text content
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove unwanted tags
            for tag in self.remove_tags:
                for element in soup.find_all(tag):
                    element.decompose()

            # Remove comments
            for comment in soup.findAll(string=lambda text: isinstance(text, NavigableString)):
                if "<!--" in str(comment):
                    comment.extract()

            # Get text
            text = soup.get_text(separator="\n", strip=True)
            return text

        except Exception as e:
            logger.warning(f"Error cleaning HTML: {e}")
            return html_content

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        if self.remove_extra_whitespace:
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = text.strip()

        # Convert to lowercase
        if self.lowercase:
            text = text.lower()

        # Remove special characters (keep basic punctuation)
        if self.remove_special_chars:
            text = re.sub(r"[^\w\s.,!?;:\-\(\)%₹$]", "", text)

        # Remove URLs
        text = re.sub(r"http[s]?://\S+", "", text)

        # Remove email addresses
        text = re.sub(r"\S+@\S+", "", text)

        return text

    def _extract_structured_info(self, content: str) -> Dict:
        """
        Extract structured information from content using patterns.

        Args:
            content: Cleaned text content

        Returns:
            Dictionary of extracted structured information
        """
        structured_info = {}

        # Extract expense ratio
        expense_pattern = r"expense\s+ratio[:\s]+(\d+\.?\d*)\s*%?"
        expense_match = re.search(expense_pattern, content, re.IGNORECASE)
        if expense_match:
            structured_info["expense_ratio"] = expense_match.group(1) + "%"

        # Extract exit load
        exit_load_pattern = r"exit\s+load[:\s]+(\d+\.?\d*)\s*%?"
        exit_load_match = re.search(exit_load_pattern, content, re.IGNORECASE)
        if exit_load_match:
            structured_info["exit_load"] = exit_load_match.group(1) + "%"

        # Extract minimum SIP
        sip_pattern = r"minimum\s+sip[:\s]+(?:rs\.?|₹)?\s*(\d+(?:,\d+)*)"
        sip_match = re.search(sip_pattern, content, re.IGNORECASE)
        if sip_match:
            structured_info["minimum_sip"] = sip_match.group(1)

        # Extract lock-in period
        lockin_pattern = r"lock[-\s]?in\s+period[:\s]+(\d+)\s*(year|month|day)s?"
        lockin_match = re.search(lockin_pattern, content, re.IGNORECASE)
        if lockin_match:
            structured_info["lock_in_period"] = f"{lockin_match.group(1)} {lockin_match.group(2)}s"

        # Extract riskometer
        risk_patterns = [
            r"risk[-\s]?o[-\s]?meter[:\s]+(very\s+high|high|moderately\s+high|moderate|moderately\s+low|low|very\s+low)",
            r"risk[:\s]+(very\s+high|high|moderately\s+high|moderate|moderately\s+low|low|very\s+low)",
        ]
        for pattern in risk_patterns:
            risk_match = re.search(pattern, content, re.IGNORECASE)
            if risk_match:
                structured_info["riskometer"] = risk_match.group(1).title()
                break

        # Extract benchmark
        benchmark_pattern = r"benchmark[:\s]+([A-Z][^\n.]+(?:Index|TRI|Total\s+Return))"
        benchmark_match = re.search(benchmark_pattern, content, re.IGNORECASE)
        if benchmark_match:
            structured_info["benchmark"] = benchmark_match.group(1).strip()

        return structured_info

    def process_scraped_content(self, scraped_data: List[Dict]) -> List[Dict]:
        """
        Process multiple scraped documents.

        Args:
            scraped_data: List of scraped content dictionaries

        Returns:
            List of processed content dictionaries
        """
        logger.info(f"Processing {len(scraped_data)} scraped documents")

        processed_documents = []

        for i, doc in enumerate(scraped_data):
            try:
                # Prepare metadata
                metadata = {
                    "url": doc.get("url"),
                    "amc_name": doc.get("amc_name"),
                    "amc_id": doc.get("amc_id"),
                    "title": doc.get("title"),
                    "scraped_at": doc.get("scraped_at"),
                }

                # Process document
                content = doc.get("content", "") or doc.get("full_text", "")
                processed = self.process_document(content, metadata)

                if processed:
                    # Add original structured data if available
                    if "structured_data" in doc:
                        processed["original_structured_data"] = doc["structured_data"]

                    processed_documents.append(processed)

                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(scraped_data)} documents")

            except Exception as e:
                logger.error(f"Error processing document {i}: {e}")
                continue

        logger.info(f"Successfully processed {len(processed_documents)}/{len(scraped_data)} documents")
        return processed_documents

    def extract_key_information(self, content: str) -> Dict[str, str]:
        """
        Extract key mutual fund information from content.

        Args:
            content: Document content

        Returns:
            Dictionary of extracted key information
        """
        key_info = {}

        # Fund name
        fund_name_pattern = r"(?:fund\s+name|scheme\s+name)[:\s]+([^\n]+)"
        fund_name_match = re.search(fund_name_pattern, content, re.IGNORECASE)
        if fund_name_match:
            key_info["fund_name"] = fund_name_match.group(1).strip()

        # Fund category
        category_pattern = r"(?:category|fund\s+type)[:\s]+([^\n]+)"
        category_match = re.search(category_pattern, content, re.IGNORECASE)
        if category_match:
            key_info["category"] = category_match.group(1).strip()

        # AUM
        aum_pattern = r"(?:aum|assets\s+under\s+management)[:\s]+(?:rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)\s*(cr(?:ore)?|lakh)?"
        aum_match = re.search(aum_pattern, content, re.IGNORECASE)
        if aum_match:
            key_info["aum"] = aum_match.group(0).strip()

        # NAV
        nav_pattern = r"(?:nav|net\s+asset\s+value)[:\s]+(?:rs\.?|₹)?\s*(\d+(?:\.\d+)?)"
        nav_match = re.search(nav_pattern, content, re.IGNORECASE)
        if nav_match:
            key_info["nav"] = nav_match.group(1)

        # Returns
        returns_pattern = r"(\d+)\s*(?:year|yr)\s+returns?[:\s]+(-?\d+(?:\.\d+)?)\s*%"
        returns_matches = re.findall(returns_pattern, content, re.IGNORECASE)
        if returns_matches:
            key_info["returns"] = {f"{year}yr": f"{value}%" for year, value in returns_matches}

        return key_info

    def split_into_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Split content into logical sections.

        Args:
            content: Document content

        Returns:
            List of section dictionaries
        """
        sections = []

        # Split by common headings
        heading_pattern = r"^([A-Z][A-Za-z\s]+):?\n"
        parts = re.split(heading_pattern, content, flags=re.MULTILINE)

        current_section = {"title": "Introduction", "content": ""}

        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Content part
                current_section["content"] += part.strip()
            else:
                # Heading part
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": part.strip(), "content": ""}

        # Add last section
        if current_section["content"]:
            sections.append(current_section)

        return sections


def main():
    """Main function for testing document processor."""
    import json

    # Initialize processor
    processor = DocumentProcessor(
        remove_html=True,
        remove_extra_whitespace=True,
        lowercase=False,
        min_content_length=50,
    )

    # Load scraped content
    try:
        with open("data/scraped_content.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            scraped_content = data.get("scraped_content", [])
    except FileNotFoundError:
        logger.error("Scraped content file not found. Run scraper first.")
        return

    # Process documents
    processed_docs = processor.process_scraped_content(scraped_content)

    # Save processed content
    output_data = {
        "processed_documents": processed_docs,
        "metadata": {
            "total_documents": len(processed_docs),
            "total_content_length": sum(doc["content_length"] for doc in processed_docs),
        },
    }

    with open("data/processed_content.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(processed_docs)} processed documents")

    # Print statistics
    print("\nProcessing Statistics:")
    print(f"Total documents processed: {len(processed_docs)}")
    print(f"Average content length: {output_data['metadata']['total_content_length'] / len(processed_docs):.0f} chars")

    # Show sample extracted info
    if processed_docs:
        print("\nSample extracted structured info:")
        for i, doc in enumerate(processed_docs[:3]):
            print(f"\nDocument {i+1}: {doc['metadata'].get('title', 'Unknown')}")
            print(f"  Structured info: {doc['structured_info']}")


if __name__ == "__main__":
    main()

