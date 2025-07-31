"""
Production configuration for Max Electric Payment Demo
"""
import os
from typing import Dict, Any

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DATABASE_PATH = os.environ.get('DATABASE_PATH', '/app/data/customer.db')
    DATABASE_BACKUP_INTERVAL = 3600  # 1 hour
    
    # SignalWire Configuration
    SIGNALWIRE_SPACE = os.environ.get('SIGNALWIRE_SPACE')
    SIGNALWIRE_PROJECT_ID = os.environ.get('SW_PROJECT_ID')
    SIGNALWIRE_REST_API_TOKEN = os.environ.get('SW_REST_API_TOKEN')
    SIGNALWIRE_CALL_TOKEN = os.environ.get('SIGNALWIRE_CALL_TOKEN')
    SIGNALWIRE_CALL_DESTINATION = os.environ.get('SIGNALWIRE_CALL_DESTINATION')
    
    # Ngrok Configuration
    NGROK_TOKEN = os.environ.get('NGROK_TOKEN')
    NGROK_REGION = os.environ.get('NGROK_REGION', 'us')
    
    # Security Configuration
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = '/app/logs/app.log'
    
    # Agent Configuration
    AGENT_HOST = "0.0.0.0"
    AGENT_PORT = 3000
    AGENT_TIMEOUT = 30
    
    # Payment Configuration
    PAYMENT_TIMEOUT = 300  # 5 minutes
    MAX_PAYMENT_AMOUNT = 10000.00
    MIN_PAYMENT_AMOUNT = 1.00
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate required configuration variables"""
        required_vars = [
            'SIGNALWIRE_SPACE',
            'SIGNALWIRE_PROJECT_ID', 
            'SIGNALWIRE_REST_API_TOKEN',
            'NGROK_TOKEN'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return {
            "status": "valid",
            "required_vars": required_vars,
            "missing_vars": missing_vars
        }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Additional production-specific settings
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'
    SECRET_KEY = 'test-secret-key'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 