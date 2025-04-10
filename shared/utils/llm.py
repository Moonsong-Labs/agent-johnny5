"""
LLM utility functions for working with Google's Generative AI.
"""
import os
from typing import Dict, List, Optional, Union

import google.generativeai as genai
from dotenv import load_dotenv
from langchain.schema import AIMessage, HumanMessage, SystemMessage

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

DEFAULT_MODEL = os.getenv("MODEL_NAME", "gemini-1.5-pro")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))


class LLMClient:
    """Client for interacting with Google's Generative AI models."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        max_tokens: int = MAX_TOKENS,
        temperature: float = 0.7,
    ):
        """Initialize the LLM client."""
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 0,
        }

    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """Complete a prompt with the LLM."""
        if temperature is not None:
            generation_config = self.generation_config.copy()
            generation_config["temperature"] = temperature
        else:
            generation_config = self.generation_config

        model = genai.GenerativeModel(
            model_name=self.model,
            generation_config=generation_config,
        )

        if system_message:
            chat = model.start_chat(system_instruction=system_message)
            response = await chat.send_message_async(prompt)
        else:
            response = await model.generate_content_async(prompt)

        return response.text

    async def chat(
        self,
        messages: List[Union[SystemMessage, HumanMessage, AIMessage]],
        temperature: Optional[float] = None,
    ) -> str:
        """Have a chat conversation with the LLM."""
        if temperature is not None:
            generation_config = self.generation_config.copy()
            generation_config["temperature"] = temperature
        else:
            generation_config = self.generation_config

        # Extract system message if present
        system_content = None
        chat_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                system_content = message.content
            elif isinstance(message, HumanMessage):
                chat_messages.append({"role": "user", "parts": [message.content]})
            elif isinstance(message, AIMessage):
                chat_messages.append({"role": "model", "parts": [message.content]})

        model = genai.GenerativeModel(
            model_name=self.model,
            generation_config=generation_config,
        )
        
        if system_content:
            chat = model.start_chat(system_instruction=system_content)
            for msg in chat_messages:
                if msg["role"] == "user":
                    if len(chat_messages) == 1 or msg == chat_messages[-1]:
                        response = await chat.send_message_async(msg["parts"][0])
                    else:
                        chat.send_message(msg["parts"][0])
        else:
            history = []
            for msg in chat_messages[:-1]:
                history.append(msg)
            
            chat = model.start_chat(history=history)
            response = await chat.send_message_async(chat_messages[-1]["parts"][0])
            
        return response.text

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts."""
        result = []
        for text in texts:
            embedding = await genai.embed_content_async(
                model="embedding-001",
                content=text,
                task_type="semantic_similarity",
            )
            result.append(embedding["embedding"])
        return result


# Create a default LLM client instance
default_client = LLMClient()


async def complete_prompt(
    prompt: str,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
) -> str:
    """Convenience function to complete a prompt using the default client."""
    return await default_client.complete(prompt, system_message, temperature)


async def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Convenience function to get embeddings using the default client."""
    return await default_client.get_embeddings(texts) 