# models/session.py - Session management
from datetime import datetime
from config import Config

class SessionManager:
    def __init__(self):
        self.current_session = None
        self.stop_flag = False
        self.scanned_uids = set()

    def start_session(self, name, duration_minutes=60, **kwargs):
        self.current_session = {
            'name': name,
            'start_time': datetime.utcnow() + Config.TIMEZONE_OFFSET,
            'duration': duration_minutes,
            # Optional class context
            'subject': kwargs.get('subject'),
            'section': kwargs.get('section'),
            'class_start': kwargs.get('class_start'),
            'class_end': kwargs.get('class_end'),
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