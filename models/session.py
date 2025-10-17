# models/session.py - Session management
from datetime import datetime
from config import Config

class SessionManager:
    def __init__(self):
        self.current_session = None
        self.stop_flag = False
        self.scanned_uids = set()

    def start_session(self, name, duration_minutes=60):
        self.current_session = {
            'name': name,
            'start_time': datetime.utcnow() + Config.TIMEZONE_OFFSET,
            'duration': duration_minutes
        }
        self.stop_flag = False
        self.scanned_uids.clear()

    def end_session(self):
        self.stop_flag = True

    def reset_session(self):
        """Reset session and clear all scanned UIDs"""
        self.scanned_uids.clear()
        self.current_session = None
        self.stop_flag = True

# Global session manager instance
session_mgr = SessionManager()