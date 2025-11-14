# Facts-Only FAQ Assistant

A RAG (Retrieval-Augmented Generation) based chatbot widget that answers factual questions about mutual fund schemes using verified sources from AMC, SEBI, and AMFI websites.

## Overview

The Facts-Only FAQ Assistant is an embedded chat widget that provides instant, accurate answers to factual questions about mutual fund schemes. It uses verified sources from official AMC (Asset Management Company), SEBI (Securities and Exchange Board of India), and AMFI (Association of Mutual Funds in India) websites to provide citation-backed responses.

**Key Features:**
- ✅ Answers factual questions about mutual fund schemes
- ✅ Provides source citations for every answer
- ✅ Prioritizes Groww website pages when available
- ✅ Strictly avoids investment advice
- ✅ Built with RAG architecture using LLM (Gemini or open-source)
- ✅ Responsive chat widget for desktop

## Project Structure

```
RAG-LLM-based-FAQ-Assistant-v2/
├── backend/                 # FastAPI backend service
│   ├── api/                # API routes
│   ├── services/           # Business logic (RAG, LLM, vector store)
│   ├── models/             # Pydantic models
│   ├── config/             # Configuration
│   └── utils/              # Utility functions
├── frontend/               # React/TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   ├── styles/         # CSS and design tokens
│   │   └── types/          # TypeScript types
│   └── public/
├── data_ingestion/         # Data scraping and processing pipeline
│   ├── scraper.py          # Web scraping module
│   ├── processor.py         # Document processing
│   ├── embedder.py         # Vector embeddings
│   └── validation/         # Data validation tests
├── docs/                   # Documentation
├── infrastructure/         # Deployment configurations
└── tasks/                  # Project tasks and PRD

```

## Prerequisites

- **Python 3.11+** (for backend)
- **Node.js 20+** (for frontend)
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Google Gemini API Key** (or access to open-source LLM)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd RAG-LLM-based-FAQ-Assistant-v2
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file and configure
cp .env.example .env
# Edit .env and set VITE_API_BASE_URL
```

### 4. Run the Application

**Option A: Run locally**

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

**Option B: Run with Docker**

```bash
# Build and start containers
docker-compose up --build

# Backend will be available at http://localhost:8000
# Frontend will be available at http://localhost:80
```

## Configuration

See [Environment Setup Guide](docs/ENVIRONMENT_SETUP.md) for detailed configuration instructions.

### Key Environment Variables

**Backend (Local Development):**
- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `ENVIRONMENT` - Environment name (development/production)
- `DEBUG` - Enable debug mode (true/false)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/WARNING/ERROR)
- `VECTORDB_PATH` - Path to vector database
- `CORS_ORIGINS_ENV` - Comma-separated list of allowed CORS origins

**Backend (Production - Railway):**
- `GEMINI_API_KEY` - Your Google Gemini API key (required)
- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `CORS_ORIGINS_ENV` - Your Vercel frontend URL
- `VECTORDB_PATH=/app/data/vectordb`
- `METADATA_PATH=/app/data/metadata_index.json`
- `SOURCE_URLS_PATH=/app/data/source_urls.json`

**Frontend (Production - Vercel):**
- `VITE_API_BASE_URL` - Your Railway backend URL (required)

See [docs/ENVIRONMENT_VARIABLES.md](docs/ENVIRONMENT_VARIABLES.md) for complete list.

## Data Ingestion

To populate the knowledge base with mutual fund data:

1. Provide 5 AMC names and their source URLs (as per task 2.1.1)
2. Run the data ingestion pipeline:

```bash
cd data_ingestion
python ingestion_pipeline.py
```

3. Validate the ingested data:

```bash
pytest data_ingestion/validation/
```

## Development

### Backend Development

```bash
cd backend
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest
```

### Frontend Development

```bash
cd frontend

# Start development server
npm run dev

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

## API Documentation

Once the backend is running, API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

See [API Documentation](docs/API.md) for detailed API reference.

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Data ingestion validation
cd data_ingestion
pytest validation/
```

## Deployment

### Quick Deployment Guide

For deploying to Railway (backend) and Vercel (frontend):

1. **Set up API key locally:**
   ```bash
   # Windows
   .\scripts\setup-env-local.ps1
   
   # Linux/Mac
   bash scripts/setup-env-local.sh
   ```

2. **Verify configurations:**
   ```bash
   # Verify Railway config
   .\scripts\verify-railway-config.ps1
   
   # Verify Vercel config
   .\scripts\verify-vercel-config.ps1
   ```

3. **Follow deployment steps:**
   - See [DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md) for detailed step-by-step instructions
   - Use [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) to track progress

### Deployment Documentation

- **[DEPLOYMENT_STEPS.md](DEPLOYMENT_STEPS.md)** - Complete deployment guide with Railway and Vercel
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Quick checklist for deployment
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - General deployment documentation
- **[docs/RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md)** - Railway-specific guide
- **[docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md)** - Vercel-specific guide

## Documentation

- [Environment Setup](docs/ENVIRONMENT_SETUP.md) - Environment variable configuration
- [API Documentation](docs/API.md) - API endpoints and usage
- [Deployment Guide](docs/DEPLOYMENT.md) - Deployment instructions
- [Design Tokens](docs/DESIGN_TOKENS.md) - Groww design system integration

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions, please open an issue in the repository.

## Acknowledgments

- Built with FastAPI, React, and TypeScript
- Uses ChromaDB for vector storage
- Powered by Google Gemini (or open-source LLM)
- Design system integration with Groww
