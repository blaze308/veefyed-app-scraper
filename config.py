"""
Configuration settings for Auto-Scraper AI Tool
"""

import os
from typing import List, Optional
from pathlib import Path


class Config:
    """Application configuration"""
    
    # Application
    APP_NAME = "Auto-Scraper AI Tool"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    SCRIPTS_RAW_DIR = DATA_DIR / "scripts_raw"
    OUTPUTS_DIR = DATA_DIR / "outputs"
    LOGS_DIR = DATA_DIR / "logs"
    MODULES_DIR = BASE_DIR / "modules"
    
    # Scraping
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RATE_LIMIT = int(os.getenv("RATE_LIMIT", "10"))  # requests per minute
    
    # User Agent
    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Job Management
    JOB_RETENTION_HOURS = int(os.getenv("JOB_RETENTION_HOURS", "24"))
    MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "5"))
    
    # Output
    OUTPUT_FORMATS = ["json", "csv"]
    DEFAULT_OUTPUT_FORMAT = "json"
    MAX_OUTPUT_FILE_SIZE_MB = 10
    
    # Security
    ALLOWED_DOMAINS: Optional[List[str]] = None  # None = all domains allowed
    BLOCKED_DOMAINS = [
        "facebook.com",
        "twitter.com",
        "instagram.com",
        "linkedin.com"
    ]
    
    # AI Pattern Detection
    AI_ENABLED = os.getenv("AI_ENABLED", "True").lower() == "true"
    AI_CONFIDENCE_THRESHOLD = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.5"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [
            cls.DATA_DIR,
            cls.SCRIPTS_RAW_DIR,
            cls.OUTPUTS_DIR,
            cls.LOGS_DIR
        ]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_domain_allowed(cls, url: str) -> bool:
        """Check if domain is allowed for scraping"""
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc.lower()
        
        # Check blocked domains
        if any(blocked in domain for blocked in cls.BLOCKED_DOMAINS):
            return False
        
        # Check allowed domains (if specified)
        if cls.ALLOWED_DOMAINS:
            return any(allowed in domain for allowed in cls.ALLOWED_DOMAINS)
        
        return True


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    
    # Stricter limits for production
    REQUEST_TIMEOUT = 20
    RATE_LIMIT = 5
    MAX_CONCURRENT_JOBS = 3


# Select configuration based on environment
ENV = os.getenv("ENVIRONMENT", "development").lower()

if ENV == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()

# Ensure directories exist
config.ensure_directories()

