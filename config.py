# GrandStay Hotel Room Management System
# Configuration Module

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    """Base application configuration loaded from environment variables."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'grandstay-hotel-secret-key-super-secure-2026')
    
    # MySQL Database Connection Settings
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'hotel_management')
    MYSQL_CHARSET = 'utf8mb4'
    
    # Application Settings
    HOTEL_NAME = os.getenv('HOTEL_NAME', 'GrandStay Hotel & Suites')
    HOTEL_TAGLINE = os.getenv('HOTEL_TAGLINE', 'Smart Hotel Booking, Room Availability and Billing Management')
    HOTEL_PHONE = os.getenv('HOTEL_PHONE', '+1 (800) 555-4726')
    HOTEL_EMAIL = os.getenv('HOTEL_EMAIL', 'info@grandstayhotel.com')
    HOTEL_ADDRESS = os.getenv('HOTEL_ADDRESS', '742 Evergreen Promenade, Suite 100, Metropolitan City')
    HOTEL_CURRENCY = os.getenv('HOTEL_CURRENCY', '$')
    HOTEL_TAX_RATE = float(os.getenv('HOTEL_TAX_RATE', 0.10)) # 10% tax rate

    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
