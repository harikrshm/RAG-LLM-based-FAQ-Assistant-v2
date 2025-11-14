# Installation Notes

## Known Issues

### ChromaDB Compatibility with Python 3.14

**Issue**: ChromaDB 1.3.4 has compatibility issues with Python 3.14 due to Pydantic v1 dependencies.

**Error**:
```
pydantic.v1.errors.ConfigError: unable to infer type for attribute "chroma_server_nofile"
```

**Solution**: Use Python 3.11 or Python 3.12 for this project.

### Recommended Python Version

- **Python 3.11** or **Python 3.12** (tested and compatible)
- **Not Python 3.14** (ChromaDB compatibility issues)

### Installation Steps

1. **Create a virtual environment with Python 3.11 or 3.12**:
   ```bash
   python3.11 -m venv venv
   # or
   python3.12 -m venv venv
   ```

2. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`

3. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Dependencies Installed So Far (Python 3.14 - Partial)

The following packages have been successfully installed:
- fastapi
- pydantic
- requests
- beautifulsoup4
- httpx
- uvicorn
- sentence-transformers
- numpy
- pyyaml
- tqdm
- tenacity
- rich
- orjson
- importlib-resources
- jsonschema
- tokenizers
- bcrypt
- overrides
- pybase64
- opentelemetry-api
- opentelemetry-sdk
- build
- typer
- mmh3

**Note**: ChromaDB requires Python ≤3.12 for full compatibility.

## Next Steps

1. Switch to Python 3.11 or 3.12
2. Reinstall all dependencies in a new virtual environment
3. Test the vector store service import

## Service Code Status

The vector store service (`backend/services/vector_store.py`) has been implemented and is ready to use once the ChromaDB dependency issue is resolved.

