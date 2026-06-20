"""Configuration management for the Meme API."""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_reload: bool = False
    
    # CORS Settings - parse as comma-separated string
    cors_origins: str = "http://localhost:3000"
    
    # File Upload Settings
    max_file_size_mb: int = 10
    allowed_image_formats: str = "image/jpeg,image/png,image/webp"
    
    # LLM API Keys (configure one or more — users pick per request)
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    default_llm: Optional[str] = None
    default_vision_llm: Optional[str] = None
    
    # Paths
    brand_config_path: Optional[str] = os.getenv("BRAND_CONFIG_PATH")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # x402 payment settings (disabled by default for local development)
    x402_enabled: bool = False
    x402_price: str = "$0.05"
    x402_evm_pay_to: Optional[str] = None
    x402_svm_pay_to: Optional[str] = None
    x402_evm_network: str = "eip155:84532"  # Base Sepolia testnet
    x402_svm_network: str = "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1"  # Solana devnet
    x402_facilitator_url: str = "https://x402.org/facilitator"

    # Admin bypass: set a long random secret; send via X-Admin-Key or Authorization: Bearer
    admin_api_key: Optional[str] = None

    # Computed properties
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_image_formats_list(self) -> list[str]:
        """Get allowed image formats as a list."""
        return [fmt.strip() for fmt in self.allowed_image_formats.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def has_llm_key(self) -> bool:
        """Check if at least one LLM provider API key is configured."""
        return bool(
            self.google_api_key
            or self.openai_api_key
            or self.groq_api_key
            or self.deepseek_api_key
            or self.openrouter_api_key
        )


# Global settings instance
settings = Settings()


# Minimal default business context when not provided
MINIMAL_BUSINESS_CONTEXT = {
    "brand_identity": {
        "core_narrative": "Web3 and crypto content creation",
        "brand_pillars": ["Innovation", "Community", "Transparency"],
        "brand_personality_traits": ["Bold", "Edgy", "Humorous"]
    },
    "communication_style": {
        "tone_descriptors": ["casual", "edgy", "witty"],
        "humor_style": "relatable internet humor with crypto context"
    },
    "audience_intelligence": {
        "primary_audience": "Crypto enthusiasts and Web3 builders",
        "expertise_level": "intermediate to advanced"
    }
}


# Minimal default platforms if not specified
DEFAULT_PLATFORMS = ["twitter"]
