# Test Dataset

This directory contains test datasets for the FAQ Assistant.

## Files

- `test_queries.json` - Main test dataset with 20 sample queries and expected responses
- `test_dataset.py` - Python module for accessing and validating test data

## Dataset Structure

The test dataset (`test_queries.json`) contains:

- **Queries**: Array of test queries with:
  - `id`: Unique query identifier
  - `category`: Query category
  - `query`: The actual query text
  - `expected_keywords`: Keywords that should appear in response
  - `expected_sources`: Expected source domains
  - `min_confidence`: Minimum confidence threshold
  - `expected_response_type`: Type of response expected
  - `should_contain`: Phrases that must appear
  - `should_not_contain`: Phrases that must not appear (compliance)
  - `note`: Optional notes

- **Categories**: Descriptions of query categories
- **Metadata**: Dataset metadata (version, dates, etc.)

## Usage

### Python

```python
from backend.tests.data.test_dataset import get_test_dataset

# Get dataset instance
dataset = get_test_dataset()

# Get all queries
queries = dataset.get_all_queries()

# Get query by ID
query = dataset.get_query_by_id("query_001")

# Get queries by category
fund_queries = dataset.get_queries_by_category("fund_details")

# Validate response
validation = dataset.validate_query_response(
    query_id="query_001",
    response_text="The expense ratio of HDFC Equity Fund is 1.5%...",
    sources=["https://hdfc.com/...", "https://amfi.com/..."],
    confidence=0.85,
)

if validation["valid"]:
    print("Response is valid")
else:
    print(f"Errors: {validation['errors']}")
```

### JSON

Load directly from JSON:

```python
import json

with open("backend/tests/data/test_queries.json", "r") as f:
    data = json.load(f)
    
queries = data["queries"]
```

## Query Categories

- **fund_details**: Specific fund details (expense ratio, NAV, etc.)
- **general_info**: General mutual fund information
- **sip_info**: Systematic Investment Plan information
- **fund_comparison**: Comparison between fund types
- **tax_info**: Tax-related information
- **amc_info**: Asset Management Company information
- **risk_info**: Risk-related information
- **fund_performance**: Historical performance data
- **fund_selection**: Fund selection guidance
- **category_info**: Fund category information

## Validation

The `validate_query_response()` method checks:

1. **Keywords**: Expected keywords present in response
2. **Required Phrases**: Phrases that must appear
3. **Prohibited Phrases**: Phrases that must not appear (compliance)
4. **Sources**: Expected source domains present
5. **Confidence**: Confidence score meets threshold

## Adding New Queries

To add a new query to the dataset:

1. Add a new entry to the `queries` array in `test_queries.json`
2. Use a unique `id` (e.g., `query_021`)
3. Set appropriate category
4. Define expected keywords and phrases
5. Specify compliance constraints (`should_not_contain`)
6. Update `metadata.total_queries` count

Example:

```json
{
  "id": "query_021",
  "category": "fund_details",
  "query": "What is the exit load for XYZ Fund?",
  "expected_keywords": ["exit load", "XYZ"],
  "expected_sources": ["xyz", "amfi"],
  "min_confidence": 0.7,
  "expected_response_type": "factual",
  "should_contain": ["exit load", "percentage"],
  "should_not_contain": ["you should", "recommended"]
}
```

## Best Practices

1. **Coverage**: Include queries from all categories
2. **Diversity**: Include various query types (factual, comparison, definition)
3. **Compliance**: Always include `should_not_contain` to prevent investment advice
4. **Realistic**: Use real-world query patterns
5. **Specificity**: Include specific fund names and details
6. **Validation**: Test validation logic with new queries

