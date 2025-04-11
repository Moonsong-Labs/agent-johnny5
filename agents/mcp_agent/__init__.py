try:
    from .agent import (
        root_agent, validate_and_setup_token, get_github_tools, 
        cleanup_web_resources, initialize_web_agent_async,
        LazyLoadingLlmAgent
    )
    
    # Explicitly export web_agent for use with 'adk web'
    # This is the agent that will be used when running with 'adk web'
    web_agent = root_agent
    
    # Export all necessary components
    __all__ = [
        "root_agent", "web_agent", "validate_and_setup_token", 
        "get_github_tools", "cleanup_web_resources", 
        "initialize_web_agent_async", "LazyLoadingLlmAgent"
    ]
except Exception as e:
    # If token validation fails during import, log the error but allow the import to succeed
    import sys
    print(f"Warning: Error importing GitHub agent: {e}", file=sys.stderr)
    print("GitHub agent features may not be available until a valid token is provided.", file=sys.stderr)
    
    # Define placeholders for required exports
    from google.adk.agents import LlmAgent
    
    class LazyLoadingLlmAgent(LlmAgent):
        """An LlmAgent that lazy-loads tools when first needed."""
        
        async def _run_async_impl(self, ctx):
            """Override _run_async_impl to provide a stub implementation."""
            # First attempt to load tools (will return False in stub)
            await self._ensure_tools_loaded()
            # Pass the call to the parent implementation
            async for event in super()._run_async_impl(ctx):
                yield event
        
        async def _ensure_tools_loaded(self):
            """Stub implementation - tools will not be loaded."""
            return False
    
    # Create a basic agent
    root_agent = LazyLoadingLlmAgent(
        model='gemini-2.0-flash-exp',
        name='GitHubAssistant',
        description="GitHub assistant (token validation required)",
        instruction="This is a placeholder. GitHub token validation is required before using this agent.",
        tools=[]
    )
    
    # Ensure web_agent is also exported for 'adk web'
    web_agent = root_agent
    
    # Stub function
    async def get_github_tools():
        return []
        
    # Stub function
    def validate_and_setup_token():
        return None
        
    # Stub cleanup function
    async def cleanup_web_resources():
        pass
        
    # Stub initialization function
    async def initialize_web_agent_async():
        return False
    
    __all__ = [
        "root_agent", "web_agent", "validate_and_setup_token", 
        "get_github_tools", "cleanup_web_resources", 
        "initialize_web_agent_async", "LazyLoadingLlmAgent"
    ] 