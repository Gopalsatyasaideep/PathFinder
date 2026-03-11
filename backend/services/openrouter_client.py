"""
OpenRouter API Client

Provides a unified interface to call OpenRouter's free API models
for text generation in chatbot and learning path features.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests


class OpenRouterClient:
    """
    Client for OpenRouter API (OpenAI-compatible endpoint).
    Supports free tier models for chatbot and learning path generation.
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    
    # Free models available on OpenRouter
    FREE_MODELS = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "google/gemma-2-2b-it:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "mistralai/mistral-7b-instruct:free",
    ]
    
    DEFAULT_MODEL = "meta-llama/llama-3.2-3b-instruct:free"
    
    # ============================================
    # SET YOUR OPENROUTER API KEY HERE:
    # ============================================
    # Get your free API key from: https://openrouter.ai/keys
    # Example: DEFAULT_API_KEY = "sk-or-v1-abc123..."
    DEFAULT_API_KEY = "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"  # <-- YOUR API KEY IS SET HERE
    # ============================================

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. Priority: 1) passed parameter, 2) DEFAULT_API_KEY, 3) OPENROUTER_API_KEY env var.
            model: Model to use. If None, uses DEFAULT_MODEL.
        """
        # Priority: parameter > class default > environment variable
        self.api_key = api_key or self.DEFAULT_API_KEY or os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key is required. Set it in code (OpenRouterClient.DEFAULT_API_KEY), "
                "pass as parameter, or set OPENROUTER_API_KEY environment variable. "
                "Get your key from https://openrouter.ai/keys"
            )
        self.model = model or self.DEFAULT_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/pathfinder-ai",  # Optional: for analytics
        }

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
    ) -> str:
        """
        Generate text using OpenRouter API.
        
        Args:
            prompt: The user prompt/question
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-2.0)
            system_message: Optional system message for context
            
        Returns:
            Generated text response
            
        Raises:
            requests.RequestException: If API call fails
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            response = requests.post(
                self.BASE_URL,
                headers=self.headers,
                json=payload,
                timeout=30,  # 30 second timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract the generated text
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0].get("message", {}).get("content", "")
                return content.strip()
            else:
                raise ValueError(f"Unexpected API response format: {data}")
                
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg)
                except:
                    pass
            raise Exception(f"OpenRouter API error: {error_msg}")

    def generate_with_fallback(
        self,
        prompt: str,
        *,
        max_tokens: int = 500,
        temperature: float = 0.7,
        system_message: Optional[str] = None,
        fallback_message: str = "I apologize, but I'm having trouble generating a response right now.",
    ) -> str:
        """
        Generate text with graceful fallback on errors.
        
        Returns fallback_message if API call fails instead of raising exception.
        """
        try:
            return self.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                system_message=system_message,
            )
        except Exception as e:
            print(f"OpenRouter API error (using fallback): {e}")
            return fallback_message


def get_openrouter_client(api_key: Optional[str] = None) -> Optional[OpenRouterClient]:
    """
    Factory function to create OpenRouter client if API key is available.
    Returns None if API key is not set (allows graceful degradation).
    
    Args:
        api_key: Optional API key. If not provided, uses DEFAULT_API_KEY or env var.
    """
    # Try to create client with provided key, class default, or env var
    try:
        return OpenRouterClient(api_key=api_key)
    except ValueError:
        # No API key available
        return None
    except Exception as e:
        print(f"Warning: Could not initialize OpenRouter client: {e}")
        return None

