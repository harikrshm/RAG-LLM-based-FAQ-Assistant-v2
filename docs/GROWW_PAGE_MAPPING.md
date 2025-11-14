# Groww Page Mapping Configuration Guide

This document describes the Groww page mapping configuration system that maps user queries and content to relevant Groww website pages.

## Overview

The Groww page mapping system enables the FAQ Assistant to:
1. Identify when information is available on Groww's website
2. Map queries to specific Groww pages
3. Prioritize Groww pages over external sources
4. Provide direct links to relevant Groww content

## Configuration Files

Two configuration file formats are available:

1. **JSON**: `backend/config/groww_page_mappings.json` (Recommended for programmatic access)
2. **YAML**: `backend/config/groww_page_mappings.yaml` (Recommended for human readability)

Both files contain the same information and can be used interchangeably.

## File Structure

### Top-Level Fields

```json
{
  "version": "1.0.0",
  "last_updated": "2024-11-14",
  "base_url": "https://groww.in",
  "amc_mappings": {...},
  "url_patterns": {...},
  "query_patterns": {...},
  "information_categories": {...},
  "page_sections": {...},
  "fallback_behavior": {...}
}
```

### AMC Mappings

Maps AMC name variations to their Groww URL slugs:

```json
{
  "amc_mappings": {
    "hdfc": "hdfc-mutual-funds",
    "hdfc mutual fund": "hdfc-mutual-funds",
    "sbi": "sbi-mutual-funds",
    ...
  }
}
```

**Usage**: When a query mentions "HDFC", it maps to `hdfc-mutual-funds` slug for building URLs.

### URL Patterns

Defines URL patterns for different page types:

```json
{
  "url_patterns": {
    "fund_details": {
      "pattern": "/mutual-funds/{fund_slug}",
      "description": "Individual fund detail page",
      "example": "/mutual-funds/hdfc-equity-fund-direct-growth"
    },
    "amc_overview": {
      "pattern": "/mutual-funds/amc/{amc_slug}",
      "description": "AMC overview page",
      "example": "/mutual-funds/amc/hdfc-mutual-funds"
    }
  }
}
```

**Variables**:
- `{fund_slug}`: Fund identifier (e.g., `hdfc-equity-fund-direct-growth`)
- `{amc_slug}`: AMC identifier (e.g., `hdfc-mutual-funds`)
- `{amc_name}`: AMC name extracted from slug (e.g., `hdfc`)
- `{category}`: Fund category (e.g., `equity-funds`)
- `{article_slug}`: Blog article identifier

### Query Patterns

Maps query keywords/phrases to information categories:

```json
{
  "query_patterns": {
    "fund_details": [
      "expense ratio",
      "exit load",
      "minimum sip",
      ...
    ],
    "amc_overview": [
      "amc",
      "asset management company",
      ...
    ]
  }
}
```

**Usage**: When a query contains "expense ratio", it's categorized as `fund_details`.

### Information Categories

Defines categories with metadata:

```json
{
  "information_categories": {
    "fund_details": {
      "keywords": ["fund", "scheme", "details"],
      "groww_available": true,
      "priority": 1
    }
  }
}
```

**Fields**:
- `keywords`: Keywords associated with this category
- `groww_available`: Whether this information is available on Groww
- `priority`: Priority level (1 = highest)

### Page Sections

Defines anchor links for specific sections:

```json
{
  "page_sections": {
    "expense_ratio": {
      "section_id": "#expense-ratio",
      "description": "Expense ratio section on fund page"
    }
  }
}
```

**Usage**: Links can point to specific sections like `/mutual-funds/fund-name#expense-ratio`.

### Fallback Behavior

Configures fallback logic:

```json
{
  "fallback_behavior": {
    "check_groww_first": true,
    "fallback_to_external": true,
    "generic_fallback_message": "For more information..."
  }
}
```

## Usage in Code

### Loading Configuration

```python
import json
from pathlib import Path

# Load JSON config
config_path = Path("backend/config/groww_page_mappings.json")
with open(config_path, "r") as f:
    config = json.load(f)

# Access AMC mappings
amc_slug = config["amc_mappings"].get("hdfc", None)

# Access URL patterns
fund_pattern = config["url_patterns"]["fund_details"]["pattern"]
```

### Building URLs

```python
# Build fund URL
fund_slug = "hdfc-equity-fund-direct-growth"
pattern = config["url_patterns"]["fund_details"]["pattern"]
url = f"{config['base_url']}{pattern.format(fund_slug=fund_slug)}"
# Result: https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth

# Build AMC URL
amc_slug = config["amc_mappings"]["hdfc"]
pattern = config["url_patterns"]["amc_overview"]["pattern"]
url = f"{config['base_url']}{pattern.format(amc_slug=amc_slug)}"
# Result: https://groww.in/mutual-funds/amc/hdfc-mutual-funds
```

## Adding New Mappings

### Adding New AMC

1. **Add to `amc_mappings`**:
```json
{
  "amc_mappings": {
    "new_amc": "new-amc-mutual-funds",
    "new amc mutual fund": "new-amc-mutual-funds"
  }
}
```

2. **Update both JSON and YAML files**

### Adding New Query Pattern

1. **Add to `query_patterns`**:
```json
{
  "query_patterns": {
    "new_category": [
      "new keyword",
      "another keyword"
    ]
  }
}
```

2. **Add corresponding URL pattern**:
```json
{
  "url_patterns": {
    "new_category": {
      "pattern": "/mutual-funds/{pattern}",
      "description": "Description"
    }
  }
}
```

### Adding New Page Section

```json
{
  "page_sections": {
    "new_section": {
      "section_id": "#new-section",
      "description": "Description"
    }
  }
}
```

## Validation

### Required Fields

- `version`: Configuration version
- `base_url`: Groww base URL
- `amc_mappings`: At least one AMC mapping
- `url_patterns`: At least one URL pattern

### Validation Rules

1. **AMC Mappings**: All values must be valid URL slugs (lowercase, hyphens)
2. **URL Patterns**: Must use valid template variables
3. **Query Patterns**: Should be lowercase for case-insensitive matching
4. **Information Categories**: Must have `groww_available` boolean field

## Best Practices

1. **Keep Configs in Sync**: Update both JSON and YAML files
2. **Version Control**: Update `version` and `last_updated` when making changes
3. **Documentation**: Add descriptions for new patterns
4. **Testing**: Test URL building with real examples
5. **Case Sensitivity**: Use lowercase for all mappings and patterns

## Examples

### Example 1: Query About Expense Ratio

**Query**: "What is the expense ratio of HDFC Equity Fund?"

**Mapping Process**:
1. Identify category: `fund_details` (contains "expense ratio")
2. Extract AMC: "HDFC" → `hdfc-mutual-funds`
3. Extract fund: "HDFC Equity Fund" → `hdfc-equity-fund-direct-growth`
4. Build URL: `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth#expense-ratio`

### Example 2: Query About AMC

**Query**: "Tell me about SBI Mutual Fund"

**Mapping Process**:
1. Identify category: `amc_overview` (contains "about" and "mutual fund")
2. Extract AMC: "SBI Mutual Fund" → `sbi-mutual-funds`
3. Build URL: `https://groww.in/mutual-funds/amc/sbi-mutual-funds`

### Example 3: Query About Fund Comparison

**Query**: "Compare HDFC Equity Fund vs SBI Equity Fund"

**Mapping Process**:
1. Identify category: `fund_comparison` (contains "compare")
2. Build URL: `https://groww.in/mutual-funds/compare`

## Maintenance

### Regular Updates

- **Quarterly**: Review and update AMC mappings
- **When Groww Changes URLs**: Update URL patterns
- **When New Categories Added**: Add query patterns and URL patterns

### Update Process

1. Make changes to config file(s)
2. Update `version` and `last_updated`
3. Test URL building
4. Update documentation
5. Commit changes

## Troubleshooting

### URLs Not Building Correctly

1. Check AMC mapping exists
2. Verify URL pattern syntax
3. Check variable names match
4. Validate fund/AMC slugs

### Queries Not Matching

1. Check query patterns are lowercase
2. Verify patterns are in correct category
3. Test with actual queries
4. Check for typos in patterns

### Configuration Not Loading

1. Verify file path is correct
2. Check JSON/YAML syntax
3. Validate file encoding (UTF-8)
4. Check file permissions

## Related Files

- `backend/services/groww_mapper.py` - Service that uses this configuration
- `backend/config/settings.py` - Application settings
- `docs/DEPLOYMENT.md` - Deployment guide

## Support

For questions or issues:
1. Check existing mappings first
2. Review examples in this document
3. Test with sample queries
4. Update configuration as needed

