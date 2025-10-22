"""
Test Suite for Virtual NFC Card
Tests card creation, data storage, persistence, and scanning simulation.
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test.virtual_nfc_card import VirtualNFCCard, VirtualNFCCardStorage, get_storage

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_card_creation():
    """Test creating a virtual NFC card."""
    print_header("TEST 1: Card Creation")
    
    try:
        card = VirtualNFCCard("ABCD1234", "Test Student")
        assert card.uid == "ABCD1234"
        assert card.name == "Test Student"
        assert card.read_count == 0
        print("✅ Card created successfully")
        print(f"   UID: {card.uid}")
        print(f"   Name: {card.name}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_card_validation():
    """Test card UID validation."""
    print_header("TEST 2: Card UID Validation")
    
    tests = [
        ("INVALID!!!", False, "Invalid characters"),
        ("ABC", False, "Too short"),
        ("ABCD12345678901234567890123456789", False, "Too long"),
        ("2297951A", True, "Valid UID"),
    ]
    
    passed = 0
    for uid, should_pass, desc in tests:
        try:
            card = VirtualNFCCard(uid)
            if should_pass:
                print(f"✅ {desc}: '{uid}' accepted")
                passed += 1
            else:
                print(f"❌ {desc}: '{uid}' should have failed")
        except ValueError as e:
            if not should_pass:
                print(f"✅ {desc}: '{uid}' rejected as expected")
                passed += 1
            else:
                print(f"❌ {desc}: '{uid}' should have passed - {e}")
    
    return passed == len(tests)

def test_data_write_read():
    """Test writing and reading data on cards."""
    print_header("TEST 3: Write/Read Data")
    
    try:
        card = VirtualNFCCard("AAAABBBB", "Data Test Card")
        
        # Write data
        card.write_data("student_id", "A2001")
        card.write_data("section", "D2")
        card.write_data("name", "John Doe")
        card.write_data("subjects", ["Math", "Physics", "Chemistry"])
        
        # Read specific data
        sid = card.read_data("student_id")
        assert sid == "A2001", f"Expected A2001, got {sid}"
        print(f"✅ Write/read specific data: student_id = {sid}")
        
        # Read all data
        all_data = card.read_data()
        assert "section" in all_data
        assert len(all_data) == 4
        print(f"✅ Read all data: {len(all_data)} fields stored")
        print(f"   Fields: {list(all_data.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_card_persistence():
    """Test saving and loading cards from disk."""
    print_header("TEST 4: Card Persistence")
    
    test_dir = "test/virtual_cards_test"
    
    try:
        # Clean up test directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        # Create storage and card
        storage = VirtualNFCCardStorage(test_dir)
        card = storage.create_card("DEADBEEF", "Persistence Test")
        card.write_data("value1", "data1")
        card.write_data("value2", 12345)
        storage.save_card(card)
        
        print(f"✅ Card saved to disk")
        
        # Verify file exists
        expected_file = os.path.join(test_dir, "DEADBEEF.json")
        assert os.path.exists(expected_file), "Card file not found"
        print(f"✅ Card file exists: {expected_file}")
        
        # Create new storage instance and load
        storage2 = VirtualNFCCardStorage(test_dir)
        loaded_card = storage2.get_card("DEADBEEF")
        
        assert loaded_card is not None, "Card not loaded"
        assert loaded_card.name == "Persistence Test"
        assert loaded_card.read_data("value1") == "data1"
        assert loaded_card.read_data("value2") == 12345
        
        print(f"✅ Card loaded from disk successfully")
        print(f"   Name: {loaded_card.name}")
        print(f"   Data: {loaded_card.read_data()}")
        
        # Clean up
        shutil.rmtree(test_dir)
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        return False

def test_card_scanning():
    """Test scanning simulation."""
    print_header("TEST 5: Card Scanning Simulation")
    
    test_dir = "test/virtual_cards_scan_test"
    
    try:
        # Clean up test directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        storage = VirtualNFCCardStorage(test_dir)
        
        # Create cards
        card1 = storage.create_card("CAFE0001", "Student 1")
        card1.write_data("student_id", "001")
        storage.save_card(card1)
        
        card2 = storage.create_card("CAFE0002", "Student 2")
        card2.write_data("student_id", "002")
        storage.save_card(card2)
        
        print(f"✅ Created 2 test cards")
        
        # Simulate scans
        scanned = storage.simulate_scan("CAFE0001")
        assert scanned is not None
        assert scanned.read_count == 1
        print(f"✅ First scan: read_count = {scanned.read_count}")
        
        # Scan again
        scanned = storage.simulate_scan("CAFE0001")
        assert scanned.read_count == 2
        print(f"✅ Second scan: read_count = {scanned.read_count}")
        
        # Scan non-existent card
        not_found = storage.simulate_scan("NONEXISTENT")
        assert not_found is None
        print(f"✅ Non-existent card returns None")
        
        # Clean up
        shutil.rmtree(test_dir)
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        return False

def test_multiple_cards():
    """Test managing multiple cards."""
    print_header("TEST 6: Multiple Cards Management")
    
    test_dir = "test/virtual_cards_multi_test"
    
    try:
        # Clean up test directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        storage = VirtualNFCCardStorage(test_dir)
        
        # Create multiple cards
        uids = ["2297951A", "33445566", "77889900", "AABBCCDD"]
        names = ["Aditya Bhardwaj", "John Doe", "Jane Smith", "Bob Wilson"]
        
        for uid, name in zip(uids, names):
            card = storage.create_card(uid, name)
            card.write_data("student_id", f"STU_{uid}")
            card.write_data("section", "D2")
        
        print(f"✅ Created {len(uids)} cards")
        
        # List all cards
        all_cards = storage.list_cards()
        assert len(all_cards) == len(uids)
        print(f"✅ Listed {len(all_cards)} cards")
        
        for card_info in all_cards:
            print(f"   - {card_info['uid']}: {card_info['name']}")
        
        # Delete one card
        storage.delete_card("33445566")
        all_cards = storage.list_cards()
        assert len(all_cards) == 3
        print(f"✅ Deleted 1 card, {len(all_cards)} remaining")
        
        # Clean up
        shutil.rmtree(test_dir)
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        return False

def test_json_serialization():
    """Test JSON export/import."""
    print_header("TEST 7: JSON Serialization")
    
    try:
        card = VirtualNFCCard("DEADC0DE", "JSON Test Card")
        card.write_data("field1", "value1")
        card.write_data("field2", 42)
        card.write_data("field3", ["a", "b", "c"])
        
        # Export to JSON
        json_str = card.to_json()
        assert isinstance(json_str, str)
        print(f"✅ Card exported to JSON ({len(json_str)} chars)")
        
        # Parse JSON
        data = json.loads(json_str)
        assert data['uid'] == "DEADC0DE"
        assert data['name'] == "JSON Test Card"
        assert len(data['data']) == 3
        print(f"✅ JSON parsed successfully")
        print(f"   Fields in JSON: {list(data['data'].keys())}")
        
        # Reconstruct from dict
        card2 = VirtualNFCCard.from_dict(data)
        assert card2.uid == card.uid
        assert card2.name == card.name
        assert card2.read_data() == card.read_data()
        print(f"✅ Card reconstructed from JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def run_all_tests():
    """Run all test suites."""
    print("\n" + "="*60)
    print("  VIRTUAL NFC CARD TEST SUITE")
    print("="*60)
    
    tests = [
        test_card_creation,
        test_card_validation,
        test_data_write_read,
        test_card_persistence,
        test_card_scanning,
        test_multiple_cards,
        test_json_serialization,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {e}")
            results.append(False)
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
