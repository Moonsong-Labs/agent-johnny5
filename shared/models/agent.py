from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Agent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def process(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process the input data and return a response."""
        pass
    
    def __str__(self) -> str:
        return f"Agent({self.name})" 