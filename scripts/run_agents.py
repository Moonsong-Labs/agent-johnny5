#!/usr/bin/env python
"""
Script to run the multi-agent system.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.mainagent import MainAgent

async def main():
    print("Initializing Agent Johnny5 multi-agent system...")
    
    # Create the main orchestrator agent
    main_agent = MainAgent()
    
    # Example query - this will be routed to the PullSage agent
    query = {
        "prompt": "Hey, I want to know about the latest merged PRs in the repo" ,
        "agent": "pullsage"  # Explicitly specify the agent (though "pullsage" is the default)
    }
    
    print("\nSending query to the system:")
    print(f"Query: {query}")
    
    # Process the query through the main agent
    result = await main_agent.process(query)
    
    print("\nResult:")
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"Agent: {result['agent']}")
        print(f"Response: {result['result']['message']}")
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main()) 