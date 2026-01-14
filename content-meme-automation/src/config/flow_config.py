"""Flow configuration management with override support."""
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv


class FlowConfig:
    """Manages configuration for flows with override support."""
    
    def __init__(
        self,
        base_config: Optional[Dict[str, Any]] = None,
        override_string: Optional[str] = None
    ):
        """
        Initialize FlowConfig.
        
        Args:
            base_config: Base configuration dictionary
            override_string: Override string in format "key1=value1,key2=value2"
        """
        # Load environment variables
        load_dotenv()
        
        # Start with base config or defaults
        self.config = base_config or self._load_default_config()
        
        # Apply overrides if provided
        if override_string:
            self._apply_overrides(override_string)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration from environment variables.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "business_documents_path": os.getenv("BUSINESS_DOCS_PATH", "./business_documents"),
            "brand_identity_path": os.getenv("BRAND_IDENTITY_PATH", "./brand_identity"),
            "meme_templates_path": os.getenv("MEME_TEMPLATES_PATH", "./rekt_meme_templates"),
            "output_path": os.getenv("OUTPUT_PATH", "./output"),
            "platforms": self._parse_platforms(os.getenv("PLATFORMS", "twitter,instagram,linkedin")),
            "skip_animation": os.getenv("SKIP_ANIMATION", "false").lower() == "true",
            "animation_style": os.getenv("ANIMATION_STYLE", "auto"),
            "force_refresh_context": False,
            "force_refresh_trends": False,
        }
    
    def _parse_platforms(self, platforms_str: str) -> list[str]:
        """
        Parse platforms from comma-separated string.
        
        Args:
            platforms_str: Comma-separated platform names
            
        Returns:
            List of platform names
        """
        return [p.strip() for p in platforms_str.split(",") if p.strip()]
    
    def _apply_overrides(self, override_string: str) -> None:
        """
        Apply overrides from a string.
        
        Format: "key1=value1,key2=value2"
        
        Args:
            override_string: Override string
        """
        if not override_string:
            return
        
        # Split by comma
        pairs = override_string.split(",")
        
        for pair in pairs:
            if "=" not in pair:
                continue
            
            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()
            
            # Handle special cases
            if key == "platforms":
                self.config[key] = self._parse_platforms(value)
            elif key in ["skip_animation", "force_refresh_context", "force_refresh_trends"]:
                self.config[key] = value.lower() in ["true", "yes", "1"]
            else:
                # Try to convert to appropriate type
                self.config[key] = self._parse_value(value)
    
    def _parse_value(self, value: str) -> Any:
        """
        Parse a value string to appropriate type.
        
        Args:
            value: Value string
            
        Returns:
            Parsed value
        """
        # Try boolean
        if value.lower() in ["true", "false"]:
            return value.lower() == "true"
        
        # Try int
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        # Check required paths exist
        required_paths = {
            "business_documents_path": "Business documents directory",
            "brand_identity_path": "Brand identity directory",
            "meme_templates_path": "Meme templates directory",
        }
        
        for path_key, description in required_paths.items():
            path = self.config.get(path_key)
            if not path:
                errors.append(f"{description} path not configured")
            elif not Path(path).exists():
                errors.append(f"{description} does not exist: {path}")
        
        # Check API keys
        if not os.getenv("GOOGLE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            errors.append("No LLM API keys found (GOOGLE_API_KEY or OPENAI_API_KEY required)")
        
        # Validate platforms
        valid_platforms = ["twitter", "instagram", "linkedin"]
        platforms = self.config.get("platforms", [])
        for platform in platforms:
            if platform not in valid_platforms:
                errors.append(f"Invalid platform: {platform}. Must be one of {valid_platforms}")
        
        return (len(errors) == 0, errors)
