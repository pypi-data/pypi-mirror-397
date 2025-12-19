"""Configuration management for Anzo MCP Server."""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
# Try to load from script directory first, then current directory
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_dir = os.path.dirname(_script_dir) if os.path.basename(_script_dir) == 'anzo_mcp' else _script_dir
env_loaded = load_dotenv(os.path.join(_project_dir, '.env')) or load_dotenv()


@dataclass
class AnzoConfig:
    """Configuration for Anzo API client."""
    
    http_base: str
    username: str
    password: str
    graphmart_iri: str = ""
    port: int = 443
    request_timeout: float = 30.0
    max_retries: int = 3
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'AnzoConfig':
        """
        Load configuration from environment variables.
        
        Raises:
            ValueError: If required environment variables are not set.
        """
        username = os.getenv("ANZO_USERNAME")
        password = os.getenv("ANZO_PASSWORD")
        http_base = os.getenv("ANZO_HTTP_BASE")
        
        if not username:
            raise ValueError("ANZO_USERNAME environment variable must be set")
        if not password:
            raise ValueError("ANZO_PASSWORD environment variable must be set")
        if not http_base:
            raise ValueError("ANZO_HTTP_BASE environment variable must be set")
        
        return cls(
            http_base=http_base,
            username=username,
            password=password,
            graphmart_iri=os.getenv("ANZO_GRAPHMART_IRI", ""),
            port=int(os.getenv("ANZO_PORT", "443")),
            request_timeout=float(os.getenv("REQUEST_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not self.http_base.startswith(("http://", "https://")):
            raise ValueError(f"Invalid ANZO_HTTP_BASE: {self.http_base}")
        
        if self.port < 1 or self.port > 65535:
            raise ValueError(f"Invalid port: {self.port}")
        
        if self.request_timeout <= 0:
            raise ValueError(f"Invalid request_timeout: {self.request_timeout}")
        
        if self.max_retries < 0:
            raise ValueError(f"Invalid max_retries: {self.max_retries}")


# Global config instance
import threading
_config: Optional[AnzoConfig] = None
_config_lock = threading.Lock()


def get_config() -> AnzoConfig:
    """Get or create the global configuration instance (thread-safe)."""
    global _config
    if _config is None:
        with _config_lock:
            # Double-check locking pattern
            if _config is None:
                _config = AnzoConfig.from_env()
                _config.validate()
    return _config
