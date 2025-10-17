# utils/helpers.py - Utility functions
from datetime import datetime
from config import Config

def get_current_time():
    """Get current time with timezone offset"""
    return datetime.utcnow() + Config.TIMEZONE_OFFSET

def format_time(dt=None):
    """Format datetime object to string"""
    if dt is None:
        dt = get_current_time()
    return dt.strftime("%H:%M:%S")

def format_date(dt=None):
    """Format datetime object to date string"""
    if dt is None:
        dt = get_current_time()
    return dt.strftime("%Y-%m-%d")