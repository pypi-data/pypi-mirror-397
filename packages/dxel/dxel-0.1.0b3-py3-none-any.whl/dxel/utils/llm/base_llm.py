"""
Base LLM class that defines the interface for all LLM implementations.

This abstract base class ensures that all LLM implementations follow the same structure
and provide consistent methods for generating content.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseLLM(ABC):
    """
    Abstract base class for LLM implementations.
    
    All LLM classes should inherit from this class and implement the required methods.
    This ensures a consistent interface across different LLM providers.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.0,
    ):
        """
        Initialize the base LLM instance.

        Args:
            api_key: Required API key for the LLM service.
            model: Model name to use.
            max_tokens: Default maximum tokens in response (default: None).
            temperature: Temperature for response generation (default: 0.0).

        Raises:
            ValueError: If API key is not provided or invalid.
        """
        # Validate API key
        if not api_key or not isinstance(api_key, str):
            raise ValueError(
                "API key must be provided as a non-empty string."
            )
        
        # Store common attributes
        self.model_name = model
        self.default_max_tokens = max_tokens
        self.temperature = temperature

    @abstractmethod
    def generate(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate a response from the LLM.

        Args:
            user_prompt: The user's input prompt.
            system_prompt: Optional system instruction for the model's behavior.
            max_tokens: Override default max_tokens for this call.

        Returns:
            The generated response as a string.

        Raises:
            Exception: If the LLM API call fails.
        """
        pass

    def _validate_prompt(self, prompt: str) -> None:
        """
        Validate that the prompt is a non-empty string.

        Args:
            prompt: The prompt to validate.

        Raises:
            ValueError: If prompt is empty or not a string.
        """
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Prompt must be a non-empty string.")

    def __repr__(self) -> str:
        """Return a string representation of the LLM instance."""
        return (
            f"{self.__class__.__name__}("
            f"model={self.model_name}, "
            f"temperature={self.temperature}, "
            f"max_tokens={self.default_max_tokens})"
        )
