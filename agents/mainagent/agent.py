from typing import Any, Dict, List, Optional, Type
import importlib
import logging

from shared.models.agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainAgent(Agent):
    """
    Main Orchestrator Agent - Responsible for coordinating work between other agents.
    """
    
    def __init__(self):
        super().__init__(name="orchestrator")
        self.agents = {}
        
    def register_agent(self, agent_name: str, agent_instance: Agent) -> None:
        """Register an agent with the orchestrator."""
        self.agents[agent_name] = agent_instance
        logger.info(f"Registered agent: {agent_name}")
        
    def load_agent(self, agent_name: str) -> Optional[Agent]:
        """Dynamically load an agent by name if it's not already registered."""
        if agent_name in self.agents:
            return self.agents[agent_name]
            
        try:
            # Try to import the agent module
            module = importlib.import_module(f"agents.{agent_name}.agent")
            
            # Just use the class name directly from the module
            if agent_name == "pullsage":
                class_name = "PullSageAgent"
            else:
                # Fallback capitalization logic for other agents
                agent_name_parts = agent_name.split('_')
                class_name = ''.join(part.capitalize() for part in agent_name_parts) + "Agent"
            
            logger.info(f"Looking for class: {class_name}")
            agent_class = getattr(module, class_name)
            
            # Instantiate the agent
            agent_instance = agent_class()
            # Register it for future use
            self.register_agent(agent_name, agent_instance)
            return agent_instance
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to load agent {agent_name}: {str(e)}")
            return None
        
    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process the input data, determine which agent to call,
        and return the processed result.
        """
        # Extract the target agent from input or use a default routing logic
        target_agent = input_data.get("agent", "pullsage")
        
        # Load the target agent
        agent = self.load_agent(target_agent)
        
        if not agent:
            return {
                "status": "error",
                "message": f"Agent '{target_agent}' not found or could not be loaded."
            }
        
        # Forward the request to the target agent
        logger.info(f"Forwarding request to {target_agent} agent")
        try:
            result = await agent.process(input_data, **kwargs)
            return {
                "status": "success",
                "agent": target_agent,
                "result": result
            }
        except Exception as e:
            logger.error(f"Error calling {target_agent} agent: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing request with {target_agent} agent: {str(e)}"
            } 