# Task List: Facts-Only FAQ Assistant

## Relevant Files

### Backend Files
- `backend/requirements.txt` - Python dependencies for the backend service
- `backend/main.py` - FastAPI application entry point
- `backend/api/routes/chat.py` - API route handler for chat queries
- `backend/api/routes/chat.test.py` - Unit tests for chat API routes
- `backend/services/rag_service.py` - RAG pipeline implementation for retrieval and generation
- `backend/services/rag_service.test.py` - Unit tests for RAG service
- `backend/services/llm_service.py` - LLM integration service (Gemini/open-source)
- `backend/services/llm_service.test.py` - Unit tests for LLM service
- `backend/services/vector_store.py` - Vector database operations and management
- `backend/services/vector_store.test.py` - Unit tests for vector store
- `backend/services/groww_mapper.py` - Service to map queries to Groww website pages
- `backend/services/groww_mapper.test.py` - Unit tests for Groww mapper
- `backend/models/chat.py` - Pydantic models for chat request/response
- `backend/models/knowledge.py` - Data models for knowledge base chunks
- `backend/utils/citation.py` - Utility functions for generating citations and source links
- `backend/utils/citation.test.py` - Unit tests for citation utilities
- `backend/config/settings.py` - Configuration management using environment variables
- `backend/config/database.py` - Database connection configuration

### Data Ingestion Pipeline Files
- `data_ingestion/scraper.py` - Web scraping module for AMC/SEBI/AMFI websites
- `data_ingestion/scraper.test.py` - Unit tests for scraper
- `data_ingestion/processor.py` - Document processing and chunking module
- `data_ingestion/processor.test.py` - Unit tests for processor
- `data_ingestion/embedder.py` - Vector embedding generation module
- `data_ingestion/embedder.test.py` - Unit tests for embedder
- `data_ingestion/ingestion_pipeline.py` - Main pipeline orchestrator for data ingestion
- `data_ingestion/ingestion_pipeline.test.py` - Unit tests for ingestion pipeline
- `data_ingestion/source_tracker.py` - Source URL tracking and validation system
- `data_ingestion/source_tracker.test.py` - Unit tests for source tracker
- `data_ingestion/groww_mapper.py` - Module to create mapping between information and Groww pages
- `data_ingestion/groww_mapper.test.py` - Unit tests for Groww mapper in ingestion
- `data_ingestion/validation/test_data_quality.py` - Test suite for validating scraped content quality
- `data_ingestion/validation/test_source_tracking.py` - Tests to validate source URLs are correctly stored
- `data_ingestion/validation/test_embeddings.py` - Tests to verify vector embeddings generation
- `data_ingestion/validation/test_metadata.py` - Tests to validate metadata storage accuracy
- `data_ingestion/validation/test_chunking.py` - Tests to verify chunking strategy
- `data_ingestion/validation/test_groww_mapping.py` - Tests to validate Groww page mappings

### Frontend Files
- `frontend/package.json` - Node.js dependencies for frontend
- `frontend/src/components/ChatWidget.tsx` - Main chat widget component
- `frontend/src/components/ChatWidget.test.tsx` - Unit tests for ChatWidget
- `frontend/src/components/MessageList.tsx` - Component to display chat messages
- `frontend/src/components/MessageList.test.tsx` - Unit tests for MessageList
- `frontend/src/components/MessageBubble.tsx` - Individual message bubble component (user/bot)
- `frontend/src/components/MessageBubble.test.tsx` - Unit tests for MessageBubble
- `frontend/src/components/SourcesSection.tsx` - Component to display source links section
- `frontend/src/components/SourcesSection.test.tsx` - Unit tests for SourcesSection
- `frontend/src/services/api.ts` - API client for backend communication
- `frontend/src/services/api.test.ts` - Unit tests for API client
- `frontend/src/styles/design-tokens.css` - CSS variables mapping Groww design tokens
- `frontend/src/styles/widget.css` - Widget-specific styles
- `frontend/src/utils/formatters.ts` - Utility functions for formatting messages and links
- `frontend/src/utils/formatters.test.ts` - Unit tests for formatters
- `frontend/src/types/chat.ts` - TypeScript type definitions for chat data structures

### Infrastructure & Configuration Files
- `docker-compose.yml` - Docker compose configuration for local development
- `Dockerfile.backend` - Dockerfile for backend service
- `Dockerfile.frontend` - Dockerfile for frontend application
- `.env.example` - Example environment variables file
- `.github/workflows/ci.yml` - CI/CD pipeline configuration
- `infrastructure/terraform/` - Terraform configuration for cloud infrastructure (if using)
- `infrastructure/kubernetes/` - Kubernetes manifests (if using)
- `scripts/setup.sh` - Setup script for development environment
- `scripts/ingest_data.py` - Script to run data ingestion pipeline

### Documentation Files
- `docs/DESIGN_TOKENS.md` - Design token mapping document for Groww design system
- `docs/API.md` - API documentation
- `docs/DEPLOYMENT.md` - Deployment guide
- `README.md` - Project overview and setup instructions

### Notes

- Unit tests should typically be placed alongside the code files they are testing (e.g., `ChatWidget.tsx` and `ChatWidget.test.tsx` in the same directory).
- Use `pytest` for Python backend tests and `npm test` or `jest` for frontend tests.
- The project structure separates backend (Python/FastAPI), frontend (React/TypeScript), and data ingestion pipeline.
- Environment variables should be managed through `.env` files and configuration modules.

## Instructions for Completing Tasks

**IMPORTANT:** As you complete each task, you must check it off in this markdown file by changing `- [ ]` to `- [x]`. This helps track progress and ensures you don't skip any steps.

Example:
- `- [ ] 1.1 Read file` → `- [x] 1.1 Read file` (after completing)

Update the file after completing each sub-task, not just after completing an entire parent task.

## Tasks

- [ ] 1.0 Set up project structure and dependencies
  - [x] 1.1 Create project root directory structure (backend/, frontend/, data_ingestion/, docs/, infrastructure/)
  - [x] 1.2 Initialize backend Python project with virtual environment and requirements.txt
  - [x] 1.3 Install backend dependencies (FastAPI, uvicorn, langchain, chromadb/pinecone, sentence-transformers, google-generativeai, requests, beautifulsoup4, pydantic)
  - [x] 1.4 Initialize frontend project with React/TypeScript and package.json
  - [x] 1.5 Install frontend dependencies (React, TypeScript, axios, CSS framework matching Groww's stack)
  - [x] 1.6 Set up environment configuration system (.env.example with all required variables)
  - [x] 1.7 Create Docker configuration files (Dockerfile.backend, Dockerfile.frontend, docker-compose.yml)
  - [x] 1.8 Set up basic project documentation structure (README.md, docs/ folder)
  - [x] 1.9 Configure linting and formatting tools (black, flake8 for Python; ESLint, Prettier for TypeScript)

- [x] 2.0 Build knowledge base ingestion pipeline
  - [x] 2.1 Create web scraper module to crawl AMC/SEBI/AMFI official websites
    - [x] 2.1.1 Request user to provide 5 AMC names and their relevant source URLs
    - [x] 2.1.2 Configure scraper to scrape only the provided AMC URLs (no broad crawling)
  - [x] 2.2 Implement source URL tracking system to store and validate source links
  - [x] 2.3 Create document processor to clean, parse, and chunk HTML/text content
  - [x] 2.4 Implement text chunking strategy (sentence-based or semantic chunking)
  - [x] 2.5 Create vector embedding generation module using sentence transformers
  - [x] 2.6 Set up vector database (ChromaDB/Pinecone/Weaviate) and create schema
  - [x] 2.7 Implement metadata storage linking chunks to source URLs and content type
  - [x] 2.8 Create Groww website mapping module to identify and map information to Groww pages
  - [x] 2.9 Build data ingestion pipeline orchestrator to process provided AMC source links
  - [x] 2.10 Implement data validation and quality checks (duplicate detection, content validation)
  - [x] 2.11 Create script to run ingestion pipeline with user-provided source links
  - [x] 2.12 Add error handling and retry logic for web scraping operations

- [x] 2.13 Validate scraped and stored data
  - [x] 2.13.1 Create data validation test suite to verify scraped content quality
  - [x] 2.13.2 Implement tests to validate source URLs are correctly stored and linked to chunks
  - [x] 2.13.3 Create tests to verify vector embeddings are generated correctly
  - [x] 2.13.4 Implement tests to validate metadata (source URLs, content type) is stored accurately
  - [x] 2.13.5 Create tests to verify chunking strategy produces appropriate content segments
  - [x] 2.13.6 Implement tests to validate Groww page mappings are correctly stored
  - [x] 2.13.7 Run validation test suite and document any data quality issues
  - [x] 2.13.8 Fix any data quality issues identified during validation

- [x] 3.0 Implement RAG backend service and API
  - [x] 3.1 Set up FastAPI application with basic structure and middleware
  - [x] 3.2 Create Pydantic models for chat request/response with source citations
  - [x] 3.3 Implement vector store service for semantic search and retrieval
  - [x] 3.4 Create RAG retrieval pipeline to fetch relevant chunks based on user query
  - [x] 3.5 Integrate LLM service (Gemini or open-source LLM) with configurable provider
  - [x] 3.6 Implement response generation with prompt engineering to ensure factual, citation-backed responses
  - [x] 3.7 Add prompt guardrails to prevent investment advice generation
  - [x] 3.8 Create citation generation utility to format source links (inline and sources section)
  - [x] 3.9 Implement Groww page checking service to map queries to Groww website pages
  - [x] 3.10 Create fallback logic: check Groww pages first, then external sources, then generic fallback
  - [x] 3.11 Implement chat API endpoint (/api/chat) with request validation
  - [x] 3.12 Add error handling for malformed queries, LLM failures, and vector store errors
  - [x] 3.13 Implement rate limiting middleware to prevent abuse
  - [x] 3.14 Add logging and request tracking for monitoring
  - [x] 3.15 Create health check endpoint (/health) for service monitoring

- [ ] 4.0 Build chat widget frontend component
  - [x] 4.1 Extract and document Groww design tokens (colors, typography, spacing, etc.)
  - [x] 4.2 Create CSS variables file mapping Groww design tokens to widget styles
  - [x] 4.3 Set up widget component structure with TypeScript types
  - [x] 4.4 Create ChatWidget main component with floating button and expandable interface
  - [x] 4.5 Implement MessageList component to display conversation history
  - [x] 4.6 Create MessageBubble component with distinct styling for user vs bot messages
  - [x] 4.7 Implement inline source link rendering within message text
  - [x] 4.8 Create SourcesSection component to display source URLs at end of responses
  - [x] 4.9 Add chat input field with send button and enter key support
  - [x] 4.10 Implement loading state indicator during API calls
  - [x] 4.11 Create API client service to communicate with backend
  - [ ] 4.12 Add error handling and display for API failures
  - [ ] 4.13 Implement responsive design for different desktop screen sizes
  - [ ] 4.14 Add accessibility features (keyboard navigation, ARIA labels, screen reader support)
  - [ ] 4.15 Style source links to be clearly visible and open in new tab/window
  - [ ] 4.16 Test widget visual consistency against Groww design system

- [ ] 5.0 Set up independent hosting infrastructure and handle Groww page mapping
  - [ ] 5.1 Choose hosting platform (AWS/GCP/Vercel/Railway/etc.) for backend and frontend
  - [ ] 5.2 Set up backend deployment configuration (environment variables, secrets management)
  - [ ] 5.3 Configure frontend deployment (static hosting or containerized)
  - [ ] 5.4 Set up domain name and SSL certificate configuration
  - [ ] 5.5 Create Groww page mapping database/config file (JSON/YAML/database)
  - [ ] 5.6 Implement Groww page mapping lookup service in backend
  - [ ] 5.7 Set up CORS configuration to allow widget embedding (if needed)
  - [ ] 5.8 Configure CDN for frontend assets (if applicable)
  - [ ] 5.9 Set up CI/CD pipeline for automated deployments
  - [ ] 5.10 Create deployment documentation with step-by-step instructions
  - [ ] 5.11 Configure environment-specific settings (dev/staging/prod)

- [ ] 6.0 Implement testing, monitoring, and deployment
  - [ ] 6.1 Write unit tests for backend services (RAG service, LLM service, vector store)
  - [ ] 6.2 Write unit tests for API endpoints
  - [ ] 6.3 Write unit tests for data ingestion pipeline components
  - [ ] 6.4 Write unit tests for frontend components (ChatWidget, MessageList, etc.)
  - [ ] 6.5 Write integration tests for end-to-end chat flow
  - [ ] 6.6 Implement response accuracy testing (test against known queries)
  - [ ] 6.7 Add compliance testing to ensure no investment advice is generated
  - [ ] 6.8 Set up application monitoring (error tracking, performance metrics)
  - [ ] 6.9 Configure logging system with appropriate log levels
  - [ ] 6.10 Set up alerting for critical errors and performance degradation
  - [ ] 6.11 Create monitoring dashboard for key metrics (response time, error rate, usage)
  - [ ] 6.12 Perform load testing to ensure system handles concurrent requests
  - [ ] 6.13 Create test data set with sample queries and expected responses
  - [ ] 6.14 Document testing procedures and run test suite before deployment
