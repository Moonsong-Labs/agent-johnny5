"""
Agent Johnny5 entry point for ADK.
This file serves as a top-level module entry for ADK.
"""
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import directly from agents package
from agents import handle_request

# Export the handle_request function at the top level
__all__ = ["handle_request"] 