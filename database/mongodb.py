from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import Config
import streamlit as st

class MongoDB:
    """MongoDB connection manager"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Establish connection to MongoDB"""
        if self._client is None:
            try:
                self._client = MongoClient(
                    Config.MONGODB_URI,
                    serverSelectionTimeoutMS=5000
                )
                # Test the connection
                self._client.admin.command('ping')
                self._db = self._client[Config.MONGODB_DB_NAME]
                return True
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                st.error(f"Failed to connect to MongoDB: {str(e)}")
                return False
        return True
    
    @property
    def db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db
    
    @property
    def campaigns(self):
        """Get campaigns collection"""
        return self.db.campaigns
    
    @property
    def email_logs(self):
        """Get email logs collection"""
        return self.db.email_logs
    
    @property
    def templates(self):
        """Get templates collection"""
        return self.db.templates
    
    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

# Singleton instance
mongodb = MongoDB()
