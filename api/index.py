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
handler = Mangum(app, lifespan="off")

def lambda_handler(event, context):
    """
    AWS Lambda handler (Vercel uses AWS Lambda under the hood)
    """
    return handler(event, context)

