"""
Test package for NFC Attendance System
Contains virtual NFC card emulation and testing utilities.
"""

from test.virtual_nfc_card import VirtualNFCCard, VirtualNFCCardStorage, get_storage
from test.mock_nfc_scanner import MockNFCScanner

__all__ = [
    'VirtualNFCCard',
    'VirtualNFCCardStorage',
    'get_storage',
    'MockNFCScanner',
]

__version__ = '1.0.0'
__description__ = 'Virtual NFC Card Testing Suite'
