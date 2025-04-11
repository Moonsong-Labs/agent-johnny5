"""
ADK Adapter utilities for Agent Johnny5.
"""
from typing import Any, Dict, Optional, Union

def format_for_adk(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the agent's response to be compatible with ADK expectations.
    
    Args:
        response: The response from the agent system
        
    Returns:
        A formatted response that meets ADK's expectations
    """
    # If the response already has the expected structure, return it as is
    if "status" in response and "result" in response and isinstance(response["result"], dict):
        return response
        
    # If response has an error message, format it appropriately
    if "message" in response and response.get("status") == "error":
        return {
            "status": "error",
            "message": response["message"]
        }
    
    # Format success responses
    if "message" in response:
        return {
            "status": "success",
            "result": {
                "message": response["message"],
                "data": response.get("data", {})
            }
        }
    
    # Default case
    return {
        "status": "success",
        "result": response
    }

def parse_adk_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and normalize a request coming from ADK.
    
    Args:
        request: The request data from ADK
        
    Returns:
        A normalized request object for the agent system
    """
    # If ADK provides the input under a specific key, extract it
    if "input" in request and isinstance(request["input"], dict):
        return request["input"]
    
    return request 