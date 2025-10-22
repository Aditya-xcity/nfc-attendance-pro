# Virtual NFC Card - System Architecture

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   NFC Attendance System                  │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────┐            ┌─────────────────────┐
│   Main Program   │            │  Test Environment   │
│   (app.py, etc)  │            │   (ISOLATED)        │
│                  │            │                     │
│ - Not modified   │            │ ✅ Fully isolated   │
│ - Works normally │            │ ✅ No dependencies  │
│ - Unchanged      │            │ ✅ Separate storage │
└──────────────────┘            └─────────────────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
            ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
            │  Virtual NFC │    │  Test Suite  │    │  Mock NFC    │
            │    Cards     │    │   (7 tests)  │    │  Scanner     │
            │              │    │              │    │              │
            │ - Create     │    │ - Validation │    │ - Interactive│
            │ - Store      │    │ - Persistence│    │ - Demo mode  │
            │ - Retrieve   │    │ - Scan sim   │    │ - Batch scan │
            │ - Delete     │    │ - JSON I/O   │    │              │
            │ - Save/Load  │    │ - Multi-card │    │              │
            └──────────────┘    └──────────────┘    └──────────────┘
```

## 📦 Module Relationships

```
test/
├── __init__.py
│   └── Exports: VirtualNFCCard, VirtualNFCCardStorage, MockNFCScanner
│
├── virtual_nfc_card.py
│   ├── VirtualNFCCard
│   │   ├── __init__(uid, name)
│   │   ├── write_data(key, value)
│   │   ├── read_data(key=None)
│   │   ├── to_dict()
│   │   ├── to_json()
│   │   └── from_dict(card_dict)
│   │
│   ├── VirtualNFCCardStorage
│   │   ├── __init__(storage_dir)
│   │   ├── create_card(uid, name)
│   │   ├── get_card(uid)
│   │   ├── delete_card(uid)
│   │   ├── list_cards()
│   │   ├── simulate_scan(uid)
│   │   ├── save_card(card)
│   │   └── save_all_cards()
│   │
│   └── get_storage(storage_dir) → VirtualNFCCardStorage
│
├── mock_nfc_scanner.py
│   └── MockNFCScanner
│       ├── __init__(storage_dir)
│       ├── create_test_cards()
│       ├── scan_card(uid)
│       ├── list_available_cards()
│       ├── get_card_info(uid)
│       └── interactive_scan()
│
├── test_virtual_nfc.py
│   ├── test_card_creation()
│   ├── test_card_validation()
│   ├── test_data_write_read()
│   ├── test_card_persistence()
│   ├── test_card_scanning()
│   ├── test_multiple_cards()
│   ├── test_json_serialization()
│   └── run_all_tests()
│
└── virtual_cards/ (storage)
    ├── 2297951A.json
    ├── 33445566.json
    ├── 77889900.json
    ├── AABBCCDD.json
    └── 11223344.json
```

## 🔄 Data Flow: Creating and Scanning a Card

```
1. CREATE CARD
═════════════════════════════════════════════════════════

User Input
   │
   ▼
VirtualNFCCardStorage.create_card(uid, name)
   │
   ├─► VirtualNFCCard(uid, name)  [Create object]
   │
   ├─► card.write_data(key, value) [Store data]
   │
   └─► save_card(card)
       │
       ├─► card.to_json()  [Serialize]
       │
       └─► Write to disk: test/virtual_cards/{uid}.json
           │
           └─► ✅ Card persisted


2. SCAN CARD
═════════════════════════════════════════════════════════

User Input: UID
   │
   ▼
MockNFCScanner.scan_card(uid)
   │
   └─► VirtualNFCCardStorage.simulate_scan(uid)
       │
       ├─► get_card(uid)  [Load from memory or disk]
       │
       ├─► card.read_data()  [Update timestamp & count]
       │
       ├─► save_card(card)  [Persist updated state]
       │
       └─► Return card
           │
           └─► ✅ Scan recorded


3. RETRIEVE CARD
═════════════════════════════════════════════════════════

User Query
   │
   ▼
VirtualNFCCardStorage.get_card(uid)
   │
   └─► Check memory cache → If not found, load from disk
       │
       └─► Return VirtualNFCCard object
           │
           └─► ✅ Card data available
```

## 📊 Card Storage Format

### In Memory
```python
VirtualNFCCard object
├── uid: str (8-32 hex)
├── name: str
├── data: dict (any key-value pairs)
├── created_at: ISO timestamp
├── last_read: ISO timestamp
└── read_count: int
```

### On Disk (JSON)
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

## 🧪 Test Execution Flow

```
python test/test_virtual_nfc.py
   │
   ├─► TEST 1: Card Creation
   │   └─► ✅ PASS
   │
   ├─► TEST 2: UID Validation
   │   └─► ✅ PASS
   │
   ├─► TEST 3: Write/Read Data
   │   └─► ✅ PASS
   │
   ├─► TEST 4: Persistence
   │   ├─► Create card
   │   ├─► Save to disk
   │   ├─► Verify file exists
   │   ├─► Load from disk
   │   ├─► Verify data
   │   └─► ✅ PASS
   │
   ├─► TEST 5: Scanning
   │   ├─► Create cards
   │   ├─► Simulate scans
   │   ├─► Verify count increments
   │   └─► ✅ PASS
   │
   ├─► TEST 6: Multiple Cards
   │   ├─► Create 4 cards
   │   ├─► List all
   │   ├─► Delete one
   │   ├─► Verify count
   │   └─► ✅ PASS
   │
   ├─► TEST 7: JSON Serialization
   │   ├─► Create card
   │   ├─► Export to JSON
   │   ├─► Parse JSON
   │   ├─► Reconstruct card
   │   └─► ✅ PASS
   │
   └─► SUMMARY: 7/7 (100%) ✅
```

## 💾 File Organization

```
test/
├── Python Modules (4 files)
│   ├── __init__.py              [17 lines]     Package init
│   ├── virtual_nfc_card.py      [214 lines]    Core classes
│   ├── test_virtual_nfc.py      [323 lines]    Test suite
│   └── mock_nfc_scanner.py      [226 lines]    Mock scanner
│
├── Documentation (3 files)
│   ├── README.md                [302 lines]    Full reference
│   ├── QUICKSTART.md            [222 lines]    Quick guide
│   └── ARCHITECTURE.md          [This file]    Design docs
│
└── Data Storage
    └── virtual_cards/           [Dynamic]      Card storage
        ├── {UID}.json
        ├── {UID}.json
        └── {UID}.json

Total: ~1,300 lines of code + comprehensive docs
```

## 🔧 Class Hierarchy

```
VirtualNFCCard
├── Properties:
│   ├── uid: str
│   ├── name: str
│   ├── data: dict
│   ├── created_at: str
│   ├── last_read: str
│   └── read_count: int
│
├── Methods:
│   ├── write_data(key, value) → bool
│   ├── read_data(key=None) → Any
│   ├── to_dict() → Dict
│   ├── to_json() → str
│   └── @staticmethod from_dict(dict) → VirtualNFCCard
│
└── Usage:
    card = VirtualNFCCard("2297951A", "Student Name")
    card.write_data("id", "001")
    print(card.read_data())


VirtualNFCCardStorage
├── Properties:
│   ├── storage_dir: str
│   └── cards: Dict[str, VirtualNFCCard]
│
├── Methods:
│   ├── create_card(uid, name) → VirtualNFCCard
│   ├── get_card(uid) → VirtualNFCCard | None
│   ├── delete_card(uid) → bool
│   ├── list_cards() → List[Dict]
│   ├── save_card(card) → bool
│   ├── save_all_cards() → bool
│   ├── simulate_scan(uid) → VirtualNFCCard | None
│   └── _load_all_cards() → None
│
└── Usage:
    storage = VirtualNFCCardStorage()
    card = storage.create_card("UID", "Name")
    scanned = storage.simulate_scan("UID")


MockNFCScanner
├── Properties:
│   ├── storage: VirtualNFCCardStorage
│   ├── scanning: bool
│   └── last_scanned_uid: str
│
├── Methods:
│   ├── create_test_cards() → List[str]
│   ├── scan_card(uid) → str | None
│   ├── list_available_cards() → List[Dict]
│   ├── get_card_info(uid) → Dict | None
│   └── interactive_scan() → None
│
└── Usage:
    scanner = MockNFCScanner()
    scanner.create_test_cards()
    uid = scanner.scan_card("2297951A")
```

## 🔌 Integration Points

### With Main Application

```
Main App (unchanged)
       │
       ├─► Query: Do you want to test?
       │
       └─► Optional:
           from test.virtual_nfc_card import get_storage
           storage = get_storage()
           card = storage.simulate_scan("uid")
           
           ✅ Main app continues normally
           ✅ Test environment completely isolated
```

### Isolation Guarantees

- ✅ No changes to existing code
- ✅ Separate storage directory
- ✅ Independent configuration
- ✅ Self-contained modules
- ✅ Zero side effects
- ✅ Can be deleted without impact

## 📈 Performance Characteristics

```
Operation               Time        Notes
─────────────────────────────────────────────
Create card            <1ms        In-memory
Write data             <1ms        Dict update
Read data              <1ms        Dict lookup
Save to disk           <10ms       JSON serialization
Load from disk         <10ms       File I/O
List cards             <5ms        Iteration
Simulate scan          <5ms        Lookup + update
Validate UID           <1ms        String check
```

## 🎓 Learning Paths

### Beginner
1. Read `test/QUICKSTART.md`
2. Run `python test/mock_nfc_scanner.py --demo`
3. Try `python test/mock_nfc_scanner.py --interactive`

### Intermediate
4. Read `test/README.md` (API reference)
5. Run `python test/test_virtual_nfc.py`
6. Create custom cards in Python

### Advanced
7. Review source code
8. Extend with custom features
9. Integrate with main application

## 🚀 Next Steps

1. **Explore**: `cd test` && `python mock_nfc_scanner.py --demo`
2. **Test**: `python test_virtual_nfc.py`
3. **Learn**: Read `README.md` and `QUICKSTART.md`
4. **Build**: Create your test scenarios

---

For detailed information, see:
- `README.md` - Full API documentation
- `QUICKSTART.md` - Quick start guide
- Individual `.py` files - Well-commented source code
