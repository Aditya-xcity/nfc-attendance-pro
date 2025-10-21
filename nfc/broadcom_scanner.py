# nfc/broadcom_scanner.py - Improved scanner for Broadcom NFC readers
import time
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from config import Config
from database import db
from models import session_mgr, voice_feedback

# Excel helpers for roster lookup
def _excel_find_by_uid(section, uid):
    try:
        import os, pandas as pd
        path = os.path.join('data/sections', f'{section}.xlsx')
        if not os.path.exists(path):
            return None
        try:
            df = pd.read_excel(path, sheet_name=section, dtype=str)
        except Exception:
            df = pd.read_excel(path, dtype=str)
        df = df.fillna('')
        # Normalize
        cols = {c.strip().lower(): c for c in df.columns}
        def get(row, key):
            c = cols.get(key)
            return str(row[c]).strip() if c in row else ''
        for _, row in df.iterrows():
            ruid = str(row.get(cols.get('uid',''), '')).strip().upper() if 'uid' in cols else ''
            if ruid and ruid.upper() == uid.upper():
                return {
                    'name': get(row, 'name'),
                    'enroll': get(row, 'enrollment no'),
                    'roll': get(row, 'roll no'),
                    'subject': get(row, 'subject'),
                    'section': get(row, 'section') or section,
                    'uid': ruid
                }
        return None
    except Exception:
        return None

def _excel_find_in_any_section(uid):
    try:
        import os, pandas as pd
        base = 'data/sections'
        if not os.path.isdir(base):
            return None
        for fname in os.listdir(base):
            if not fname.lower().endswith('.xlsx'):
                continue
            section = fname.rsplit('.',1)[0]
            rec = _excel_find_by_uid(section, uid)
            if rec:
                return rec
        return None
    except Exception:
        return None

def nfc_scan_loop_web(web_handler):
    """
    Improved web-compatible NFC scanning loop for Broadcom readers
    """
    print("[DEBUG] Starting Broadcom-compatible NFC scanner")
    
    # Common APDU commands for NFC cards
    GET_UID_COMMANDS = [
        [0xFF, 0xCA, 0x00, 0x00, 0x00],  # Standard UID command
        [0xFF, 0xCA, 0x00, 0x00, 0x04],  # UID with 4-byte response
        [0xFF, 0xCA, 0x00, 0x00, 0x07],  # UID with 7-byte response
    ]
    
    last_uid_per_reader = {}
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    web_handler.update_status("🔍 NFC scanning started (Broadcom mode)", success=True)
    print("[DEBUG] Status updated: NFC scanning started")
    
    while not session_mgr.stop_flag:
        try:
            rdrs = readers()
            print(f"[DEBUG] Found {len(rdrs) if rdrs else 0} NFC readers")
            
            if not rdrs:
                web_handler.update_status("❌ No NFC readers detected", error=True)
                print("[DEBUG] No readers found, sleeping...")
                time.sleep(2)
                continue
            
            # Focus on contactless readers (for NFC)
            contactless_readers = [r for r in rdrs if 'contactless' in str(r).lower()]
            if not contactless_readers:
                contactless_readers = rdrs  # Fallback to all readers
            
            card_found = False
            
            for reader in contactless_readers:
                try:
                    print(f"[DEBUG] Checking reader: {reader}")
                    
                    # Use direct connection method
                    connection = reader.createConnection()
                    try:
                        connection.connect()
                    except (NoCardException, CardConnectionException):
                        # No card present, skip this reader
                        last_uid_per_reader[reader] = None
                        continue
                    except Exception as e:
                        print(f"[DEBUG] Connection error: {e}")
                        continue
                    
                    print("[DEBUG] Card detected and connected")
                    
                    uid = None
                    # Try different UID commands
                    for cmd in GET_UID_COMMANDS:
                        try:
                            resp, sw1, sw2 = connection.transmit(cmd)
                            print(f"[DEBUG] Command {cmd}: SW1={sw1:02X}, SW2={sw2:02X}, Resp={resp}")
                            
                            if sw1 == 0x90 and sw2 == 0x00 and resp:
                                uid = ''.join(f"{b:02X}" for b in resp)
                                print(f"[DEBUG] UID extracted: {uid}")
                                break
                                
                        except Exception as e:
                            print(f"[DEBUG] UID command failed: {e}")
                            continue
                    
                    # Only proceed if we got a UID
                    if uid:
                        card_found = True
                        consecutive_errors = 0
                        
                        # If already scanned this session, treat as duplicate (even if same-reader)
                        if uid in session_mgr.scanned_uids:
                            student = db.get_student_by_uid(uid)
                            name = student[0] if student else "Unknown"
                            web_handler.update_status(f"⚠️ Duplicate scan: {name}", warning=True)
                            voice_feedback(f"Already scanned {name}")
                            print(f"[DEBUG] Duplicate scan for: {name}")
                            # Update last seen to keep UI responsive
                            last_uid_per_reader[reader] = uid
                        else:
                            # For new scans, do NOT block on same-reader duplicate the first time
                            if last_uid_per_reader.get(reader) == uid:
                                print(f"[DEBUG] Same-reader UID seen again quickly, but not yet in session set; proceeding: {uid}")
                            
                            last_uid_per_reader[reader] = uid
                            print(f"[DEBUG] Processing new UID: {uid}")
                            
                            # Clear the duplicate detection after a short delay to allow re-scanning
                            def clear_duplicate(r, u):
                                time.sleep(2)  # Allow re-scan after 2 seconds
                                if last_uid_per_reader.get(r) == u:
                                    last_uid_per_reader[r] = None
                                    print(f"[DEBUG] Cleared duplicate lock for: {u}")
                            
                            import threading
                            threading.Thread(target=clear_duplicate, args=(reader, uid), daemon=True).start()
                            
                            # Check if student exists
                            student = db.get_student_by_uid(uid)
                            if student:
                                # Student found - check section
                                name, enroll, roll, section, subject = student
                                print(f"[DEBUG] Student found: {name} (Section: {section})")

                                # Enforce session section, if provided
                                session_section = None
                                try:
                                    if session_mgr.current_session:
                                        session_section = session_mgr.current_session.get('section')
                                except Exception:
                                    session_section = None

                                if session_section and str(section or '').strip().upper() != str(session_section).strip().upper():
                                    # Different section -> do not mark
                                    msg = f"Not from this session: {name} (belongs to {section or 'Unknown'})"
                                    web_handler.update_status(msg, warning=True)
                                    voice_feedback("Not from this session")
                                    print(f"[DEBUG] Section mismatch for UID {uid}: card {section} vs session {session_section}")
                                else:
                                    # Mark attendance
                                    db.log_attendance(uid)
                                    session_mgr.scanned_uids.add(uid)
                                    
                                    # Update web interface
                                    web_handler.update_status(f"✅ Attendance marked: {name}", success=True)
                                    web_handler.add_recent_attendance(name)
                                    web_handler.update_dashboard()
                                    
                                    # Voice feedback
                                    voice_feedback(f"Welcome {name}. Scan next card.")
                                    print(f"[DEBUG] Attendance marked for: {name}")
                            else:
                                # Unknown student - try Excel roster for current session
                                session_section = session_mgr.current_session.get('section') if session_mgr.current_session else None
                                roster_rec = _excel_find_by_uid(session_section, uid) if session_section else None
                                if roster_rec and str(roster_rec.get('section','')).strip().upper() == str(session_section or '').strip().upper():
                                    # Auto-add from roster and mark
                                    name = roster_rec['name']; enroll = roster_rec.get('enroll',''); roll = roster_rec.get('roll','');
                                    section = roster_rec.get('section'); subject = roster_rec.get('subject','');
                                    added = db.add_student(name, enroll, roll, section, subject, uid)
                                    if added:
                                        db.log_attendance(uid)
                                        session_mgr.scanned_uids.add(uid)
                                        web_handler.update_status(f"✅ Attendance marked: {name}", success=True)
                                        web_handler.add_recent_attendance(name)
                                        web_handler.update_dashboard()
                                        voice_feedback(f"Welcome {name}. Scan next card.")
                                        print(f"[DEBUG] Auto-added from Excel and marked: {name}")
                                    else:
                                        web_handler.update_status("⚠️ Could not add student from Excel", warning=True)
                                else:
                                    # See if this UID exists in any other section Excel
                                    other = _excel_find_in_any_section(uid)
                                    if other and (not session_section or str(other.get('section','')).strip().upper() != str(session_section).strip().upper()):
                                        web_handler.update_status("Not from this session", warning=True)
                                        voice_feedback("Not from this session")
                                        print(f"[DEBUG] UID belongs to section {other.get('section')} not current {session_section}")
                                    else:
                                        web_handler.update_status(f"❓ Unknown NFC card: {uid}", warning=True)
                                        voice_feedback("Unknown card detected. Please register student.")
                                        print(f"[DEBUG] Unknown card: {uid}")
                    
                    # Disconnect card
                    try:
                        connection.disconnect()
                    except:
                        pass
                            
                except (NoCardException, CardConnectionException):
                    # No card present - this is normal
                    last_uid_per_reader[reader] = None
                    
                except Exception as e:
                    print(f"[DEBUG] Reader error: {e}")
                    consecutive_errors += 1
                    if consecutive_errors < max_consecutive_errors:
                        continue
                    else:
                        web_handler.update_status(f"⚠️ Reader error: {str(e)}", warning=True)
            
            # Update status if no cards found
            if not card_found:
                if consecutive_errors < max_consecutive_errors:
                    web_handler.update_status("🔍 Scanning for NFC cards...", success=True)
                time.sleep(Config.NFC_READ_DELAY)
            
        except Exception as e:
            print(f"[DEBUG] Scanner error: {e}")
            consecutive_errors += 1
            if consecutive_errors >= max_consecutive_errors:
                web_handler.update_status(f"❌ Scanner error: {str(e)}", error=True)
                time.sleep(2)
                consecutive_errors = 0  # Reset after showing error
    
    web_handler.update_status("🛑 NFC scanning stopped", warning=True)
    print("[DEBUG] NFC scanning stopped")