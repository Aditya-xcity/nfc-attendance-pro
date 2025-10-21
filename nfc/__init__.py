# nfc/__init__.py
# Minimal export to avoid importing removed modules.
try:
    from .broadcom_scanner import nfc_scan_loop_web  # preferred
except Exception:
    nfc_scan_loop_web = None
