# backend/config.py

import os

class Config:
    """Base configuration."""
    DEBUG = os.getenv("DEBUG", True)  # Set to False in production
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = os.getenv("PORT", 5000)
    # Add any other configuration variables as needed

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
