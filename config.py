import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Gmail Settings
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    
    # MongoDB Settings
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'bulk_emailer')
    
    # Application Settings
    APP_TITLE = os.getenv('APP_TITLE', 'Bulk Email Sender')
    RATE_LIMIT_EMAILS_PER_MINUTE = int(os.getenv('RATE_LIMIT_EMAILS_PER_MINUTE', 30))
    
    # Email Settings
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required = [
            ('GMAIL_EMAIL', cls.GMAIL_EMAIL),
            ('GMAIL_APP_PASSWORD', cls.GMAIL_APP_PASSWORD),
            ('MONGODB_URI', cls.MONGODB_URI)
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
