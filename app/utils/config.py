"""
Configuration management for Delivery Distance Tracker API.

This module provides centralized configuration loading and validation
using environment variables with sensible defaults.
"""

import os
from typing import List


class Config:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.cors_origins = self._get_cors_origins()
        self.nominatim_base_url = self._get_nominatim_base_url()
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

    def _get_cors_origins(self) -> List[str]:
        """
        Get CORS allowed origins from environment variable.
        
        Returns:
            List[str]: List of allowed origins for CORS
        """
        cors_origins_env = os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:3000,http://127.0.0.1:3000"
        )
        return [origin.strip() for origin in cors_origins_env.split(",")]

    def _get_nominatim_base_url(self) -> str:
        """
        Get Nominatim base URL from environment variable.
        
        Returns:
            str: Base URL for Nominatim API
        """
        return os.getenv(
            "NOMINATIM_BASE_URL", 
            "https://nominatim.openstreetmap.org"
        )

    @property
    def nominatim_search_url(self) -> str:
        """
        Get the full Nominatim search endpoint URL.
        
        Returns:
            str: Full URL for Nominatim search endpoint
        """
        return f"{self.nominatim_base_url}/search"


# Global configuration instance
config = Config()