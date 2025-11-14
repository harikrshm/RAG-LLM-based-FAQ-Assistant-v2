# Fixing Data Quality Issues

This guide provides solutions for common data quality issues that may be identified during validation testing.

## Table of Contents

1. [Scraped Content Issues](#scraped-content-issues)
2. [Source URL Issues](#source-url-issues)
3. [Embedding Issues](#embedding-issues)
4. [Metadata Issues](#metadata-issues)
5. [Chunking Issues](#chunking-issues)
6. [Groww Mapping Issues](#groww-mapping-issues)

---

## Scraped Content Issues

### Issue: High Duplicate Content Rate (>5%)

**Symptoms:**
- `test_duplicate_detection` fails
- Multiple chunks with identical content

**Causes:**
- Same URL scraped multiple times
- Duplicate URLs in source file
- Pagination issues

**Solutions:**

1. **Check source URLs:**
   ```python
   # Review data/source_urls.json for duplicates
   import json
   with open("data/source_urls.json") as f:
       data = json.load(f)
       for amc, urls in data.items():
           if len(urls) != len(set(urls)):
               print(f"Duplicate URLs in {amc}")
   ```

2. **Add deduplication to scraper:**
   ```python
   # In scraper.py, track processed URLs
   self.processed_urls = set()
   
   def scrape_url(self, url, amc_name):
       if url in self.processed_urls:
           logger.warning(f"URL already processed: {url}")
           return None
       self.processed_urls.add(url)
       # ... continue scraping
   ```

3. **Filter duplicates in pipeline:**
   ```python
   # In pipeline.py, add deduplication step
   def _deduplicate_content(self, scraped_data):
       seen_hashes = set()
       unique_data = []
       for item in scraped_data:
           content_hash = hashlib.md5(item['content'].encode()).hexdigest()
           if content_hash not in seen_hashes:
               seen_hashes.add(content_hash)
               unique_data.append(item)
       return unique_data
   ```

### Issue: Low Quality Content

**Symptoms:**
- `test_content_quality` fails
- Content mostly whitespace or repetitive

**Solutions:**

1. **Improve HTML cleaning in processor:**
   ```python
   # In processor.py, enhance _clean_html method
   def _clean_html(self, html_content):
       soup = BeautifulSoup(html_content, "html.parser")
       
       # Remove more unwanted tags
       for tag in ['script', 'style', 'nav', 'footer', 'header', 
                   'aside', 'iframe', 'noscript', 'svg', 'button',
                   'form', 'input']:
           for element in soup.find_all(tag):
               element.decompose()
       
       # Get text and clean
       text = soup.get_text(separator="\n", strip=True)
       return text
   ```

2. **Add quality filters:**
   ```python
   # In validator.py, adjust thresholds
   def _is_low_quality_content(self, content):
       # Check whitespace ratio
       if len(content.strip()) < len(content) * 0.7:
           return True
       
       # Check repetition
       words = content.split()
       if len(set(words)) / len(words) < 0.4:
           return True
       
       return False
   ```

### Issue: Invalid URLs

**Symptoms:**
- `test_url_validity` fails
- URLs not accessible

**Solutions:**

1. **Validate URLs before scraping:**
   ```python
   # In source_tracker.py
   def validate_url(self, url):
       try:
           response = requests.head(url, timeout=5)
           return response.status_code < 400
       except:
           return False
   ```

2. **Update source_urls.json with valid URLs**

---

## Source URL Issues

### Issue: Missing Source URLs

**Symptoms:**
- `test_all_chunks_have_source_url` fails
- Chunks without source_url field

**Solutions:**

1. **Ensure source URL propagation:**
   ```python
   # In processor.py
   def process_document(self, content, metadata):
       result = {
           "content": cleaned_content,
           "source_url": metadata.get("url"),  # Add this
           "metadata": metadata,
       }
       return result
   ```

2. **Fix chunker to preserve source URL:**
   ```python
   # In chunker.py
   def chunk_text(self, text, metadata):
       for chunk in chunks:
           chunk.source_url = metadata.get("url")
   ```

### Issue: Inconsistent Source URLs

**Symptoms:**
- `test_source_url_consistency` fails
- Same content, different URLs

**Solutions:**

1. **Normalize URLs:**
   ```python
   def normalize_url(self, url):
       # Remove trailing slashes, query params, fragments
       parsed = urlparse(url)
       return f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
   ```

---

## Embedding Issues

### Issue: Missing Embeddings

**Symptoms:**
- `test_all_chunks_have_embeddings` fails
- Some chunks without embeddings

**Solutions:**

1. **Add error handling:**
   ```python
   # In embedder.py
   def embed_chunks(self, chunks):
       for chunk in chunks:
           try:
               embedding = self.generate_embedding(chunk['content'])
               chunk['embedding'] = embedding.tolist()
           except Exception as e:
               logger.error(f"Failed to embed chunk {chunk['chunk_id']}: {e}")
               # Use zero vector or skip
               chunk['embedding'] = [0.0] * self.embedding_dimension
   ```

2. **Verify model loading:**
   ```python
   # Check if model loaded correctly
   try:
       self.model = SentenceTransformer(model_name)
       test_embedding = self.model.encode("test")
       assert len(test_embedding) > 0
   except Exception as e:
       logger.error(f"Model loading failed: {e}")
       raise
   ```

### Issue: Inconsistent Embedding Dimensions

**Symptoms:**
- `test_consistent_dimensions` fails
- Different embedding sizes

**Solutions:**

1. **Use consistent model:**
   ```python
   # In pipeline.py, ensure same model throughout
   EMBEDDING_MODEL = "all-MiniLM-L6-v2"
   
   embedder = EmbeddingGenerator(model_name=EMBEDDING_MODEL)
   ```

2. **Validate dimensions:**
   ```python
   expected_dim = 384  # for all-MiniLM-L6-v2
   for chunk in chunks:
       if len(chunk['embedding']) != expected_dim:
           logger.error(f"Wrong dimension: {len(chunk['embedding'])}")
           # Re-generate embedding
   ```

### Issue: Low Embedding Quality

**Symptoms:**
- `test_similar_content_similar_embeddings` fails
- Poor similarity scores

**Solutions:**

1. **Improve text preprocessing:**
   ```python
   # Clean text before embedding
   def preprocess_for_embedding(self, text):
       # Remove special characters but keep meaning
       text = re.sub(r'[^\w\s.,!?-]', '', text)
       # Normalize whitespace
       text = ' '.join(text.split())
       return text
   ```

---

## Metadata Issues

### Issue: Missing AMC Names

**Symptoms:**
- `test_amc_name_present` fails
- <80% coverage

**Solutions:**

1. **Extract AMC from URL:**
   ```python
   # In metadata_manager.py
   def infer_amc_from_url(self, url):
       amc_patterns = {
           'hdfc': 'HDFC Mutual Fund',
           'sbi': 'SBI Mutual Fund',
           'icici': 'ICICI Prudential Mutual Fund',
           'axis': 'Axis Mutual Fund',
           'nippon': 'Nippon India Mutual Fund',
       }
       for pattern, amc_name in amc_patterns.items():
           if pattern in url.lower():
               return amc_name
       return None
   ```

2. **Backfill missing metadata:**
   ```python
   # Run after ingestion
   for chunk in chunks:
       if not chunk.get('metadata', {}).get('amc_name'):
           url = chunk.get('source_url', '')
           chunk['metadata']['amc_name'] = infer_amc_from_url(url)
   ```

### Issue: Incorrect Content Types

**Symptoms:**
- `test_content_type_determination` fails
- Wrong classifications

**Solutions:**

1. **Improve classification logic:**
   ```python
   # In metadata_manager.py
   def _determine_content_type(self, url, metadata):
       url_lower = url.lower()
       
       # More specific patterns first
       if '/amc/' in url_lower:
           return ContentType.AMC_PAGE.value
       elif '/top/' in url_lower or '/best-' in url_lower:
           return ContentType.COMPARISON_PAGE.value
       elif re.search(r'/mutual-funds/[\w-]+-fund', url_lower):
           return ContentType.FUND_PAGE.value
       elif '/blog/' in url_lower:
           return ContentType.BLOG_POST.value
       
       return ContentType.UNKNOWN.value
   ```

---

## Chunking Issues

### Issue: Chunks Too Large or Too Small

**Symptoms:**
- `test_chunks_within_size_limits` fails
- Inconsistent chunk sizes

**Solutions:**

1. **Adjust chunking parameters:**
   ```python
   # In pipeline.py
   self.chunker = TextChunker(
       chunk_size=400,  # Reduce from 500
       chunk_overlap=40,  # Reduce from 50
       min_chunk_size=80,  # Reduce from 100
   )
   ```

2. **Improve boundary detection:**
   ```python
   # In chunker.py
   def _split_sentences(self, text):
       # Use better sentence splitting
       sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
       return [s.strip() for s in sentences if s.strip()]
   ```

### Issue: Poor Chunk Boundaries

**Symptoms:**
- `test_chunks_end_at_sentence_boundaries` fails
- <60% good boundaries

**Solutions:**

1. **Use sentence-based chunking:**
   ```python
   chunker = TextChunker(chunking_strategy="sentence")
   ```

2. **Improve sentence detection:**
   ```python
   # Handle abbreviations better
   def _split_sentences(self, text):
       # Protect abbreviations
       text = text.replace("Mr.", "Mr")
       text = text.replace("Mrs.", "Mrs")
       text = text.replace("Dr.", "Dr")
       text = text.replace("Rs.", "Rs")
       text = text.replace("Cr.", "Cr")
       
       sentences = re.split(r'(?<=[.!?])\s+', text)
       return sentences
   ```

---

## Groww Mapping Issues

### Issue: Low Mapping Rate

**Symptoms:**
- `test_mapping_statistics` fails
- <50% mapping rate

**Solutions:**

1. **Verify AMC slug mappings:**
   ```python
   # In groww_mapper.py, ensure all AMCs are mapped
   self.amc_slug_mapping = {
       "SBI Mutual Fund": "sbi-mutual-funds",
       "HDFC Mutual Fund": "hdfc-mutual-funds",
       "ICICI Prudential Mutual Fund": "icici-prudential-mutual-funds",
       "Axis Mutual Fund": "axis-mutual-funds",
       "Nippon India Mutual Fund": "nippon-india-mutual-funds",
   }
   ```

2. **Improve category identification:**
   ```python
   # Add more keywords
   "expense_ratio": {
       "keywords": ["expense ratio", "fees", "charges", "expense", "cost"],
       ...
   }
   ```

### Issue: Invalid Groww URLs

**Symptoms:**
- `test_groww_urls_are_valid` fails
- Malformed URLs

**Solutions:**

1. **Validate URL construction:**
   ```python
   def build_groww_url(self, category, fund_slug=None, amc_slug=None):
       url = self.build_url(...)
       
       # Validate before returning
       if not self._validate_groww_url(url):
           logger.warning(f"Invalid Groww URL: {url}")
           return None
       
       return url
   
   def _validate_groww_url(self, url):
       return url.startswith("https://groww.in/mutual-funds/")
   ```

---

## General Troubleshooting

### Re-run Pipeline After Fixes

```bash
# Clear old data
rm -rf data/vectordb
rm data/*.json

# Re-run pipeline
python run_ingestion.py --reset-db

# Re-run validation
python data_ingestion/validation/run_validation.py
```

### Incremental Fixes

1. Fix one category of issues at a time
2. Re-run specific test suite
3. Verify fix doesn't break other tests
4. Move to next issue

### Debugging Tips

```python
# Add verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check intermediate outputs
print(f"Scraped: {len(scraped_data)} documents")
print(f"Processed: {len(processed_docs)} documents")
print(f"Chunks: {len(chunks)}")
print(f"With embeddings: {len([c for c in chunks if 'embedding' in c])}")
```

---

## Prevention

### Pre-commit Checks

```bash
# Add to .git/hooks/pre-commit
pytest data_ingestion/validation/ --tb=short
```

### CI/CD Integration

```yaml
# In .github/workflows/ci.yml
- name: Run Validation Tests
  run: |
    python run_ingestion.py
    python data_ingestion/validation/run_validation.py
```

### Regular Monitoring

- Run validation after each ingestion
- Track metrics over time
- Set up alerts for quality degradation

---

## Need Help?

If issues persist:
1. Check test output for specific error messages
2. Review validation report for patterns
3. Check individual module logs
4. Verify data sources are accessible
5. Ensure all dependencies are installed

---

**Note:** This guide covers common issues. Specific issues may require custom solutions based on your data and requirements.

