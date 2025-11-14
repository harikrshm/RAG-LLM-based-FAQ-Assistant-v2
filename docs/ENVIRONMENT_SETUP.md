# Environment Setup Guide

This document describes how to set up environment variables for the Facts-Only FAQ Assistant project.

## Backend Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the required values:

```bash
cp backend/.env.example backend/.env
```

### Required Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key for LLM integration
- `SECRET_KEY`: A secret key for security (generate a strong random string)

### Optional Variables

All other variables have default values but can be customized based on your needs.

## Frontend Environment Variables

Copy `frontend/.env.example` to `frontend/.env`:

```bash
cp frontend/.env.example frontend/.env
```

### Required Variables

- `VITE_API_BASE_URL`: The backend API URL (default: http://localhost:8000)

### Note

Frontend environment variables must be prefixed with `VITE_` to be accessible in the React application.

## Environment Files

- `.env.example`: Template files with all available variables
- `.env`: Your actual environment file (not committed to git)
- `.env.local`: Local overrides (not committed to git)

## Security Notes

1. Never commit `.env` files to version control
2. Always use `.env.example` as a template
3. Generate strong `SECRET_KEY` values for production
4. Keep API keys secure and rotate them regularly

