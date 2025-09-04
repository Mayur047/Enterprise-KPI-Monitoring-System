import os
from datetime import timedelta

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///kpi_monitoring.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    POWERBI_CLIENT_ID = os.environ.get('POWERBI_CLIENT_ID')
    POWERBI_CLIENT_SECRET = os.environ.get('POWERBI_CLIENT_SECRET')
    POWERBI_TENANT_ID = os.environ.get('POWERBI_TENANT_ID')
    POWERBI_WORKSPACE_ID = os.environ.get('POWERBI_WORKSPACE_ID')

    API_RATE_LIMIT = '1000 per hour'

    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300