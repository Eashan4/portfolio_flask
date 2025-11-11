"""
Vercel serverless function entry point for Flask app
This file is the entry point for Vercel's serverless Python runtime
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects the app to be exported as 'app'
# The @vercel/python builder will wrap this in a serverless function

