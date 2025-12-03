import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()


class Config:
    """
    Application configuration - supports both local development and Streamlit Cloud.
    
    Priority order:
    1. Streamlit secrets (st.secrets) - Used on Streamlit Cloud
    2. Environment variables (.env file) - Used for local development
    """
    
    @staticmethod
    def _get_config_value(key, default=None):
        """
        Get configuration value from Streamlit secrets or environment variables.
        
        Args:
            key: Configuration key name
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        # First, try to get from Streamlit secrets
        if key in st.secrets:
            return st.secrets[key]
        
        # Fall back to environment variables
        return os.getenv(key, default)
    
    # Gmail Settings
    @property
    def GMAIL_EMAIL(self):
        return self._get_config_value('GMAIL_EMAIL')
    
    @property
    def GMAIL_APP_PASSWORD(self):
        return self._get_config_value('GMAIL_APP_PASSWORD')
    
    # MongoDB Settings
    @property
    def MONGODB_URI(self):
        return self._get_config_value('MONGODB_URI')
    
    @property
    def MONGODB_DB_NAME(self):
        return self._get_config_value('MONGODB_DB_NAME', 'bulk_emailer')
    
    # Application Settings
    @property
    def APP_TITLE(self):
        return self._get_config_value('APP_TITLE', 'Bulk Email Sender')
    
    @property
    def RATE_LIMIT_EMAILS_PER_MINUTE(self):
        value = self._get_config_value('RATE_LIMIT_EMAILS_PER_MINUTE', '30')
        return int(value) if isinstance(value, str) else value
    
    # Email Settings
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    
    def validate(self):
        """Validate that all required configuration is present"""
        required = [
            ('GMAIL_EMAIL', self.GMAIL_EMAIL),
            ('GMAIL_APP_PASSWORD', self.GMAIL_APP_PASSWORD),
            ('MONGODB_URI', self.MONGODB_URI)
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True


# Create a singleton instance
config = Config()
