import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class ModelConfig(BaseModel):
    """Configuration for AI models"""
    model_config = ConfigDict(protected_namespaces=())  # Fix pydantic warning
    
    provider: str = Field(default="gemini", description="AI provider: gemini, openai, groq, ollama, anthropic")
    model_name: str = Field(default="gemini-2.0-flash-exp", description="Model name")
    
    # Store multiple API keys for easy switching
    api_keys: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {
            "gemini": None,
            "openai": None,
            "groq": None,
            "anthropic": None
        },
        description="API keys for each provider"
    )
    
    # Deprecated - keeping for backward compatibility
    api_key: Optional[str] = Field(default=None, description="Legacy API key field")
    
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=8192, ge=1, le=100000)
    base_url: Optional[str] = Field(default=None, description="Custom base URL for Ollama or custom endpoints")

class BugPilotConfig(BaseModel):
    """Main configuration for BugPilot CLI"""
    model: ModelConfig = Field(default_factory=ModelConfig)
    mode: str = Field(default="normal", description="Mode: normal or hacker")
    context_history_size: int = Field(default=10, ge=1, le=100)
    auto_execute_commands: bool = Field(default=False, description="Auto-execute commands in hacker mode")
    mcp_enabled: bool = Field(default=True, description="Enable MCP (Model Context Protocol)")
    terminal_theme: str = Field(default="ocean", description="Terminal theme: ocean, sunset, neon, forest, midnight")
    developer: str = Field(default="LAKSHMIKANTHAN K (letchupkt)", description="Developer information")
    working_directory: str = Field(default=".", description="Current working directory for file access")
    auto_update_check: bool = Field(default=True, description="Check for updates on startup")

class ConfigManager:
    """Manages BugPilot configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".bugpilot"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self.config = self.load_config()
    
    def load_config(self) -> BugPilotConfig:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    return BugPilotConfig(**data)
            except Exception as e:
                print(f"Error loading config: {e}")
                return BugPilotConfig()
        else:
            return BugPilotConfig()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.model_dump(), f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def update_model(self, provider: str, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Update model configuration"""
        self.config.model.provider = provider
        self.config.model.model_name = model_name
        if api_key:
            # Store in the api_keys dict for the specific provider
            if not self.config.model.api_keys:
                self.config.model.api_keys = {}
            self.config.model.api_keys[provider] = api_key
        if base_url:
            self.config.model.base_url = base_url
        self.save_config()
    
    def update_mode(self, mode: str):
        """Update operating mode"""
        if mode in ["normal", "hacker"]:
            self.config.mode = mode
            self.save_config()
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key from config or environment"""
        # First check the new api_keys dict
        if self.config.model.api_keys and provider in self.config.model.api_keys:
            if self.config.model.api_keys[provider]:
                return self.config.model.api_keys[provider]
        
        # Backward compatibility - check legacy api_key field
        if self.config.model.api_key:
            return self.config.model.api_key
        
        # Fallback to environment variables
        env_keys = {
            "gemini": "GEMINI_API_KEY",
            "openai": "OPENAI_API_KEY",
            "groq": "GROQ_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
        }
        
        env_var = env_keys.get(provider)
        if env_var:
            return os.getenv(env_var)
        
        return None
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a specific provider"""
        if not self.config.model.api_keys:
            self.config.model.api_keys = {}
        self.config.model.api_keys[provider] = api_key
        self.save_config()
