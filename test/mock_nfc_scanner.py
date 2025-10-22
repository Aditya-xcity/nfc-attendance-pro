"""
Mock NFC Scanner
Simulates the NFC scanner using virtual NFC cards for testing.
Can be used to test the main application without physical NFC hardware.
"""

import os
import sys
import time
import random
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.virtual_nfc_card import VirtualNFCCardStorage, get_storage

class MockNFCScanner:
    """Mock NFC scanner that simulates real card scanning."""
    
    def __init__(self, storage_dir: str = "test/virtual_cards"):
        """
        Initialize mock scanner with virtual card storage.
        
        Args:
            storage_dir: Directory containing virtual cards
        """
        self.storage = VirtualNFCCardStorage(storage_dir)
        self.scanning = False
        self.last_scanned_uid = None
    
    def create_test_cards(self):
        """Create sample test cards for demonstration."""
        test_data = [
            ("2297951A", "Aditya Bhardwaj", "A2900", "D2"),
            ("33445566", "John Doe", "A2001", "A2"),
            ("77889900", "Jane Smith", "B2001", "B2"),
            ("AABBCCDD", "Bob Wilson", "C2001", "C2"),
            ("11223344", "Alice Johnson", "D2001", "D2"),
        ]
        
        created = []
        for uid, name, student_id, section in test_data:
            try:
                card = self.storage.create_card(uid, name)
                card.write_data("student_id", student_id)
                card.write_data("section", section)
                card.write_data("subject", "General")
                self.storage.save_card(card)
                created.append(uid)
            except ValueError:
                # Card already exists
                pass
        
        return created
    
    def scan_card(self, uid: str) -> Optional[str]:
        """
        Simulate scanning a specific card.
        
        Args:
            uid: UID of card to scan
            
        Returns:
            UID if card found, None otherwise
        """
        card = self.storage.simulate_scan(uid)
        if card:
            self.last_scanned_uid = uid
            return uid
        return None
    
    def list_available_cards(self) -> list:
        """List all available cards for scanning."""
        return self.storage.list_cards()
    
    def get_card_info(self, uid: str) -> Optional[dict]:
        """Get detailed info about a card."""
        card = self.storage.get_card(uid)
        if card:
            return card.to_dict()
        return None
    
    def interactive_scan(self):
        """Interactive mode to simulate card scanning."""
        print("\n" + "="*60)
        print("  INTERACTIVE NFC SCANNER SIMULATOR")
        print("="*60)
        
        # Create test cards if needed
        print("\n📱 Loading virtual cards...")
        created = self.create_test_cards()
        if created:
            print(f"   Created {len(created)} new test cards")
        
        # Show available cards
        cards = self.list_available_cards()
        print(f"\n📋 Available cards ({len(cards)} total):")
        for i, card_info in enumerate(cards, 1):
            print(f"   {i}. {card_info['uid']} - {card_info['name']}")
        
        # Interactive scanning
        self.scanning = True
        print("\n📡 Ready to scan! Enter options:")
        print("   - Type a UID to simulate scanning")
        print("   - Type 'list' to show available cards")
        print("   - Type 'info <UID>' to get card details")
        print("   - Type 'quit' to exit")
        
        while self.scanning:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() == 'quit':
                    print("\n👋 Exiting scanner...")
                    break
                
                elif user_input.lower() == 'list':
                    cards = self.list_available_cards()
                    print(f"\n📋 Available cards:")
                    for card_info in cards:
                        print(f"   {card_info['uid']} - {card_info['name']} (reads: {card_info['read_count']})")
                
                elif user_input.lower().startswith('info '):
                    uid = user_input[5:].strip().upper()
                    info = self.get_card_info(uid)
                    if info:
                        print(f"\n📄 Card Info:")
                        print(f"   UID: {info['uid']}")
                        print(f"   Name: {info['name']}")
                        print(f"   Created: {info['created_at']}")
                        print(f"   Last Read: {info['last_read']}")
                        print(f"   Read Count: {info['read_count']}")
                        print(f"   Data: {info['data']}")
                    else:
                        print(f"❌ Card not found: {uid}")
                
                elif user_input and all(c in '0123456789ABCDEF' for c in user_input.upper()):
                    uid = user_input.upper()
                    scanned = self.scan_card(uid)
                    if scanned:
                        card_info = self.get_card_info(scanned)
                        print(f"\n✅ CARD SCANNED!")
                        print(f"   UID: {scanned}")
                        print(f"   Name: {card_info['name']}")
                        print(f"   Data: {card_info['data']}")
                        print(f"   Read Count: {card_info['read_count']}")
                    else:
                        print(f"\n❌ Card not found in storage: {uid}")
                
                else:
                    print("❌ Invalid input. Use a hex UID or a command (list, info, quit)")
            
            except KeyboardInterrupt:
                print("\n\n👋 Scanner stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def demo_automated_scan():
    """Demonstrate automated scanning sequence."""
    print("\n" + "="*60)
    print("  AUTOMATED SCAN DEMONSTRATION")
    print("="*60)
    
    scanner = MockNFCScanner()
    
    # Create test cards
    print("\n📱 Setting up test cards...")
    scanner.create_test_cards()
    
    # Show available cards
    cards = scanner.list_available_cards()
    print(f"✅ {len(cards)} test cards loaded")
    
    # Simulate scanning sequence
    print("\n📡 Simulating scan sequence...")
    scan_sequence = [
        ("2297951A", "Aditya Bhardwaj"),
        ("33445566", "John Doe"),
        ("77889900", "Jane Smith"),
        ("AABBCCDD", "Bob Wilson"),
        ("11223344", "Alice Johnson"),
    ]
    
    for uid, expected_name in scan_sequence:
        time.sleep(0.5)  # Simulate delay between scans
        scanned = scanner.scan_card(uid)
        if scanned:
            card_info = scanner.get_card_info(scanned)
            print(f"\n✅ Scanned: {card_info['uid']}")
            print(f"   Name: {card_info['name']}")
            print(f"   Student ID: {card_info['data'].get('student_id', 'N/A')}")
            print(f"   Section: {card_info['data'].get('section', 'N/A')}")
        else:
            print(f"❌ Failed to scan: {uid}")
    
    # Show statistics
    print("\n📊 Scan Statistics:")
    cards = scanner.list_available_cards()
    for card_info in cards:
        if card_info['read_count'] > 0:
            print(f"   {card_info['name']}: {card_info['read_count']} reads")
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Mock NFC Scanner for Testing")
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--demo', '-d', action='store_true', help='Run automated demo')
    
    args = parser.parse_args()
    
    if args.interactive:
        scanner = MockNFCScanner()
        scanner.interactive_scan()
    elif args.demo:
        demo_automated_scan()
    else:
        # Default: show help and run demo
        print("Mock NFC Scanner for Testing\n")
        print("Usage:")
        print("  python test/mock_nfc_scanner.py --interactive  # Interactive scanning")
        print("  python test/mock_nfc_scanner.py --demo         # Automated demonstration\n")
        demo_automated_scan()
