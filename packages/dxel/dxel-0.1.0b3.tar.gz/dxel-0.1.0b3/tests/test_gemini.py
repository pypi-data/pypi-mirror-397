"""
Tests for the Gemini LLM class.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv
import sys


# Project setup
project_name = 'DataGenie'
base_pth = os.getcwd().split(project_name)[0] + f'{project_name}/'
sys.path.append(base_pth)


from dxel.utils.llm.gemini import Gemini


# Load environment variables from .env file
load_dotenv()


class TestGeminiInitialization:
    """Test cases for Gemini class initialization."""

    def test_init_with_valid_api_key(self):
        """Test successful initialization with a valid API key."""
        api_key = "test-api-key-12345"
        gemini = Gemini(api_key=api_key)
        
        assert gemini.model_name == "gemini-2.5-flash"
        assert gemini.default_max_tokens is None
        assert gemini.temperature == 0.0
        assert gemini._client is not None

    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        api_key = "test-api-key-12345"
        model = "gemini-1.5-pro"
        max_tokens = 1000
        
        gemini = Gemini(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens
        )
        
        assert gemini.model_name == model
        assert gemini.default_max_tokens == max_tokens
        assert gemini.temperature == 0.0

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Gemini(api_key="")

    def test_init_with_none_api_key_raises_error(self):
        """Test that initialization with None API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Gemini(api_key=None)

    def test_init_with_non_string_api_key_raises_error(self):
        """Test that initialization with non-string API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            Gemini(api_key=12345)


class TestGeminiIntegration:
    """Integration tests for Gemini (requires actual API key)."""

    def test_real_api_call(self):
        """Test a real API call to Gemini (only runs if API key is available)."""
        api_key = os.getenv('GOOGLE_API_KEY')
        
        # Fail if API key is not present
        if not api_key:
            pytest.fail("GOOGLE_API_KEY environment variable is not set")
        
        gemini = Gemini(api_key=api_key)
        
        response = gemini.generate("Say 'Hello, World!' and nothing else.")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Hello" in response or "hello" in response

    def test_real_api_call_with_system_instruction(self):
        """Test a real API call with system instruction."""
        api_key = os.getenv('GOOGLE_API_KEY')
        
        # Fail if API key is not present
        if not api_key:
            pytest.fail("GOOGLE_API_KEY environment variable is not set")
        
        system_prompt = "You are a mathematician. Answer only with numbers."
        gemini = Gemini(api_key=api_key)
        
        response = gemini.generate("What is 2 + 2?", system_prompt=system_prompt)
        
        assert isinstance(response, str)
        assert "4" in response
