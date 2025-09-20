"""
Configuration settings for Ayurvedic Diet Management API
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Ayurvedic Diet Management API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Firebase
    FIREBASE_CRED_PATH: str = "secrets/firebase-adminsdk.json"
    GOOGLE_CLOUD_PROJECT: str = "ayurvedic-diet-app"
    FIREBASE_DATABASE_URL: Optional[str] = None
    
    # ML Models
    ML_MODELS_BUCKET: str = "gs://ayur-ml-models"
    MODEL_CACHE_SIZE: int = 256
    PREDICTION_CACHE_TTL: int = 900  # 15 minutes
    
    # Cloud Tasks
    CLOUD_TASKS_QUEUE: str = "projects/ayurvedic-diet-app/locations/us-central1/queues/ayur-tasks"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Database
    FIRESTORE_COLLECTION_PREFIX: str = "ayur_diet"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
