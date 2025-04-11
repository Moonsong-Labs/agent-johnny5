# GitHub MCP Agent Example
import asyncio
import os
import sys
import subprocess
import getpass
import requests
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Load environment variables from .env file
load_dotenv('../.env')

# Global variable to store the MCP server process
_mcp_server_process = None

# Initialize with empty tools by default
# Don't try to run asyncio at module import time
github_tools = []

# --- Step 1: Token Validation and Setup ---
def validate_and_setup_token():
    """Validates the GitHub token and prompts for a new one if needed."""
    # Try to get the token from the environment variable first
    env_token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    print(f"Debug: GitHub token from environment: {'Present' if env_token else 'Missing'}")

    # Use the provided token as a fallback
    provided_token = ""
    print(f"Debug: Using provided token in code: {provided_token[:4]}...{provided_token[-4:]}")

    # Use environment variable if available, otherwise use the provided token
    GITHUB_TOKEN = env_token if env_token else provided_token
    
    # Validate the token format
    if not GITHUB_TOKEN or not GITHUB_TOKEN.startswith("ghp_"):
        print("Error: GitHub token appears to be invalid. It should start with 'ghp_'")
        print(f"Token format: {'Valid' if GITHUB_TOKEN and GITHUB_TOKEN.startswith('ghp_') else 'Invalid'}")
        print(f"Token length: {len(GITHUB_TOKEN) if GITHUB_TOKEN else 0}")

    # We could check if the token is valid by making a simple API request
    print("Performing a test GitHub API request to validate token...")
    token_is_valid = False
    try:
        response = requests.get('https://api.github.com/user', headers={'Authorization': f'token {GITHUB_TOKEN}'})
        if response.status_code == 200:
            user_data = response.json()
            print(f"Debug: Token validated successfully. Authenticated as: {user_data.get('login')}")
            token_is_valid = True
        else:
            print(f"Debug: Token validation failed with status code: {response.status_code}")
            print(f"Debug: Response: {response.text}")
    except Exception as e:
        print(f"Debug: Error validating token: {str(e)}")

    # If token is invalid, prompt for a new one
    if not token_is_valid:
        print("\n⚠️ The GitHub token appears to be invalid or expired.")
        use_new_token = input("Would you like to provide a new GitHub token? (y/n): ").lower() == 'y'
        
        if use_new_token:
            # Using getpass for more secure input
            new_token = getpass.getpass("Enter your GitHub Personal Access Token: ")
            if new_token and new_token.strip():
                GITHUB_TOKEN = new_token.strip()
                print(f"Using new token: {GITHUB_TOKEN[:4]}...{GITHUB_TOKEN[-4:]}")
                
                # Validate the new token
                try:
                    response = requests.get('https://api.github.com/user', headers={'Authorization': f'token {GITHUB_TOKEN}'})
                    if response.status_code == 200:
                        user_data = response.json()
                        print(f"✅ New token validated successfully. Authenticated as: {user_data.get('login')}")
                        token_is_valid = True
                    else:
                        print(f"❌ New token validation failed with status code: {response.status_code}")
                        print(f"Response: {response.text}")
                except Exception as e:
                    print(f"Error validating new token: {str(e)}")
            else:
                print("No token provided. Continuing with original token.")
        else:
            print("Continuing with original token (which appears to be invalid).")

    # Print token info (safely)
    if GITHUB_TOKEN:
        print(f"Using GitHub token: {GITHUB_TOKEN[:4]}...{GITHUB_TOKEN[-4:]}")
    
    # If token is still invalid, raise exception to prevent proceeding
    if not token_is_valid:
        raise ValueError("GitHub token is invalid or expired. Please provide a valid token.")
    
    return GITHUB_TOKEN

# Initialize the token at module load time
try:
    GITHUB_TOKEN = validate_and_setup_token()
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
except Exception as e:
    print(f"Error setting up GitHub token: {e}")
    GITHUB_TOKEN = None
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')

# Install node-fetch globally if not already installed (exactly as in run_github_agent.py)
try:
    print("Ensuring node-fetch is installed...")
    subprocess.run(["npm", "list", "-g", "node-fetch"], 
                  stdout=subprocess.PIPE, 
                  stderr=subprocess.PIPE,
                  check=True)
    print("node-fetch is already installed")
except subprocess.CalledProcessError:
    print("Installing node-fetch globally...")
    try:
        subprocess.run(["npm", "install", "-g", "node-fetch"], check=True)
        print("node-fetch installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install node-fetch: {e}")
        print("Will continue anyway, but expect errors if fetch is used")

# --- Step 2: Configure and Connect to GitHub MCP Server ---
async def get_tools_async():
    """Gets tools from the GitHub MCP Server.
    This implementation matches exactly how it's done in run_github_agent.py
    """
    print("Attempting to connect to GitHub MCP server...")
    print(f"Debug: Token format check - Token starts with 'ghp_': {GITHUB_TOKEN.startswith('ghp_')}, Length: {len(GITHUB_TOKEN)}")
    
    # Use a more permissive NODE_OPTIONS that includes fetch polyfill
    env_vars = {
        "GITHUB_TOKEN": GITHUB_TOKEN,
        "GOOGLE_API_KEY": GOOGLE_API_KEY,
        "NODE_OPTIONS": "--no-warnings --experimental-fetch",
        "DEBUG": "mcp:*"  # Enable MCP debug logging
    }
    
    # Add NODE_PATH to help find node-fetch if installed
    npm_prefix = subprocess.check_output(["npm", "config", "get", "prefix"], 
                                         text=True).strip()
    node_path = os.path.join(npm_prefix, "lib", "node_modules")
    env_vars["NODE_PATH"] = node_path
    
    print("Debug: Attempting to connect with environment variables:")
    for key, value in env_vars.items():
        if key == "GITHUB_PERSONAL_ACCESS_TOKEN":
            print(f"  {key}: {value[:4]}...{value[-4:]}")
        elif key == "GOOGLE_API_KEY":
            print(f"  {key}: [REDACTED]")
        else:
            print(f"  {key}: {value}")
    
    tools, exit_stack = await MCPToolset.from_server(
        # Use StdioServerParameters with npx directly - exactly as in run_github_agent.py
        connection_params=StdioServerParameters(
            command='npx',
            args=[
                "-y",
                "--node-options=--experimental-fetch",  # Request experimental fetch support
                "@modelcontextprotocol/server-github"   # The MCP server package
            ],
            env=env_vars
        )
    )
    print(f"MCP Toolset created successfully with {len(tools)} tools:")
    # Print information about the available tools to help with debugging
    for i, tool in enumerate(tools):
        print(f"  Tool {i+1}: {tool.name}")
        if hasattr(tool, 'description'):
            print(f"    Description: {tool.description}")
    
    return tools, exit_stack

# --- Step 3: Create the Agent ---
# Store global references to tools and exit_stack
_tools = None
_exit_stack = None

async def get_github_tools():
    """Fetches and caches GitHub tools."""
    global _tools, _exit_stack
    if _tools is None:
        _tools, _exit_stack = await get_tools_async()
    return _tools

# Inherit from LlmAgent to add lazy loading capability
class LazyLoadingLlmAgent(LlmAgent):
    """An LlmAgent that lazy-loads tools when first needed."""
    
    async def _run_async_impl(self, ctx):
        """Override _run_async_impl to ensure tools are loaded first."""
        await self._ensure_tools_loaded()
        async for event in super()._run_async_impl(ctx):
            yield event
    
    async def _ensure_tools_loaded(self):
        """Ensure the agent has tools loaded before running."""
        global _tools, _exit_stack
        
        # Skip if tools already loaded
        if self.tools and len(self.tools) > 0:
            return True
        
        try:
            # Attempt to load tools if not loaded yet
            if _tools is None:
                print("Lazy initialization: Loading GitHub tools on first use...")
                _tools, _exit_stack = await get_tools_async()
                print(f"Lazy initialization: Successfully loaded {len(_tools)} GitHub tools.")
            
            # Update our tools with the loaded tools
            self.tools = _tools
            print("Agent updated with GitHub tools.")
            return True
        except Exception as e:
            print(f"Error lazy-loading GitHub tools: {e}")
            return False

# Create the agent with initially empty tools using our LazyLoadingLlmAgent
root_agent = LazyLoadingLlmAgent(
    model='gemini-2.0-flash-exp',
    name='GitHubAssistant',
    description="An assistant that can help with GitHub repository management and operations.",
    instruction="""
    You are a GitHub assistant that can help with repository management, code search, and GitHub operations.
    
    IMPORTANT: Do NOT import any modules or libraries. The GitHub tools are already available 
    to you as functions. Simply call them directly by name when needed.
    
    Common GitHub functions you can use:
    - search_repositories(query="search term") - Search for repositories
    - get_repository(owner="owner", repo="repo") - Get repository details
    - list_issues(owner="owner", repo="repo") - List repository issues
    - create_issue(owner="owner", repo="repo", title="title", body="body") - Create an issue
    - get_user(username="username") - Get user information
    
    When searching for repositories:
    1. Use specific search terms
    2. Format the response in a readable way
    3. Include important details like stars, description, and language
    4. Sort by relevance or stars
    5. Limit the number of results to the most relevant ones
    
    Always examine the tool response carefully and provide detailed, helpful responses about 
    the GitHub information you find. Format your responses in a readable way with repository names, 
    issue numbers, and other relevant information.
    """,
    tools=github_tools
)

# --- Web Mode Initialization ---
# This function gets called by ADK web framework when using 'adk web'
async def initialize_web_agent_async():
    """Initialize the GitHub agent for web mode asynchronously.
    This is the async implementation that should be called within an existing event loop.
    """
    global GITHUB_TOKEN, _tools, _exit_stack, root_agent
    
    print("Initializing GitHub agent for web mode asynchronously...")
    
    # Check if we need to validate the token
    if not GITHUB_TOKEN:
        try:
            print("GitHub token not available. Attempting to validate...")
            GITHUB_TOKEN = validate_and_setup_token()
            print(f"Token validated for web mode: {GITHUB_TOKEN[:4]}...{GITHUB_TOKEN[-4:]}")
        except Exception as e:
            print(f"⚠️ Web mode: Error setting up GitHub token: {e}")
            print("⚠️ GitHub agent may not function properly in web mode.")
            return False
    
    # Initialize tools if needed
    try:
        print("Initializing GitHub MCP tools for web mode...")
        _tools, _exit_stack = await get_tools_async()
        print(f"✅ Successfully initialized {len(_tools)} GitHub MCP tools for web mode.")
        print(f"✅ Supported tools: {_tools}.")
        
        # Update the root_agent with the tools
        if _tools:
            root_agent.tools = _tools
            print("✅ Updated agent with the fetched GitHub tools.")
    except Exception as e:
        print(f"⚠️ Web mode: Failed to initialize GitHub tools: {e}")
        return False
    
    print("✅ GitHub agent successfully initialized for web mode.")
    return True

# Synchronous wrapper for web mode initialization
def initialize_web_agent():
    """Initialize the GitHub agent for web mode.
    This is called by the ADK web framework when using 'adk web'.
    
    Note: This doesn't immediately initialize the tools to avoid asyncio.run() errors.
    Tools will be initialized on first use.
    """
    print("Preparing GitHub agent for web mode...")
    print("Tools will be initialized on first agent use to avoid asyncio conflicts.")
    return True

# Initialize web mode on module load - but don't run async code
try:
    _web_initialized = initialize_web_agent()
    print(f"Web mode preparation: {'Successful' if _web_initialized else 'Failed'}")
except Exception as e:
    print(f"Error during web mode preparation: {e}")
    _web_initialized = False

# --- Step 5: Main Execution Logic (for direct script execution) ---
async def async_main():
    """Run the agent directly for testing purposes."""
    # Add explicit import and configuration for Google Generative AI
    import os
    from google import generativeai as genai
    
    # Load environment variables from .env file again to ensure they're loaded
    print("Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv('.env')
    
    # Set up Google Generative AI with API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"Initializing Google Generative AI with API key: {api_key[:5]}...{api_key[-5:]}")
        genai.configure(api_key=api_key)
    else:
        print("ERROR: Google API key not found in environment variables.")
        return
    
    # Continue with the rest of the function as before
    session_service = InMemorySessionService()
    artifacts_service = InMemoryArtifactService()

    session = session_service.create_session(
        state={}, app_name='github_mcp_app', user_id='github_user'
    )

    query = "Search for popular Python libraries and show their details"
    print(f"User Query: '{query}'")
    content = types.Content(role='user', parts=[types.Part(text=query)])

    # Use our lazy-loading agent directly - it will load tools when needed
    print("Setting up agent...")
    
    # Create and run the runner with our LazyLoadingLlmAgent directly
    runner = Runner(
        app_name='github_mcp_app',
        agent=root_agent,  # Use the agent directly now 
        artifact_service=artifacts_service,
        session_service=session_service,
    )

    try:
        # Ensure tools are loaded before running
        print("Preloading tools...")
        await root_agent._ensure_tools_loaded()
        
        print("Running agent...")
        events_async = runner.run_async(
            session_id=session.id, user_id=session.user_id, new_message=content
        )

        async for event in events_async:
            print(f"Event received: {event}")
            
        print("Agent execution completed successfully")
    finally:
        # Crucial Cleanup: Ensure the MCP server process connection is closed.
        print("Closing MCP server connection...")
        if _exit_stack:
            await _exit_stack.aclose()
        print("Cleanup complete.")

# Run the agent if this file is executed directly
if __name__ == '__main__':
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nAgent stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

# --- Web Mode Cleanup ---
# This can be called when the web application is shut down
async def cleanup_web_resources():
    """Clean up resources when the web application is shutting down."""
    global _exit_stack
    
    print("Cleaning up GitHub agent web resources...")
    
    # Close the MCP server connection
    if _exit_stack:
        try:
            print("Closing MCP server connection...")
            await _exit_stack.aclose()
            print("MCP server connection closed.")
        except Exception as e:
            print(f"Error closing MCP server connection: {e}")
    
    print("GitHub agent web resources cleanup complete.")