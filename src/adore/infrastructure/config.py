"""Configuration management for ADORE using Pydantic Settings.

This module handles all configuration including environment variables,
API keys, and runtime settings.
"""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AdoreSettings(BaseSettings):
    """ADORE application settings with environment variable support.

    All settings can be overridden via environment variables with ADORE_ prefix.
    Example: ADORE_OPENAI_API_KEY=your_key
    """

    # API Keys
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for LLM operations",
        validation_alias="OPENAI_API_KEY",
    )

    watsonx_api_key: Optional[str] = Field(
        default=None, description="IBM Watsonx API key (optional)", validation_alias="WATSONX_API_KEY"
    )

    watsonx_url: Optional[str] = Field(
        default=None, description="IBM Watsonx URL (optional)", validation_alias="WATSONX_URL"
    )

    watsonx_project_id: Optional[str] = Field(
        default=None, description="IBM Watsonx project ID (optional)", validation_alias="PROJECT_ID"
    )

    # LLM Settings
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM model to use")

    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")

    llm_max_tokens: int = Field(default=200, ge=1, le=4096, description="Maximum tokens for LLM")

    # Reasoning Settings
    reasoning_timeout: int = Field(
        default=30, ge=1, le=300, description="Timeout for reasoning operations (seconds)"
    )

    # Paths
    ontology_cache_dir: Path = Field(
        default=Path(".adore_cache"), description="Directory for ontology cache"
    )

    log_dir: Path = Field(default=Path("logs"), description="Directory for log files")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    log_json: bool = Field(default=False, description="Enable JSON logging")

    # Workflow Settings
    max_repair_iterations: int = Field(
        default=3, ge=1, le=10, description="Maximum repair iterations"
    )

    enable_human_in_loop: bool = Field(default=True, description="Enable human-in-the-loop stages")

    # Display Settings
    rich_console: bool = Field(default=True, description="Enable rich console output")

    show_banner: bool = Field(default=True, description="Show ADORE banner on startup")

    model_config = SettingsConfigDict(
        env_prefix="ADORE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **kwargs: object) -> None:
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        self.ontology_cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Optional[AdoreSettings] = None


def get_settings() -> AdoreSettings:
    """Get the global settings instance (singleton pattern).

    Returns:
        AdoreSettings: The application settings.

    Raises:
        ConfigurationError: If settings cannot be loaded.
    """
    global _settings
    if _settings is None:
        try:
            _settings = AdoreSettings()
        except Exception as e:
            from adore.core.exceptions import ConfigurationError

            raise ConfigurationError(f"Failed to load settings: {e}") from e
    return _settings


def reload_settings() -> AdoreSettings:
    """Reload settings from environment (useful for testing).

    Returns:
        AdoreSettings: The reloaded application settings.
    """
    global _settings
    _settings = None
    return get_settings()
