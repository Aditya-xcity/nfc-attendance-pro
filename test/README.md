# Virtual NFC Card Testing Suite

This test folder contains tools for testing NFC attendance functionality without requiring physical NFC hardware.

## 📁 Files

### `virtual_nfc_card.py`
Core module for virtual NFC card emulation.

**Features:**
- Create virtual NFC cards with custom UIDs and data
- Store arbitrary key-value data on cards
- Persistent storage to disk (JSON format)
- Read/write tracking with timestamps
- Import/export functionality

**Classes:**
- `VirtualNFCCard` - Individual card representation
- `VirtualNFCCardStorage` - Collection management with persistence

**Usage:**
```python
from test.virtual_nfc_card import VirtualNFCCardStorage

# Initialize storage
storage = VirtualNFCCardStorage("test/virtual_cards")

# Create a card
card = storage.create_card("2297951A", "Aditya Bhardwaj")
card.write_data("student_id", "A2900")
card.write_data("section", "D2")

# Simulate scanning
scanned = storage.simulate_scan("2297951A")
print(f"Scanned: {scanned.name}")
```

### `test_virtual_nfc.py`
Comprehensive test suite for virtual NFC functionality.

**Tests:**
1. Card creation validation
2. UID format validation
3. Write/read data operations
4. Persistence to disk
5. Scanning simulation
6. Multiple card management
7. JSON serialization

**Run tests:**
```bash
python test/test_virtual_nfc.py
```

**Output:**
```
============================================================
  VIRTUAL NFC CARD TEST SUITE
============================================================

============================================================
  TEST 1: Card Creation
============================================================
✅ Card created successfully
   UID: ABCD1234
   Name: Test Student

... (more tests)

============================================================
  TEST SUMMARY
============================================================
Passed: 7/7 (100.0%)

🎉 All tests passed!
```

### `mock_nfc_scanner.py`
Mock NFC scanner for interactive testing and demonstration.

**Modes:**

#### Interactive Mode
```bash
python test/mock_nfc_scanner.py --interactive
```

Commands:
- Type a UID to simulate scanning (e.g., `2297951A`)
- `list` - Show available cards
- `info <UID>` - Get detailed card information
- `quit` - Exit scanner

Example:
```
> list
📋 Available cards:
   2297951A - Aditya Bhardwaj (reads: 0)
   33445566 - John Doe (reads: 0)

> 2297951A
✅ CARD SCANNED!
   UID: 2297951A
   Name: Aditya Bhardwaj
   Data: {'student_id': 'A2900', 'section': 'D2', 'subject': 'General'}
   Read Count: 1
```

#### Demo Mode
```bash
python test/mock_nfc_scanner.py --demo
```

Automatically simulates scanning sequence with test cards and shows statistics.

## 🎯 Use Cases

### 1. Test Card Creation
```python
from test.virtual_nfc_card import VirtualNFCCard

card = VirtualNFCCard("DEADBEEF", "Test Student")
card.write_data("student_id", "TEST001")
card.write_data("section", "A1")
```

### 2. Batch Create Multiple Cards
```python
from test.virtual_nfc_card import VirtualNFCCardStorage

storage = VirtualNFCCardStorage()
for i in range(10):
    uid = f"{i:08X}"
    card = storage.create_card(uid, f"Student {i}")
    card.write_data("roll", str(i))
```

### 3. Simulate Attendance Session
```python
scanner = MockNFCScanner()
scanner.create_test_cards()

# Simulate multiple scans
for uid in ["2297951A", "33445566", "77889900"]:
    result = scanner.scan_card(uid)
    if result:
        print(f"Attendance marked for {result}")
```

### 4. Test Data Persistence
```python
storage = VirtualNFCCardStorage()

# Create and save
card = storage.create_card("PERSIST1", "Test")
card.write_data("data", "important")
storage.save_card(card)

# Load later
new_storage = VirtualNFCCardStorage()
loaded = new_storage.get_card("PERSIST1")
print(loaded.read_data("data"))  # Output: important
```

## 📊 Virtual Card Structure

Each virtual card stores:
```json
{
  "uid": "2297951A",
  "name": "Aditya Bhardwaj",
  "data": {
    "student_id": "A2900",
    "section": "D2",
    "subject": "General"
  },
  "created_at": "2024-10-21T18:45:10.123456",
  "last_read": "2024-10-21T18:50:30.654321",
  "read_count": 5
}
```

## 🔐 UID Format

Valid UIDs:
- Length: 8-32 hexadecimal characters
- Characters: 0-9, A-F (case-insensitive)
- Examples: `2297951A`, `DEADBEEF`, `00112233`, `AABBCCDDEEFF0011`

## 📝 Storage Location

Virtual cards are stored as JSON files:
```
test/
├── virtual_cards/           # Default storage directory
│   ├── 2297951A.json
│   ├── 33445566.json
│   └── 77889900.json
├── virtual_nfc_card.py
├── test_virtual_nfc.py
├── mock_nfc_scanner.py
└── README.md
```

## 🚀 Integration with Main Application

To use virtual cards with the main application:

1. **Import the module:**
   ```python
   from test.virtual_nfc_card import get_storage
   ```

2. **Get storage instance:**
   ```python
   storage = get_storage()
   ```

3. **Scan cards:**
   ```python
   card = storage.simulate_scan("2297951A")
   ```

The main application code remains unchanged. Virtual cards are only used for testing.

## 🧪 Example Test Workflow

```bash
# 1. Run unit tests
python test/test_virtual_nfc.py

# 2. Try interactive scanner
python test/mock_nfc_scanner.py --interactive

# 3. Run demo
python test/mock_nfc_scanner.py --demo

# 4. Create custom test scenario
python -c "
from test.virtual_nfc_card import VirtualNFCCardStorage
s = VirtualNFCCardStorage()
c = s.create_card('CUSTOM01', 'My Test Card')
c.write_data('test', 'value')
print(f'Card created: {c.uid}')
"
```

## ⚙️ Troubleshooting

### Cards not persisting
- Check `test/virtual_cards/` directory exists
- Ensure write permissions to test folder
- Verify JSON files are created

### Storage directory already has cards
- Delete `test/virtual_cards/` and recreate
- Or use custom storage directory: `VirtualNFCCardStorage("test/my_custom_storage")`

### UID validation fails
- UIDs must be 8-32 hex characters
- No special characters allowed
- Case-insensitive (automatically converted to uppercase)

## 📚 API Reference

### VirtualNFCCard
```python
card = VirtualNFCCard(uid, name)
card.write_data(key, value)        # Store data
card.read_data(key=None)            # Read specific or all data
card.to_dict()                      # Dictionary representation
card.to_json()                      # JSON string
```

### VirtualNFCCardStorage
```python
storage = VirtualNFCCardStorage(storage_dir)
storage.create_card(uid, name)      # Create new card
storage.get_card(uid)               # Retrieve card
storage.delete_card(uid)            # Delete card
storage.list_cards()                # List all cards
storage.simulate_scan(uid)          # Scan simulation
storage.save_card(card)             # Save to disk
storage.save_all_cards()            # Save all
```

### MockNFCScanner
```python
scanner = MockNFCScanner()
scanner.create_test_cards()         # Create sample cards
scanner.scan_card(uid)              # Simulate scan
scanner.list_available_cards()      # List cards
scanner.get_card_info(uid)          # Get details
scanner.interactive_scan()          # Interactive mode
```

## 📞 Support

For issues or questions:
1. Check this README
2. Review test files for examples
3. Run `python test/test_virtual_nfc.py` to verify setup
