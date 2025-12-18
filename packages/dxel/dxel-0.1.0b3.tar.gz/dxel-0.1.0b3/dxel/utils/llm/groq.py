"""
LLM wrapper using the Groq API SDK.

- Uses Groq client for API interaction.
- API Key must be explicitly passed.
- Temperature is fixed at 0.0.
- System prompt is optional.
"""

from typing import Optional
from groq import Groq
from groq import APIError

from .base_llm import BaseLLM


class GroqLLM(BaseLLM):
    """
    LLM class for interacting with Groq language models via the Groq API.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize the LLM instance and the Groq client.

        Args:
            api_key: Required API key for Groq.
            model: Model name to use (default: "mixtral-8x7b-32768").
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
        
        # Initialize Groq-specific client
        self._client = Groq(api_key=api_key)

    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the LLM using the Groq API.

        Args:
            user_prompt: The user's input prompt.
            system_prompt: Optional system instruction for the model's behavior.
            max_tokens: Override default max_tokens for this call.

        Returns:
            The generated response as a string.

        Raises:
            Exception: If the Groq API call fails.
        """
        
        # --- 1. Validate user prompt ---
        self._validate_prompt(user_prompt)
        
        # --- 2. Configure Generation Settings ---
        current_max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        # --- 3. Construct Messages ---
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        # --- 4. Generate Response ---
        try:
            response = self._client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=current_max_tokens,
            )
            
            return response.choices[0].message.content
        
        except APIError as e:
            raise Exception(f"Groq API call failed: {e}") from e
