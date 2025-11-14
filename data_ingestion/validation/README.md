# Data Validation Suite

This directory contains comprehensive validation tests for the mutual funds FAQ assistant data ingestion pipeline.

## Overview

The validation suite ensures data quality across all stages of the pipeline:
- **Scraped Content Quality** - Validates raw scraped data
- **Source URL Tracking** - Ensures proper URL storage and linking
- **Vector Embeddings** - Verifies embedding generation quality
- **Metadata Accuracy** - Validates metadata completeness and accuracy
- **Chunking Quality** - Tests chunking strategy effectiveness
- **Groww Page Mappings** - Validates Groww website mappings

## Test Files

| File | Purpose | Test Count |
|------|---------|------------|
| `test_data_quality.py` | Scraped content validation | ~25 tests |
| `test_source_tracking.py` | Source URL linking validation | ~30 tests |
| `test_embeddings.py` | Embedding quality validation | ~25 tests |
| `test_metadata.py` | Metadata accuracy validation | ~30 tests |
| `test_chunking.py` | Chunking strategy validation | ~25 tests |
| `test_groww_mapping.py` | Groww mapping validation | ~25 tests |

## Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-json-report

# Ensure data is available (run ingestion first)
python run_ingestion.py
```

### Run All Tests

```bash
# Using the validation runner
python data_ingestion/validation/run_validation.py

# Or using pytest directly
pytest data_ingestion/validation/ -v
```

### Run Specific Test Suite

```bash
pytest data_ingestion/validation/test_data_quality.py -v
pytest data_ingestion/validation/test_embeddings.py -v
```

## Test Coverage

### Data Quality Tests
- ✅ Data structure validation
- ✅ Required fields presence
- ✅ Content length validation
- ✅ URL validity
- ✅ Duplicate detection
- ✅ Content quality checks
- ✅ AMC name consistency

### Source Tracking Tests
- ✅ Source URL presence
- ✅ URL format validation
- ✅ Chunk-to-URL mapping
- ✅ Bidirectional linking
- ✅ No orphaned chunks

### Embedding Tests
- ✅ Embedding presence
- ✅ Dimension consistency
- ✅ Value validity (no NaN/Inf)
- ✅ Normalization
- ✅ Similarity properties
- ✅ Reproducibility

### Metadata Tests
- ✅ Metadata structure
- ✅ Source URL storage
- ✅ AMC information
- ✅ Content type classification
- ✅ Timestamp validation
- ✅ Structured info format

### Chunking Tests
- ✅ Chunk size validation
- ✅ Boundary quality
- ✅ Overlap validation
- ✅ Content preservation
- ✅ Semantic coherence

### Groww Mapping Tests
- ✅ Mapping presence
- ✅ URL validity
- ✅ Category identification
- ✅ AMC slug mappings
- ✅ Source priority logic
- ✅ Mapping consistency

## Quality Thresholds

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| Valid documents | >80% | Ensure data quality |
| Chunks with embeddings | 100% | Complete coverage |
| Chunks with source URLs | 100% | Full traceability |
| Metadata coverage | >90% | Rich context |
| Groww mapping rate | >50% | Good integration |
| Duplicate content | <5% | Minimize redundancy |
| Chunk size compliance | >90% | Proper segmentation |

## Interpreting Results

### Success Criteria

All tests pass with:
- No critical failures
- <5% warnings
- All thresholds met

### Common Issues

**High duplicate rate:**
- Review scraper logic
- Check for repeated URLs
- Verify deduplication

**Low embedding quality:**
- Check model loading
- Verify text preprocessing
- Review embedding generation

**Poor chunking:**
- Adjust chunk size parameters
- Review chunking strategy
- Check boundary detection

**Missing metadata:**
- Review metadata extraction
- Check source data quality
- Verify metadata propagation

**Low Groww mapping rate:**
- Review category identification
- Check URL construction logic
- Verify AMC slug mappings

## Generating Reports

### HTML Report

```bash
pytest data_ingestion/validation/ -v \
  --html=validation_report.html \
  --self-contained-html
```

### JSON Report

```bash
pytest data_ingestion/validation/ -v \
  --json-report \
  --json-report-file=validation_report.json
```

### Detailed Output

```bash
pytest data_ingestion/validation/ -vv --tb=long
```

## Integration with Pipeline

The validation suite should be run:
1. After initial data ingestion
2. After any pipeline changes
3. Before deploying to production
4. Periodically for data monitoring

### Automated Validation

Add to your pipeline:

```python
from validation.run_validation import main

# After ingestion
ingestion_result = run_ingestion()

if ingestion_result == 0:
    validation_result = main()
    if validation_result != 0:
        raise Exception("Validation failed!")
```

## Troubleshooting

### Tests Skipped

If tests are skipped, it usually means:
- Data files not found
- Insufficient data for test
- Dependencies not installed

**Solution:** Run ingestion pipeline first

### Import Errors

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Install requirements
pip install -r backend/requirements.txt

# Or install test dependencies
pip install pytest numpy
```

### Slow Tests

Embedding tests may be slow on first run (model download).

**Solution:** Tests will be faster on subsequent runs.

## Contributing

When adding new tests:
1. Follow existing test structure
2. Use descriptive test names
3. Add docstrings
4. Update this README
5. Update validation report template

## Support

For issues or questions:
- Check test output for details
- Review VALIDATION_REPORT.md
- Check individual test files for documentation

---

**Last Updated:** 2024-11-14  
**Version:** 1.0.0  
**Status:** Complete and ready for use

