# config.py - Configuration settings
from datetime import timedelta

class Config:
    NFC_READ_DELAY = 0.5
    TIMEZONE_OFFSET = timedelta(hours=5, minutes=30)
    
    # Modern Color Scheme
    GUI_BG = "#0f0f23"  # Dark blue-black
    GUI_CARD_BG = "#1a1a2e"  # Card background
    GUI_ACCENT = "#00d4ff"  # Cyan accent
    GUI_ACCENT_DARK = "#0099cc"  # Darker cyan
    GUI_SUCCESS = "#00ff88"  # Green success
    GUI_WARNING = "#ffaa00"  # Orange warning
    GUI_ERROR = "#ff4444"  # Red error
    GUI_TEXT = "#ffffff"  # White text
    GUI_TEXT_SECONDARY = "#b0b0b0"  # Gray text
    
    GUI_FONT_PRIMARY = "Segoe UI"
    GUI_FONT_SECONDARY = "Consolas"