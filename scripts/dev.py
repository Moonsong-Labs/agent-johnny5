#!/usr/bin/env python
"""
Development server for Agent Johnny5 system.
"""
import os
import sys
import logging
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from fastapi import FastAPI
from uvicorn import run
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("dev")

# Create FastAPI app
app = FastAPI(title="Agent Johnny5", description="Code repository analysis agent system")

@app.get("/")
async def root():
    return {"message": "Welcome to Agent Johnny5", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/models")
async def list_models():
    """List available Google Generative AI models."""
    try:
        models = genai.list_models()
        return {"models": [m.name for m in models]}
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return {"error": str(e)}

def main():
    """Run the development server."""
    logger.info("Starting development server")
    port = int(os.getenv("MAIN_AGENT_PORT", 8000))
    run(
        "scripts.dev:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )

if __name__ == "__main__":
    main() 