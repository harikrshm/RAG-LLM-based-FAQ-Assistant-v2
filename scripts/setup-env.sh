#!/bin/bash

# Environment Setup Script
# Helps set up environment-specific configuration files

set -e

ENVIRONMENT=${1:-development}

echo "Setting up $ENVIRONMENT environment..."

# Backend setup
if [ -d "backend" ]; then
    echo "Setting up backend environment..."
    
    case $ENVIRONMENT in
        development)
            if [ ! -f "backend/.env.development" ]; then
                cp backend/.env.development.example backend/.env.development
                echo "✅ Created backend/.env.development"
                echo "⚠️  Please edit backend/.env.development and add your API keys"
            else
                echo "ℹ️  backend/.env.development already exists"
            fi
            ;;
        staging)
            if [ ! -f "backend/.env.staging" ]; then
                cp backend/.env.staging.example backend/.env.staging
                echo "✅ Created backend/.env.staging"
                echo "⚠️  Please edit backend/.env.staging and add your API keys"
            else
                echo "ℹ️  backend/.env.staging already exists"
            fi
            ;;
        production)
            if [ ! -f "backend/.env.production" ]; then
                cp backend/.env.production.example backend/.env.production
                echo "✅ Created backend/.env.production"
                echo "⚠️  Please edit backend/.env.production and add your API keys"
            else
                echo "ℹ️  backend/.env.production already exists"
            fi
            ;;
        *)
            echo "❌ Unknown environment: $ENVIRONMENT"
            echo "Usage: $0 [development|staging|production]"
            exit 1
            ;;
    esac
fi

# Frontend setup
if [ -d "frontend" ]; then
    echo "Setting up frontend environment..."
    
    case $ENVIRONMENT in
        development)
            if [ ! -f "frontend/.env.development" ]; then
                cp frontend/.env.development.example frontend/.env.development
                echo "✅ Created frontend/.env.development"
            else
                echo "ℹ️  frontend/.env.development already exists"
            fi
            ;;
        staging)
            if [ ! -f "frontend/.env.staging" ]; then
                cp frontend/.env.staging.example frontend/.env.staging
                echo "✅ Created frontend/.env.staging"
            else
                echo "ℹ️  frontend/.env.staging already exists"
            fi
            ;;
        production)
            if [ ! -f "frontend/.env.production" ]; then
                cp frontend/.env.production.example frontend/.env.production
                echo "✅ Created frontend/.env.production"
            else
                echo "ℹ️  frontend/.env.production already exists"
            fi
            ;;
    esac
fi

echo ""
echo "✅ Environment setup complete for $ENVIRONMENT"
echo ""
echo "Next steps:"
echo "1. Edit the .env files and add your API keys"
echo "2. Verify configuration matches your environment"
echo "3. Test locally before deploying"

