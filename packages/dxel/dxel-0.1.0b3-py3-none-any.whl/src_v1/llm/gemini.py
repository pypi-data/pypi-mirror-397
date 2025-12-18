from google import genai
from google.genai import types
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiClient:
    
    SUPPORTED_MODELS = [
        # Current (Gemini API)
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite", 
        # Still widely used & supported (keep for compatibility)
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        # Legacy support
        "gemini-pro"
    ]
    
    def _validate_model(self, model: str) -> None:
        """
        Validate if the specified model is supported.
        
        Args:
            model (str): The model name to validate.
            
        Raises:
            ValueError: If the model is not supported.
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model '{model}'. "
                f"Supported models: {', '.join(self.SUPPORTED_MODELS)}"
            )
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash", temp: float = 0):
        self.api_key = api_key
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        self.model_name = model_name
        self.temperature = temp
        
        # Validate model
        self._validate_model(self.model_name)
        
        # Initialize the modern Gemini client
        self.client = genai.Client(api_key=self.api_key)
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
    ):
        try:
            # Extract system message if present
            system_instruction = None
            user_messages = []
            
            for message in messages:
                role = message.get("role", "")
                content = message.get("content", "")
                
                if role == "system":
                    system_instruction = content
                elif role in ["user", "assistant"]:
                    user_messages.append(content)
            
            # Use the last user message as the main query
            user_query = user_messages[-1] if user_messages else ""
            
            # Generate content using the modern API
            response = self.client.models.generate_content(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=self.temperature
                ),
                contents=user_query
            )
            
            if response and response.text:
                return {
                    "status": "success",
                    "content": response.text,
                    "model": self.model_name,
                    "prompt_tokens": -1,  # Gemini doesn't provide this
                    "completion_tokens": -1,  # Gemini doesn't provide this
                    "total_tokens": -1,  # Gemini doesn't provide this
                    "finish_reason": "stop"  # Assuming successful completion
                }
            else:
                return {
                    "status": "error",
                    "message": "No response text generated"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
            }

    def simple_completion(
        self, 
        prompt: str, 
    ):
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages)
    
    def system_user_completion(
        self,
        system_message: str,
        user_message: str
    ):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        return self.chat_completion(messages)