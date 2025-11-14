#!/bin/bash
# Bash script to set up local .env file for backend
# Run this script from the project root directory

echo "Setting up local .env file for backend..."

BACKEND_ENV_PATH="backend/.env"

# Check if .env file already exists
if [ -f "$BACKEND_ENV_PATH" ]; then
    echo "Warning: backend/.env already exists!"
    read -p "Do you want to overwrite it? (y/N) " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "Skipping .env file creation."
        exit 0
    fi
fi

# Prompt for Gemini API key
echo ""
echo "Please enter your Google Gemini API key."
echo "Get your API key from: https://makersuite.google.com/app/apikey"
echo ""

read -p "Enter your GEMINI_API_KEY: " api_key

if [ -z "$api_key" ]; then
    echo "Error: API key cannot be empty!"
    exit 1
fi

# Create .env file content
cat > "$BACKEND_ENV_PATH" << EOF
# Google Gemini API Key
GEMINI_API_KEY=$api_key

# Environment Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS Configuration (for local development)
# CORS_ORIGINS_ENV=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# Vector Database Paths
VECTORDB_PATH=data/vectordb
METADATA_PATH=data/metadata_index.json
SOURCE_URLS_PATH=data/source_urls.json
EOF

echo ""
echo "Successfully created backend/.env file!"
echo "Location: $BACKEND_ENV_PATH"
echo ""
echo "Next steps:"
echo "1. Verify the .env file contains your API key"
echo "2. Test locally: cd backend && uvicorn main:app --reload"
echo "3. Follow DEPLOYMENT_STEPS.md for Railway and Vercel deployment"

