# nfc/scanner.py - NFC scanning logic
import time
from smartcard.System import readers
from smartcard.Exceptions import NoCardException, CardConnectionException
from config import Config
from database import db
from models import session_mgr, voice_feedback

def nfc_scan_loop(ui):
    GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
    last_uid_per_reader = {}
    
    while not session_mgr.stop_flag:
        try:
            rdrs = readers()
            if not rdrs:
                ui.update_status(" No NFC readers detected", error=True)
                time.sleep(2)
                continue
                
            reader_found = False
            for r in rdrs:
                try:
                    conn = r.createConnection()
                    conn.connect()
                    resp, sw1, sw2 = conn.transmit(GET_UID)
                    if sw1 == 0x90 and sw2 == 0x00 and resp:
                        reader_found = True
                        uid = ''.join(f"{b:02X}" for b in resp)
                        if last_uid_per_reader.get(r) == uid:
                            continue
                        last_uid_per_reader[r] = uid
                        
                        if uid in session_mgr.scanned_uids:
                            student = db.get_student_by_uid(uid)
                            name = student[0] if student else "Unknown"
                            ui.update_status(f" Duplicate scan: {name}", warning=True)
                            voice_feedback(f"Already scanned {name}")
                        else:
                            student = db.get_student_by_uid(uid)
                            if student:
                                name, enroll, roll = student
                                db.log_attendance(uid)
                                session_mgr.scanned_uids.add(uid)
                                ui.update_status(f" Attendance marked: {name}", success=True)
                                voice_feedback(f"Welcome {name}")
                                ui.update_dashboard()
                                ui.add_recent_attendance(name)
                            else:
                                ui.root.after(0, lambda uid=uid: ui.show_add_student_dialog(uid))
                    else:
                        last_uid_per_reader[r] = None
                except (NoCardException, CardConnectionException):
                    last_uid_per_reader[r] = None
                except Exception as e:
                    print(f"Reader error: {e}")
            
            if not reader_found:
                time.sleep(1)
                
            time.sleep(Config.NFC_READ_DELAY)
        except Exception as e:
            ui.update_status(f"❌ Scanner error: {str(e)}", error=True)
            time.sleep(2)