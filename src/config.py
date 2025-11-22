"""Configuration management for the OCR service."""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Model settings
    model_name: str = "protonx-models/protonx-legal-tc"
    model_cache_dir: str = "./model_cache"
    device: str = "cpu"
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 1
    
    # Logging
    log_level: str = "INFO"
    
    # OCR settings
    ocr_engine: str = "easyocr"  # 'easyocr' or 'tesseract'
    ocr_languages: str = "vi,en"  # Comma-separated list of language codes
    max_upload_size: int = 10 * 1024 * 1024  # 10MB default
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
