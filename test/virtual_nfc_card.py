"""
Virtual NFC Card Emulator
Simulates NFC card reading/writing without requiring physical hardware.
Stores and retrieves UID and custom data.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

class VirtualNFCCard:
    """Represents a virtual NFC card with UID and data storage."""
    
    def __init__(self, uid: str, name: str = "Virtual Card"):
        """
        Initialize a virtual NFC card.
        
        Args:
            uid: Unique identifier (8-32 hex characters)
            name: Human-readable name for the card
        """
        self.uid = uid.upper()
        self.name = name
        self.data = {}
        self.created_at = datetime.now().isoformat()
        self.last_read = None
        self.read_count = 0
        
        # Validate UID format
        if not all(c in '0123456789ABCDEF' for c in self.uid):
            raise ValueError(f"Invalid UID format: {uid}. Must be hex characters only.")
        if not (8 <= len(self.uid) <= 32):
            raise ValueError(f"UID must be 8-32 hex characters, got {len(self.uid)}")
    
    def write_data(self, key: str, value: Any) -> bool:
        """Write data to the card."""
        try:
            self.data[key] = value
            return True
        except Exception as e:
            print(f"[ERROR] Failed to write data: {e}")
            return False
    
    def read_data(self, key: str = None) -> Any:
        """Read data from the card."""
        self.last_read = datetime.now().isoformat()
        self.read_count += 1
        
        if key is None:
            return self.data.copy()
        return self.data.get(key)
    
    def to_dict(self) -> Dict:
        """Convert card to dictionary for serialization."""
        return {
            'uid': self.uid,
            'name': self.name,
            'data': self.data,
            'created_at': self.created_at,
            'last_read': self.last_read,
            'read_count': self.read_count
        }
    
    def to_json(self) -> str:
        """Convert card to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @staticmethod
    def from_dict(card_dict: Dict) -> 'VirtualNFCCard':
        """Create a card from dictionary."""
        card = VirtualNFCCard(card_dict['uid'], card_dict.get('name', 'Virtual Card'))
        card.data = card_dict.get('data', {})
        card.created_at = card_dict.get('created_at', card.created_at)
        card.last_read = card_dict.get('last_read')
        card.read_count = card_dict.get('read_count', 0)
        return card


class VirtualNFCCardStorage:
    """Manages a collection of virtual NFC cards with file persistence."""
    
    def __init__(self, storage_dir: str = "test/virtual_cards"):
        """
        Initialize card storage.
        
        Args:
            storage_dir: Directory to store card files
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.cards: Dict[str, VirtualNFCCard] = {}
        self._load_all_cards()
    
    def create_card(self, uid: str, name: str = "Virtual Card") -> VirtualNFCCard:
        """Create and store a new virtual card."""
        if uid.upper() in self.cards:
            raise ValueError(f"Card with UID {uid} already exists")
        
        card = VirtualNFCCard(uid, name)
        self.cards[card.uid] = card
        self.save_card(card)
        return card
    
    def get_card(self, uid: str) -> Optional[VirtualNFCCard]:
        """Retrieve a card by UID."""
        return self.cards.get(uid.upper())
    
    def delete_card(self, uid: str) -> bool:
        """Delete a card."""
        uid = uid.upper()
        if uid in self.cards:
            del self.cards[uid]
            filepath = os.path.join(self.storage_dir, f"{uid}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        return False
    
    def save_card(self, card: VirtualNFCCard) -> bool:
        """Save a card to disk."""
        try:
            filepath = os.path.join(self.storage_dir, f"{card.uid}.json")
            with open(filepath, 'w') as f:
                f.write(card.to_json())
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save card: {e}")
            return False
    
    def save_all_cards(self) -> bool:
        """Save all cards to disk."""
        try:
            for card in self.cards.values():
                self.save_card(card)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save cards: {e}")
            return False
    
    def _load_all_cards(self) -> None:
        """Load all cards from disk."""
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    with open(filepath, 'r') as f:
                        card_dict = json.load(f)
                        card = VirtualNFCCard.from_dict(card_dict)
                        self.cards[card.uid] = card
        except Exception as e:
            print(f"[WARN] Failed to load cards: {e}")
    
    def list_cards(self) -> list:
        """List all available cards."""
        return [
            {
                'uid': card.uid,
                'name': card.name,
                'read_count': card.read_count,
                'last_read': card.last_read
            }
            for card in self.cards.values()
        ]
    
    def simulate_scan(self, uid: str) -> Optional[VirtualNFCCard]:
        """Simulate scanning a card and return it."""
        card = self.get_card(uid)
        if card:
            card.read_data()  # Update read timestamp
            self.save_card(card)
        return card


# Global storage instance
_storage = None

def get_storage(storage_dir: str = "test/virtual_cards") -> VirtualNFCCardStorage:
    """Get or create global storage instance."""
    global _storage
    if _storage is None:
        _storage = VirtualNFCCardStorage(storage_dir)
    return _storage


if __name__ == "__main__":
    # Example usage
    storage = get_storage()
    
    # Create a new card
    card1 = storage.create_card("2297951A", "Aditya Bhardwaj")
    card1.write_data("student_id", "A2900")
    card1.write_data("section", "D2")
    card1.write_data("subject", "Major")
    
    print("✅ Created card:", card1.uid)
    print(json.dumps(card1.to_dict(), indent=2))
    
    # Create another card
    card2 = storage.create_card("33445566", "John Doe")
    card2.write_data("student_id", "A2001")
    card2.write_data("section", "A2")
    
    # Simulate scanning
    scanned = storage.simulate_scan("2297951A")
    print(f"\n✅ Simulated scan: {scanned.name}")
    print(f"   UID: {scanned.uid}")
    print(f"   Data: {scanned.read_data()}")
    print(f"   Read count: {scanned.read_count}")
    
    # List all cards
    print("\n📄 All Virtual Cards:")
    for info in storage.list_cards():
        print(f"   {info['uid']} - {info['name']}")
