"""
Agents package for Agent Johnny5.
"""
import asyncio
import logging
import sys
from typing import Any, Dict

from agents.mainagent import MainAgent
from shared.utils.adk_adapter import format_for_adk, parse_adk_request

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("agents")

# Initialize the main agent globally
logger.info("Initializing MainAgent for ADK...")
main_agent = MainAgent()

async def _process_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a request through the main agent."""
    logger.info(f"Received request: {data}")
    
    # Parse and normalize the request
    normalized_request = parse_adk_request(data)
    logger.info(f"Normalized request: {normalized_request}")
    
    # Process the request through the main agent
    result = await main_agent.process(normalized_request)
    logger.info(f"Agent result: {result}")
    
    # Format the response for ADK
    formatted = format_for_adk(result)
    logger.info(f"Formatted response: {formatted}")
    return formatted

def handle_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entry point for ADK to process requests.
    This is the function specified in adk.config.json.
    """
    logger.info("ADK called handle_request")
    try:
        logger.info(f"Processing request: {data}")
        result = asyncio.run(_process_request(data))
        logger.info(f"Final result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in handle_request: {str(e)}", exc_info=True)
        # Ensure errors are properly formatted for ADK
        return {
            "status": "error",
            "message": f"Error processing request: {str(e)}"
        } 