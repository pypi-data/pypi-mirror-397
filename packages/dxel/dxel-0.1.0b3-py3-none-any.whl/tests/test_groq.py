"""
Tests for the Groq LLM class.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from groq import APIError
from dotenv import load_dotenv
import sys


# Project setup
project_name = 'DataGenie'
base_pth = os.getcwd().split(project_name)[0] + f'{project_name}/'
sys.path.append(base_pth)


from dxel.utils.llm.groq import GroqLLM


# Load environment variables from .env file
load_dotenv()


class TestGroqLLMInitialization:
    """Test cases for GroqLLM class initialization."""

    def test_init_with_valid_api_key(self):
        """Test successful initialization with a valid API key."""
        api_key = "test-api-key-12345"
        groq = GroqLLM(api_key=api_key)
        
        assert groq.model_name == "llama-3.3-70b-versatile"
        assert groq.default_max_tokens is None
        assert groq.temperature == 0.0
        assert groq._client is not None

    def test_init_with_custom_parameters(self):
        """Test initialization with custom parameters."""
        api_key = "test-api-key-12345"
        model = "llama-3.3-70b-versatile"
        max_tokens = 1000
        
        groq = GroqLLM(
            api_key=api_key,
            model=model,
            max_tokens=max_tokens
        )
        
        assert groq.model_name == model
        assert groq.default_max_tokens == max_tokens
        assert groq.temperature == 0.0

    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            GroqLLM(api_key="")

    def test_init_with_none_api_key_raises_error(self):
        """Test that initialization with None API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            GroqLLM(api_key=None)

    def test_init_with_non_string_api_key_raises_error(self):
        """Test that initialization with non-string API key raises ValueError."""
        with pytest.raises(ValueError, match="API key must be provided"):
            GroqLLM(api_key=12345)


class TestGroqLLMGenerate:
    """Test cases for GroqLLM generate method."""

    @patch('dxel.utils.llm.groq.Groq')
    def test_generate_with_user_prompt_only(self, mock_groq_class):
        """Test generate method with only user prompt."""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Test response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        groq = GroqLLM(api_key="test-key")
        response = groq.generate("What is 2 + 2?")
        
        assert response == "Test response"
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify call arguments
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == "llama-3.3-70b-versatile"
        assert call_args.kwargs['temperature'] == 0.0
        assert any(msg['role'] == 'user' and '2 + 2' in msg['content'] 
                   for msg in call_args.kwargs['messages'])

    @patch('dxel.utils.llm.groq.Groq')
    def test_generate_with_system_prompt(self, mock_groq_class):
        """Test generate method with system prompt."""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="4"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        system_prompt = "You are a mathematician. Answer only with numbers."
        groq = GroqLLM(api_key="test-key")
        response = groq.generate("What is 2 + 2?", system_prompt=system_prompt)
        
        assert response == "4"
        
        # Verify system prompt was included
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs['messages']
        assert any(msg['role'] == 'system' and msg['content'] == system_prompt 
                   for msg in messages)

    @patch('dxel.utils.llm.groq.Groq')
    def test_generate_with_max_tokens_override(self, mock_groq_class):
        """Test generate method with max_tokens override."""
        # Setup mock
        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Test
        groq = GroqLLM(api_key="test-key", max_tokens=500)
        response = groq.generate("Test", max_tokens=1000)
        
        # Verify the override max_tokens was used
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['max_tokens'] == 1000

    @patch('dxel.utils.llm.groq.Groq')
    def test_generate_with_empty_user_prompt_raises_error(self, mock_groq_class):
        """Test that empty user prompt raises ValueError."""
        groq = GroqLLM(api_key="test-key")
        
        with pytest.raises(ValueError, match="Prompt must be a non-empty string"):
            groq.generate("")


class TestGroqLLMIntegration:
    """Integration tests for GroqLLM (requires actual API key)."""

    def test_real_api_call(self):
        """Test a real API call to Groq (only runs if API key is available)."""
        api_key = os.getenv('GROQ_API_KEY')
        
        # Fail if API key is not present
        if not api_key:
            pytest.fail("GROQ_API_KEY environment variable is not set")
        
        # Using an available Groq model
        groq = GroqLLM(api_key=api_key, model="llama-3.3-70b-versatile")
        
        response = groq.generate("Say 'Hello, World!' and nothing else.")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Hello" in response or "hello" in response

    def test_real_api_call_with_system_instruction(self):
        """Test a real API call with system instruction."""
        api_key = os.getenv('GROQ_API_KEY')
        
        # Fail if API key is not present
        if not api_key:
            pytest.fail("GROQ_API_KEY environment variable is not set")
        
        system_prompt = "You are a mathematician. Answer only with numbers."
        groq = GroqLLM(api_key=api_key, model="llama-3.3-70b-versatile")
        
        response = groq.generate("What is 2 + 2?", system_prompt=system_prompt)
        
        assert isinstance(response, str)
        assert "4" in response

    def test_real_api_call_with_custom_model(self):
        """Test a real API call with custom model."""
        api_key = os.getenv('GROQ_API_KEY')
        
        # Fail if API key is not present
        if not api_key:
            pytest.fail("GROQ_API_KEY environment variable is not set")
        
        # Using a different Groq model (using a model that's actively supported)
        groq = GroqLLM(api_key=api_key, model="llama-3.3-70b-versatile")
        
        response = groq.generate("What is the capital of France?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Paris" in response or "paris" in response
