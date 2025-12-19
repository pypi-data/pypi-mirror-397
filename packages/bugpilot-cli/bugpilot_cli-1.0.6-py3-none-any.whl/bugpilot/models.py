"""
AI Model Integration Layer
Supports: Gemini, OpenAI, Groq, Ollama, Anthropic
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from openai import OpenAI
from groq import Groq
import anthropic
import httpx


class BaseModel(ABC):
    """Base class for all AI models"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = None, **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response from the model"""
        pass


class GeminiModel(BaseModel):
    """Google Gemini model integration"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat = None
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Gemini"""
        try:
            if context and len(context) > 0:
                # Use chat mode for context
                if not self.chat:
                    self.chat = self.model.start_chat(history=[])
                response = self.chat.send_message(prompt)
            else:
                response = self.model.generate_content(prompt)
            
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"


class OpenAIModel(BaseModel):
    """OpenAI model integration"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.client = OpenAI(api_key=api_key)
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using OpenAI"""
        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.kwargs.get('temperature', 0.7),
                max_tokens=self.kwargs.get('max_tokens', 4096)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"


class GroqModel(BaseModel):
    """Groq model integration"""
    
    def __init__(self, api_key: str, model_name: str = "mixtral-8x7b-32768", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.client = Groq(api_key=api_key)
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Groq"""
        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.kwargs.get('temperature', 0.7),
                max_tokens=self.kwargs.get('max_tokens', 4096)
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"


class OllamaModel(BaseModel):
    """Ollama local model integration"""
    
    def __init__(self, model_name: str = "llama2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(None, model_name, **kwargs)
        self.base_url = base_url
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Ollama"""
        try:
            url = f"{self.base_url}/api/generate"
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            
            response = httpx.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            
            return response.json().get("response", "No response")
        except Exception as e:
            return f"Error generating response: {str(e)}"


class AnthropicModel(BaseModel):
    """Anthropic Claude model integration"""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-opus-20240229", **kwargs):
        super().__init__(api_key, model_name, **kwargs)
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate(self, prompt: str, context: List[Dict[str, str]] = None) -> str:
        """Generate response using Anthropic"""
        try:
            messages = []
            if context:
                messages.extend(context)
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=self.kwargs.get('max_tokens', 4096),
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            return f"Error generating response: {str(e)}"


class ModelFactory:
    """Factory for creating AI model instances"""
    
    @staticmethod
    def create_model(provider: str, api_key: Optional[str] = None, model_name: str = None, **kwargs) -> BaseModel:
        """Create and return appropriate model instance"""
        
        models = {
            "gemini": (GeminiModel, "gemini-2.0-flash-exp"),
            "openai": (OpenAIModel, "gpt-4o"),
            "groq": (GroqModel, "llama-3.3-70b-versatile"),
            "ollama": (OllamaModel, "llama3.2"),
            "anthropic": (AnthropicModel, "claude-3-5-sonnet-20241022"),
        }
        
        if provider not in models:
            raise ValueError(f"Unsupported provider: {provider}")
        
        model_class, default_model = models[provider]
        model_name = model_name or default_model
        
        if provider == "ollama":
            return model_class(model_name=model_name, **kwargs)
        else:
            if not api_key:
                raise ValueError(f"API key required for {provider}")
            return model_class(api_key=api_key, model_name=model_name, **kwargs)
