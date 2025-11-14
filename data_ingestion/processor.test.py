"""
Unit tests for the processor module
"""

import pytest
from processor import DocumentProcessor


@pytest.fixture
def processor():
    """Create a document processor."""
    return DocumentProcessor(
        remove_html=True,
        remove_extra_whitespace=True,
        lowercase=False,
        min_content_length=10,
    )


def test_processor_initialization():
    """Test processor initialization."""
    processor = DocumentProcessor()
    assert processor.remove_html is True
    assert processor.remove_extra_whitespace is True
    assert processor.min_content_length == 50


def test_clean_html(processor):
    """Test HTML cleaning."""
    html = """
    <html>
        <head><title>Test</title></head>
        <body>
            <script>alert('test');</script>
            <nav>Navigation</nav>
            <main>
                <p>This is the main content.</p>
                <p>Expense ratio: 1.5%</p>
            </main>
            <footer>Footer</footer>
        </body>
    </html>
    """
    
    cleaned = processor._clean_html(html)
    
    assert "main content" in cleaned
    assert "Expense ratio" in cleaned
    assert "alert" not in cleaned
    assert "Navigation" not in cleaned
    assert "Footer" not in cleaned


def test_clean_text(processor):
    """Test text cleaning."""
    text = "This   has    extra     spaces\n\n\n\nand   newlines"
    cleaned = processor._clean_text(text)
    
    assert "extra spaces" in cleaned
    assert "   " not in cleaned


def test_extract_expense_ratio(processor):
    """Test expense ratio extraction."""
    content = "The expense ratio of this fund is 1.5% per annum."
    structured = processor._extract_structured_info(content)
    
    assert "expense_ratio" in structured
    assert "1.5" in structured["expense_ratio"]


def test_extract_exit_load(processor):
    """Test exit load extraction."""
    content = "Exit load: 1% if redeemed within 1 year."
    structured = processor._extract_structured_info(content)
    
    assert "exit_load" in structured
    assert "1" in structured["exit_load"]


def test_extract_minimum_sip(processor):
    """Test minimum SIP extraction."""
    content = "Minimum SIP: Rs. 500 per month"
    structured = processor._extract_structured_info(content)
    
    assert "minimum_sip" in structured
    assert "500" in structured["minimum_sip"]


def test_extract_lock_in_period(processor):
    """Test lock-in period extraction."""
    content = "Lock-in period: 3 years for ELSS funds"
    structured = processor._extract_structured_info(content)
    
    assert "lock_in_period" in structured
    assert "3" in structured["lock_in_period"]
    assert "year" in structured["lock_in_period"]


def test_extract_riskometer(processor):
    """Test riskometer extraction."""
    content = "Riskometer: Moderately High risk category"
    structured = processor._extract_structured_info(content)
    
    assert "riskometer" in structured
    assert "Moderately High" in structured["riskometer"]


def test_extract_benchmark(processor):
    """Test benchmark extraction."""
    content = "Benchmark: Nifty 50 Total Return Index"
    structured = processor._extract_structured_info(content)
    
    assert "benchmark" in structured
    assert "Nifty 50" in structured["benchmark"]


def test_process_document(processor):
    """Test full document processing."""
    content = """
    <html>
        <body>
            <h1>HDFC Equity Fund</h1>
            <p>Expense ratio: 1.8%</p>
            <p>Minimum SIP: Rs. 500</p>
            <p>Benchmark: Nifty 50 TRI</p>
        </body>
    </html>
    """
    
    metadata = {"url": "https://example.com", "amc_name": "HDFC"}
    result = processor.process_document(content, metadata)
    
    assert result is not None
    assert "content" in result
    assert "structured_info" in result
    assert len(result["structured_info"]) > 0
    assert result["metadata"]["amc_name"] == "HDFC"


def test_process_short_content(processor):
    """Test processing content that's too short."""
    content = "Short"
    result = processor.process_document(content)
    
    assert result is None


def test_extract_key_information(processor):
    """Test key information extraction."""
    content = """
    Fund Name: HDFC Equity Fund
    Category: Equity - Large Cap
    NAV: Rs. 750.50
    3 year returns: 15.5%
    """
    
    key_info = processor.extract_key_information(content)
    
    assert "fund_name" in key_info
    assert "HDFC" in key_info["fund_name"]
    assert "category" in key_info
    assert "nav" in key_info


def test_process_scraped_content(processor):
    """Test processing multiple scraped documents."""
    scraped_data = [
        {
            "url": "https://example.com/fund1",
            "amc_name": "Test AMC",
            "amc_id": "test",
            "title": "Test Fund 1",
            "content": "This is test content with expense ratio: 1.5%",
            "scraped_at": "2025-11-14",
        },
        {
            "url": "https://example.com/fund2",
            "amc_name": "Test AMC",
            "amc_id": "test",
            "title": "Test Fund 2",
            "content": "This is test content with minimum SIP: Rs. 500",
            "scraped_at": "2025-11-14",
        },
    ]
    
    processed = processor.process_scraped_content(scraped_data)
    
    assert len(processed) == 2
    assert all("content" in doc for doc in processed)
    assert all("structured_info" in doc for doc in processed)

