#!/usr/bin/env python
"""
Development server for Agent Johnny5.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from agents.mainagent import MainAgent

app = FastAPI(title="Agent Johnny5", description="Multi-agent system for various tasks")
main_agent = MainAgent()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "message": "Agent Johnny5 is alive!"}

@app.post("/process")
async def process_request(request: Request):
    """Process a request through the agent system."""
    try:
        data = await request.json()
        result = await main_agent.process(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Run the development server."""
    port = int(os.getenv("MAIN_AGENT_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main() 