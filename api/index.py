"""
Vercel Serverless Function Entry Point for FastAPI Backend

This file adapts the FastAPI application to work with Vercel's serverless function runtime.
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mangum import Mangum
from backend.main import app

# Create ASGI adapter for Vercel
mangum_handler = Mangum(app, lifespan="off")

# Vercel expects the handler function to be named 'handler'
def handler(event, context):
    """
    Vercel serverless function handler
    """
    return mangum_handler(event, context)

