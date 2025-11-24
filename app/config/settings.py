"""
Configuration Settings Module

Centralized configuration management for the application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application configuration settings."""
    
    # Flask Configuration
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    FLASK_HOST: str = '0.0.0.0'
    FLASK_PORT: int = 8000
    
    # Service Configuration
    SERVICE_NAME: str = 'paprika-showcase'
    
    # Gemini Model Configuration
    GEMINI_TEXT_MODEL: str = os.getenv('GEMINI_TEXT_MODEL', 'gemini-2.0-flash')
    GEMINI_IMAGE_MODEL: str = os.getenv('GEMINI_IMAGE_MODEL', 'gemini-2.0-flash')
    
    # Agent Configuration
    STORYBOARD_APP_NAME: str = "paprika_storyboard"
    STORYBOARD_AGENT_NAME: str = "storyboard_agent"
    STORYBOARD_AGENT_DESCRIPTION: str = (
        "Analyzes video descriptions and segments them into distinct frames for storyboarding."
    )
    IMAGE_GENERATION_APP_NAME: str = "paprika_image_generation"
    IMAGE_GENERATION_AGENT_NAME: str = "image_generation_agent"
    IMAGE_GENERATION_AGENT_DESCRIPTION: str = (
        "Generates sequential images for storyboard frames using image generation models."
    )
    
    # Session Configuration
    DEFAULT_USER_ID: str = "api_user"
    
    # Output Configuration
    OUTPUT_DIR: str = "output"


settings = Settings()
