"""
Web Scraper Module for AMC/SEBI/AMFI Websites

This module scrapes mutual fund scheme information from provided URLs only.
No broad crawling is performed.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MutualFundScraper:
    """
    Scraper for mutual fund scheme information from specified URLs.
    Only scrapes provided URLs - no broad crawling.
    """

    def __init__(
        self,
        source_urls_file: str = "data/source_urls.json",
        user_agent: Optional[str] = None,
        timeout: int = 30,
        retry_attempts: int = 3,
        delay_between_requests: float = 1.0,
        max_retries: int = 5,
        backoff_factor: float = 0.5,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 300,
    ):
        """
        Initialize the scraper.

        Args:
            source_urls_file: Path to JSON file containing source URLs
            user_agent: User agent string for requests
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            delay_between_requests: Delay between requests in seconds
            max_retries: Maximum number of retries for transient errors
            backoff_factor: Backoff factor for exponential backoff (0.5 means 0.5, 1, 2, 4, 8 seconds)
            circuit_breaker_threshold: Number of consecutive failures before circuit breaks
            circuit_breaker_timeout: Time in seconds before circuit breaker resets
        """
        self.source_urls_file = Path(source_urls_file)
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.delay_between_requests = delay_between_requests
        self.backoff_factor = backoff_factor

        # Circuit breaker settings
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.domain_failures = defaultdict(int)
        self.circuit_breaker_until = {}

        # Error tracking
        self.error_counts = {
            "connection_errors": 0,
            "timeout_errors": 0,
            "http_errors": 0,
            "parsing_errors": 0,
            "circuit_breaker_trips": 0,
        }

        # Default user agent
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )

        # Configure session with retry strategy
        self.session = self._create_session_with_retries(max_retries, backoff_factor)
        self.session.headers.update({"User-Agent": self.user_agent})

        # Load source URLs
        self.source_urls = self._load_source_urls()
        logger.info(f"Loaded {len(self.source_urls['amcs'])} AMCs with URLs")

    def _create_session_with_retries(self, max_retries: int, backoff_factor: float) -> requests.Session:
        """
        Create a requests session with automatic retry logic.

        Args:
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for exponential backoff

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy for transient errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these HTTP status codes
            allowed_methods=["GET", "HEAD"],  # Only retry safe methods
            raise_on_status=False,  # Don't raise exception, let us handle it
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _load_source_urls(self) -> Dict:
        """Load source URLs from JSON file."""
        if not self.source_urls_file.exists():
            raise FileNotFoundError(f"Source URLs file not found: {self.source_urls_file}")

        with open(self.source_urls_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        logger.info(f"Loaded {data['metadata']['total_urls']} URLs from file")
        return data

    def _check_circuit_breaker(self, domain: str) -> bool:
        """
        Check if circuit breaker is open for a domain.

        Args:
            domain: Domain to check

        Returns:
            True if circuit is closed (can proceed), False if open (should skip)
        """
        if domain in self.circuit_breaker_until:
            if datetime.now() < self.circuit_breaker_until[domain]:
                logger.warning(f"Circuit breaker OPEN for {domain}, skipping until {self.circuit_breaker_until[domain]}")
                return False
            else:
                # Circuit breaker timeout expired, reset
                logger.info(f"Circuit breaker RESET for {domain}")
                del self.circuit_breaker_until[domain]
                self.domain_failures[domain] = 0

        return True

    def _record_failure(self, domain: str, error_type: str) -> None:
        """
        Record a failure for a domain and potentially trip circuit breaker.

        Args:
            domain: Domain that failed
            error_type: Type of error
        """
        self.domain_failures[domain] += 1
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        if self.domain_failures[domain] >= self.circuit_breaker_threshold:
            until_time = datetime.now() + timedelta(seconds=self.circuit_breaker_timeout)
            self.circuit_breaker_until[domain] = until_time
            self.error_counts["circuit_breaker_trips"] += 1
            logger.error(
                f"Circuit breaker TRIPPED for {domain} after {self.domain_failures[domain]} failures. "
                f"Will retry after {until_time}"
            )

    def _record_success(self, domain: str) -> None:
        """
        Record a successful request for a domain.

        Args:
            domain: Domain that succeeded
        """
        if domain in self.domain_failures:
            self.domain_failures[domain] = 0

    def _classify_error(self, error: Exception) -> Tuple[str, bool]:
        """
        Classify error and determine if it's retryable.

        Args:
            error: Exception that occurred

        Returns:
            Tuple of (error_type, is_retryable)
        """
        if isinstance(error, requests.exceptions.Timeout):
            return ("timeout_errors", True)
        elif isinstance(error, requests.exceptions.ConnectionError):
            return ("connection_errors", True)
        elif isinstance(error, requests.exceptions.HTTPError):
            # 4xx errors are generally not retryable, 5xx are
            if hasattr(error, "response") and error.response is not None:
                if 400 <= error.response.status_code < 500:
                    return ("http_errors", False)  # Client errors, don't retry
                else:
                    return ("http_errors", True)  # Server errors, retry
            return ("http_errors", True)
        elif isinstance(error, requests.exceptions.RequestException):
            return ("connection_errors", True)
        else:
            return ("parsing_errors", False)

    def scrape_url(self, url: str, amc_name: str) -> Optional[Dict]:
        """
        Scrape a single URL and extract content with enhanced error handling.

        Args:
            url: URL to scrape
            amc_name: Name of the AMC for tracking

        Returns:
            Dictionary containing scraped content and metadata, or None if failed
        """
        logger.info(f"Scraping URL: {url}")

        # Extract domain for circuit breaker
        try:
            domain = urlparse(url).netloc
        except Exception:
            logger.error(f"Invalid URL: {url}")
            return None

        # Check circuit breaker
        if not self._check_circuit_breaker(domain):
            return None

        # Retry logic with exponential backoff
        for attempt in range(self.retry_attempts):
            try:
                # Add delay between requests
                if attempt > 0:
                    backoff_time = self.backoff_factor * (2 ** (attempt - 1))
                    logger.debug(f"Backing off for {backoff_time:.2f} seconds")
                    time.sleep(backoff_time)
                else:
                    time.sleep(self.delay_between_requests)

                # Make request
                logger.debug(f"Attempt {attempt + 1}/{self.retry_attempts} for {url}")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Parse HTML content
                try:
                    soup = BeautifulSoup(response.content, "html.parser")
                except Exception as e:
                    logger.error(f"Failed to parse HTML for {url}: {e}")
                    self._record_failure(domain, "parsing_errors")
                    return None

                # Extract content
                try:
                    content_data = self._extract_content(soup, url, amc_name)
                except Exception as e:
                    logger.error(f"Failed to extract content from {url}: {e}")
                    self._record_failure(domain, "parsing_errors")
                    return None

                # Success!
                self._record_success(domain)
                logger.info(f"Successfully scraped: {url}")
                return content_data

            except requests.exceptions.Timeout as e:
                error_type, is_retryable = self._classify_error(e)
                logger.warning(f"Timeout error on attempt {attempt + 1}/{self.retry_attempts} for {url}: {e}")
                
                if attempt < self.retry_attempts - 1 and is_retryable:
                    continue
                else:
                    self._record_failure(domain, error_type)
                    logger.error(f"Failed to scrape {url} after {self.retry_attempts} attempts (timeout)")
                    return None

            except requests.exceptions.HTTPError as e:
                error_type, is_retryable = self._classify_error(e)
                status_code = e.response.status_code if e.response else "unknown"
                logger.warning(
                    f"HTTP {status_code} error on attempt {attempt + 1}/{self.retry_attempts} for {url}: {e}"
                )
                
                if attempt < self.retry_attempts - 1 and is_retryable:
                    continue
                else:
                    self._record_failure(domain, error_type)
                    logger.error(f"Failed to scrape {url} with HTTP {status_code}")
                    return None

            except requests.exceptions.ConnectionError as e:
                error_type, is_retryable = self._classify_error(e)
                logger.warning(
                    f"Connection error on attempt {attempt + 1}/{self.retry_attempts} for {url}: {e}"
                )
                
                if attempt < self.retry_attempts - 1 and is_retryable:
                    continue
                else:
                    self._record_failure(domain, error_type)
                    logger.error(f"Failed to scrape {url} after {self.retry_attempts} attempts (connection error)")
                    return None

            except requests.exceptions.RequestException as e:
                error_type, is_retryable = self._classify_error(e)
                logger.warning(f"Request error on attempt {attempt + 1}/{self.retry_attempts} for {url}: {e}")
                
                if attempt < self.retry_attempts - 1 and is_retryable:
                    continue
                else:
                    self._record_failure(domain, error_type)
                    logger.error(f"Failed to scrape {url} after {self.retry_attempts} attempts")
                    return None

            except Exception as e:
                logger.error(f"Unexpected error scraping {url}: {e}", exc_info=True)
                self._record_failure(domain, "parsing_errors")
                return None

        return None

    def _extract_content(self, soup: BeautifulSoup, url: str, amc_name: str) -> Dict:
        """
        Extract relevant content from BeautifulSoup object.

        Args:
            soup: BeautifulSoup parsed HTML
            url: Source URL
            amc_name: AMC name

        Returns:
            Dictionary with extracted content and metadata
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Extract text content
        text_content = soup.get_text(separator="\n", strip=True)

        # Extract title
        title = soup.title.string if soup.title else urlparse(url).path

        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"]

        # Extract main content areas (customize based on Groww structure)
        main_content = ""
        
        # Try to find main content container
        main_containers = soup.find_all(
            ["main", "article", "div"],
            class_=lambda x: x and any(
                term in str(x).lower() for term in ["content", "main", "body", "scheme", "fund"]
            )
        )
        
        if main_containers:
            main_content = "\n\n".join([container.get_text(separator="\n", strip=True) 
                                       for container in main_containers])
        else:
            main_content = text_content

        # Extract structured data if available (JSON-LD)
        structured_data = []
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                structured_data.append(json.loads(script.string))
            except json.JSONDecodeError:
                continue

        return {
            "url": url,
            "amc_name": amc_name,
            "title": title,
            "meta_description": meta_desc,
            "content": main_content,
            "full_text": text_content,
            "structured_data": structured_data,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "content_length": len(main_content),
        }

    def scrape_all(self) -> List[Dict]:
        """
        Scrape all URLs from the source file.

        Returns:
            List of dictionaries containing scraped content
        """
        all_content = []
        total_urls = sum(len(amc["urls"]) for amc in self.source_urls["amcs"])
        
        logger.info(f"Starting to scrape {total_urls} URLs...")

        for amc in self.source_urls["amcs"]:
            amc_name = amc["name"]
            amc_id = amc["amc_id"]
            
            logger.info(f"Scraping {amc_name} ({len(amc['urls'])} URLs)")

            for url in amc["urls"]:
                # Scrape URL
                content = self.scrape_url(url, amc_name)
                
                if content:
                    content["amc_id"] = amc_id
                    all_content.append(content)
                
                # Delay between requests to be respectful
                time.sleep(self.delay_between_requests)

        logger.info(f"Scraping complete. Successfully scraped {len(all_content)}/{total_urls} URLs")
        return all_content

    def save_scraped_content(self, content: List[Dict], output_file: str = "data/scraped_content.json"):
        """
        Save scraped content to JSON file.

        Args:
            content: List of scraped content dictionaries
            output_file: Path to output file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "scraped_content": content,
                    "metadata": {
                        "total_pages": len(content),
                        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"Saved {len(content)} scraped pages to {output_path}")


def main():
    """Main function to run the scraper."""
    # Initialize scraper
    scraper = MutualFundScraper(
        source_urls_file="data/source_urls.json",
        delay_between_requests=1.0,
    )

    # Scrape all URLs
    content = scraper.scrape_all()

    # Save results
    scraper.save_scraped_content(content)

    print(f"\nScraping Summary:")
    print(f"Total pages scraped: {len(content)}")
    print(f"Total content size: {sum(c['content_length'] for c in content):,} characters")


if __name__ == "__main__":
    main()

