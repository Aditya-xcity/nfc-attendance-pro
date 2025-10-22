# Virtual NFC Card - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### 1. Run the Test Suite
```bash
python test\test_virtual_nfc.py
```
This runs 7 comprehensive tests verifying all functionality. ✅ All tests should pass.

### 2. Try the Demo
```bash
python test\mock_nfc_scanner.py --demo
```
Watch automated scanning of 5 virtual cards with statistics.

### 3. Interactive Scanning
```bash
python test\mock_nfc_scanner.py --interactive
```
Manually simulate card scanning. Try these commands:
- Type `2297951A` to scan Aditya's card
- Type `list` to see all available cards
- Type `info 2297951A` to see card details
- Type `quit` to exit

## 📚 Common Usage Patterns

### Create a Custom Card
```python
from test.virtual_nfc_card import VirtualNFCCardStorage

storage = VirtualNFCCardStorage()
card = storage.create_card("MYCARDID", "Student Name")
card.write_data("student_id", "A2001")
card.write_data("section", "D2")
```

### Simulate Scanning Sequence
```python
from test.mock_nfc_scanner import MockNFCScanner

scanner = MockNFCScanner()
scanner.create_test_cards()

for uid in ["2297951A", "33445566", "77889900"]:
    result = scanner.scan_card(uid)
    if result:
        print(f"✅ Scanned: {result}")
```

### List All Cards
```python
from test.virtual_nfc_card import VirtualNFCCardStorage

storage = VirtualNFCCardStorage()
cards = storage.list_cards()

for card in cards:
    print(f"{card['uid']} - {card['name']}")
```

### Get Card Details
```python
from test.virtual_nfc_card import VirtualNFCCardStorage

storage = VirtualNFCCardStorage()
card = storage.get_card("2297951A")

if card:
    print(f"Name: {card.name}")
    print(f"Data: {card.read_data()}")
    print(f"Read Count: {card.read_count}")
```

## 📁 File Structure
```
test/
├── __init__.py                 # Package initialization
├── virtual_nfc_card.py         # Core NFC card emulation
├── test_virtual_nfc.py         # Test suite
├── mock_nfc_scanner.py         # Mock scanner
├── README.md                   # Full documentation
└── QUICKSTART.md               # This file
```

## 🎯 Pre-created Test Cards

The system automatically creates these test cards:

| UID | Name | Student ID | Section |
|-----|------|------------|---------|
| 2297951A | Aditya Bhardwaj | A2900 | D2 |
| 33445566 | John Doe | A2001 | A2 |
| 77889900 | Jane Smith | B2001 | B2 |
| AABBCCDD | Bob Wilson | C2001 | C2 |
| 11223344 | Alice Johnson | D2001 | D2 |

Use these UIDs for testing without creating custom cards.

## 🔧 UID Format Rules

Valid UID examples:
- `2297951A` ✅ 8 hex chars
- `DEADBEEF` ✅ 8 hex chars
- `CAFE0001` ✅ 8 hex chars
- `AABBCCDDEEFF0011` ✅ 16 hex chars

Invalid UID examples:
- `INVALID!!` ❌ Contains special characters
- `ABC` ❌ Too short (needs 8-32)
- `ZZZ00000` ❌ Contains Z (not hex)

## 📊 Storage Location

Virtual cards are stored as JSON files in:
```
test/virtual_cards/
```

Each card is a separate file:
```
test/virtual_cards/
├── 2297951A.json
├── 33445566.json
└── 77889900.json
```

Delete files to reset cards.

## 🐛 Troubleshooting

### "Card not found" error
- Ensure the UID exists with `list` command
- Check UID is typed correctly (case-insensitive)
- Run `scanner.create_test_cards()` to populate defaults

### Import errors
- Verify you're in the `nfc_aditya` directory
- Check `test/__init__.py` exists
- Try: `python -c "from test import VirtualNFCCard; print('OK')"`

### JSON files not saving
- Check `test/virtual_cards/` directory is writable
- Ensure sufficient disk space
- Try deleting `test/virtual_cards/` and recreating

## 🎓 Example Projects

### Test Attendance Marking
```python
from test.mock_nfc_scanner import MockNFCScanner

scanner = MockNFCScanner()
scanner.create_test_cards()
attendance = {}

for card_info in scanner.list_available_cards():
    scanned = scanner.scan_card(card_info['uid'])
    if scanned:
        attendance[scanned] = True

print(f"Marked {len(attendance)} students present")
```

### Verify Read Count
```python
from test.virtual_nfc_card import VirtualNFCCardStorage

storage = VirtualNFCCardStorage()

# Simulate multiple scans
for _ in range(3):
    card = storage.simulate_scan("2297951A")

# Check
final_card = storage.get_card("2297951A")
print(f"Total reads: {final_card.read_count}")  # Output: 3
```

### Export Card Data
```python
from test.virtual_nfc_card import VirtualNFCCardStorage
import json

storage = VirtualNFCCardStorage()
card = storage.get_card("2297951A")

# Export to JSON
with open("card_backup.json", "w") as f:
    f.write(card.to_json())
```

## 📞 Need Help?

1. **Full Documentation**: See `test/README.md`
2. **Run Tests**: `python test/test_virtual_nfc.py`
3. **Check Examples**: Review code comments in the `.py` files
4. **Try Demo**: `python test/mock_nfc_scanner.py --demo`

## ✨ Features Summary

✅ Create unlimited virtual NFC cards  
✅ Store custom data on each card  
✅ Simulate card scanning  
✅ Persistent storage to disk  
✅ Interactive testing mode  
✅ Automated test suite  
✅ Read/write tracking  
✅ JSON import/export  
✅ No physical hardware required  
✅ Fully isolated from main application  

## 🎉 You're Ready!

Your virtual NFC card testing system is ready to use. Start with:

```bash
python test\mock_nfc_scanner.py --interactive
```

Enjoy testing! 🚀
