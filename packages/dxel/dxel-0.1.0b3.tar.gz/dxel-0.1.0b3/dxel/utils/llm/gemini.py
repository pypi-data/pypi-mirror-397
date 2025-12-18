"""
LLM wrapper using the new 'google-genai' SDK structure.

- Uses genai.Client for API interaction.
- API Key must be explicitly passed.
- Temperature is fixed at 0.0.
- System prompt is optional.
"""

from typing import Optional
from google import genai
from google.genai import types # Imports GenerationConfig, etc.
from google.genai.errors import APIError

from .base_llm import BaseLLM





class Gemini(BaseLLM):
    """
    LLM class for interacting with Google Gemini language models via the Client API.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize the LLM instance and the Client object.

        Args:
            api_key: Required API key for Gemini.
            model: Model name to use (default: "gemini-2.5-flash").
            max_tokens: Default maximum tokens in response (default: None).

        Raises:
            ValueError: If API key is not provided.
        """
        # Initialize base class with fixed temperature
        super().__init__(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens,
            temperature=0.0
        )
        
        # Initialize Gemini-specific client
        self._client = genai.Client(api_key=api_key) 


    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the LLM using the Client service.

        Args:
            user_prompt: The user's input prompt.
            max_tokens: Override default max_tokens for this call.

        Returns:
            The generated response as a string.

        Raises:
            Exception: If the Gemini API call fails.
        """
        
        # --- 1. Validate user prompt ---
        self._validate_prompt(user_prompt)
        
        # --- 2. Configure Generation Settings ---
        current_max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        generation_config = types.GenerateContentConfig(
            temperature=self.temperature, 
            max_output_tokens=current_max_tokens,
            system_instruction= system_prompt if system_prompt else None
        )
        
        # --- 3. Construct Contents (User Prompt) ---
        contents = [
                    types.Content(
                        parts=[
                            types.Part(text=user_prompt)  
                        ]
                    )
                ]

        # --- 4. Generate Response ---
        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=generation_config,
                # Pass system instruction directly in the call if available
            )
            
            return response.text
        
        except APIError as e:
            raise Exception(f"Gemini API call failed: {e}") from e