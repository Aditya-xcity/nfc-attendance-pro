# app.py - Flask web application for NFC Attendance Pro
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from threading import Thread
import json
import os
from datetime import datetime

from config import Config
from database import db
from models import session_mgr, voice_feedback
# Try to use Broadcom scanner first, fallback to regular scanner
try:
    from nfc.broadcom_scanner import nfc_scan_loop_web
    print("[INFO] Using Broadcom-compatible NFC scanner")
except ImportError:
    from nfc.web_scanner import nfc_scan_loop_web
    print("[INFO] Using standard NFC scanner")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nfc-attendance-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebNFCHandler:
    def __init__(self, socketio):
        self.socketio = socketio
        self.scanning_thread = None
        self.last_status = { 'message': 'System Ready', 'type': 'info' }
        self.last_attendance = None
    
    def update_status(self, msg, success=False, warning=False, error=False):
        status_type = 'success' if success else 'warning' if warning else 'error' if error else 'info'
        self.last_status = { 'message': msg, 'type': status_type }
        self.socketio.emit('status_update', {
            'message': msg,
            'type': status_type
        })
    
    def update_dashboard(self):
        total, present = db.get_today_stats()
        absent = total - present
        self.socketio.emit('dashboard_update', {
            'total': total,
            'present': present,
            'absent': absent
        })
    
    def add_recent_attendance(self, name):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.last_attendance = { 'name': name, 'time': time_str }
        self.socketio.emit('new_attendance', {
            'name': name,
            'time': time_str
        })
    
    def show_add_student_dialog(self, uid):
        self.socketio.emit('show_student_dialog', {
            'uid': uid
        })

web_handler = WebNFCHandler(socketio)

@app.route('/')
def dashboard():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    # Redirect to minimal class session view
    return redirect(url_for('class_session_page'))

@app.route('/session')
def class_session_page():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('class_session.html')

@app.route('/students')
def students_page():
    if 'authenticated' not in session:
        return redirect(url_for('login'))
    return render_template('students.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if db.authenticate_admin(username, password):
            session['authenticated'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/start_session', methods=['POST'])
def start_session():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    username = session.get('username')
    print(f"[DEBUG] Starting session for user: {username}")
    session_mgr.start_session(name=f"Session by {username}")
    
    if web_handler.scanning_thread and web_handler.scanning_thread.is_alive():
        print("[DEBUG] Stopping existing scanning thread...")
        web_handler.scanning_thread.join(timeout=1.0)
        
    print("[DEBUG] Creating new scanning thread...")
    web_handler.scanning_thread = Thread(target=nfc_scan_loop_web, args=(web_handler,), daemon=True)
    web_handler.scanning_thread.start()
    print(f"[DEBUG] Scanning thread started: {web_handler.scanning_thread.is_alive()}")
    
    voice_feedback("Session started. Ready for scanning.")
    return jsonify({'success': True, 'message': 'Session started successfully'})

@app.route('/api/end_session', methods=['POST'])
def end_session():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    session_mgr.end_session()
    voice_feedback("Session ended")
    
    total, present = db.get_today_stats()
    return jsonify({
        'success': True,
        'message': 'Session ended',
        'stats': {
            'total': total,
            'present': present,
            'absent': total - present
        }
    })

@app.route('/api/start_class_session', methods=['POST'])
def start_class_session():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    data = request.get_json() or {}
    subject = data.get('subject')
    section = data.get('section')
    class_start = data.get('class_start')
    class_end = data.get('class_end')
    if not subject or not section:
        return jsonify({'success': False, 'message': 'Subject and Section are required'})
    
    # Auto-import the selected section from Excel (idempotent)
    try:
        import_section_from_excel(section)
    except Exception:
        pass

    # Clear today's attendance for fresh session
    print("[DEBUG] Clearing today's attendance for fresh session...")
    try:
        import pandas as pd
        today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
        df_att = pd.read_excel('data/attendance.xlsx', sheet_name='Attendance', dtype=str)
        df_att = df_att[df_att['Date'] != today]
        df_att.to_excel('data/attendance.xlsx', index=False, sheet_name='Attendance')
        print(f"[DEBUG] Cleared attendance records for {today}")
    except Exception as e:
        print(f"[DEBUG] Could not clear attendance: {e}")
    
    # Start session with class context
    username = session.get('username')
    session_mgr.start_session(
        name=f"Class by {username}",
        subject=subject,
        section=section,
        class_start=class_start,
        class_end=class_end
    )
    
    # Reset session scanned UIDs
    session_mgr.scanned_uids.clear()
    print(f"[DEBUG] Session scanned UIDs cleared")
    
    # Start scanner if needed
    if web_handler.scanning_thread and web_handler.scanning_thread.is_alive():
        web_handler.scanning_thread.join(timeout=1.0)
    web_handler.scanning_thread = Thread(target=nfc_scan_loop_web, args=(web_handler,), daemon=True)
    web_handler.scanning_thread.start()
    
    return jsonify({'success': True})

def read_section_excel(section):
    """Read students for section from both roster file AND main database.
    Returns a list of dicts: {name,enroll,roll,subject,section,uid}
    Combines roster file + any students in database for this section.
    """
    import os
    import pandas as pd
    roster = []
    uids_seen = set()  # Track UIDs to avoid duplicates
    
    # First, read from section roster file
    path = os.path.join('data/sections', f'{section}.xlsx')
    if os.path.exists(path):
        try:
            try:
                df = pd.read_excel(path, sheet_name=section, dtype=str)
            except Exception:
                df = pd.read_excel(path, dtype=str)
            df = df.fillna('')
            # Normalize columns
            col = {c.strip().lower(): c for c in df.columns}
            for idx in range(len(df)):
                name = str(df.iloc[idx][col['name']]).strip() if 'name' in col else ''
                if not name:
                    continue
                enroll = str(df.iloc[idx][col['enrollment no']]).strip() if 'enrollment no' in col else ''
                roll = str(df.iloc[idx][col['roll no']]).strip() if 'roll no' in col else ''
                subject = str(df.iloc[idx][col['subject']]).strip() if 'subject' in col else ''
                sec = str(df.iloc[idx][col['section']]).strip() if 'section' in col else section
                uid = str(df.iloc[idx][col['uid']]).strip().upper() if 'uid' in col else ''
                if uid:
                    uids_seen.add(uid)
                roster.append({'name': name, 'enroll': enroll, 'roll': roll, 'subject': subject, 'section': sec, 'uid': uid})
        except Exception as e:
            print(f"[DEBUG] Error reading roster: {e}")
    
    # Second, check main database for students in this section that aren't in roster
    try:
        db_students = db.get_students_by_section(section)
        for student in db_students:
            # student tuple: (name, enroll_no, roll_no, section, subject, uid)
            uid = str(student[5]).strip().upper() if student[5] else ''
            if uid and uid not in uids_seen:
                # Add from database
                roster.append({
                    'name': student[0],
                    'enroll': student[1],
                    'roll': student[2],
                    'subject': student[4],
                    'section': student[3],
                    'uid': uid
                })
                uids_seen.add(uid)
    except Exception as e:
        print(f"[DEBUG] Error reading from database: {e}")
    
    return roster

@app.route('/api/session_lists')
def api_session_lists():
    # Section can come from query or current session
    section = request.args.get('section')
    if not section and session_mgr.current_session:
        section = session_mgr.current_session.get('section')
    if not section:
        return jsonify({'success': False, 'message': 'No section provided'}), 400

    # Read roster directly from Excel
    roster = read_section_excel(section)
    total = len(roster)

    # Present UIDs today for this section (from DB attendance)
    present_uids = db.get_present_uids_today_by_section(section)
    present_uid_set = set(u.upper() for u in present_uids)

    # Build waiting by excluding UIDs in present
    waiting = []
    uid_in_roster = set()
    for r in roster:
        uid = (r.get('uid') or '').upper()
        uid_in_roster.add(uid)
        if uid and uid in present_uid_set:
            continue
        waiting.append({'name': r.get('name'), 'roll_no': r.get('roll')})

    # Present list with times from DB
    from datetime import datetime as dt
    import pandas as pd
    today = (dt.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
    present_list = []
    try:
        with db.lock:
            # Read attendance file
            att_df = pd.read_excel(db.attendance_file, sheet_name='Attendance', dtype=str)
            att_df = att_df.fillna('')
            
            # Filter by today's date
            today_att = att_df[att_df['Date'].astype(str) == today]
            
            # Read students file
            stu_df = pd.read_excel(db.students_file, sheet_name='Students', dtype=str)
            stu_df = stu_df.fillna('')
            stu_df.columns = [col.strip().lower() for col in stu_df.columns]
            
            # Build map of UIDs to names for this section
            uid_to_name = {}
            for _, row in stu_df.iterrows():
                if str(row.get('section', '')).strip().upper() == section.upper():
                    uid = str(row.get('nfc uid', '')).strip()
                    name = str(row.get('name', '')).strip()
                    if uid and name:
                        uid_to_name[uid] = name
            
            # Build present list
            for _, row in today_att.iterrows():
                uid = str(row.get('Student UID', '')).strip()
                time_val = str(row.get('Time', '')).strip()
                if uid in uid_to_name:
                    present_list.append({'name': uid_to_name[uid], 'time': time_val})
    except Exception as e:
        print(f"[DEBUG] Error building present_list: {e}")
        pass

    # Last scan
    last_scan = web_handler.last_attendance or {}

    return jsonify({
        'success': True,
        'total': total,
        'present': len(present_list),
        'absent': total - len(present_list),
        'waiting': waiting,
        'present_list': present_list,
        'last_scan': last_scan,
        'meta': session_mgr.current_session
    })

@app.route('/api/reset_session', methods=['POST'])
def reset_session():
    """Reset current session - clears all attendance and makes everyone absent."""
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if not session_mgr.current_session:
        return jsonify({'success': False, 'message': 'No active session to reset'})
    
    try:
        print("[DEBUG] Resetting session - clearing all attendance...")
        
        # Clear today's attendance
        import pandas as pd
        today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
        df_att = pd.read_excel('data/attendance.xlsx', sheet_name='Attendance', dtype=str)
        df_att = df_att[df_att['Date'] != today]
        df_att.to_excel('data/attendance.xlsx', index=False, sheet_name='Attendance')
        print(f"[DEBUG] Cleared all attendance records for {today}")
        
        # Clear scanned UIDs
        session_mgr.scanned_uids.clear()
        print(f"[DEBUG] Cleared scanned UIDs")
        
        return jsonify({
            'success': True,
            'message': 'Session reset - all students now absent'
        })
    except Exception as e:
        print(f"[DEBUG] Error resetting session: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stop_session', methods=['POST'])
def stop_session():
    """Stop current session and export to PDF."""
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if not session_mgr.current_session:
        return jsonify({'success': False, 'message': 'No active session to stop'})
    
    try:
        # Stop the NFC scanner
        session_mgr.end_session()
        
        # Get session info
        section = session_mgr.current_session.get('section', 'General')
        subject = session_mgr.current_session.get('subject', 'General')
        
        # Get present students from this session
        present_students_data = []
        for uid in session_mgr.scanned_uids:
            student = db.get_student_by_uid(uid)
            if student:
                present_students_data.append(student)
        
        # Get absent students (from roster for this section)
        roster = read_section_excel(section)
        roster_uids = {r['uid'].upper() for r in roster if r['uid']}
        scanned_uids = {uid.upper() for uid in session_mgr.scanned_uids}
        absent_uids = roster_uids - scanned_uids
        
        absent_students_data = []
        for r in roster:
            if r['uid'].upper() in absent_uids:
                absent_students_data.append((r['name'], r['enroll'], r['roll'], r['section']))
        
        # Generate PDF
        pdf_filename = f"session_report_{section}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join('static/reports', pdf_filename)
        
        success = generate_session_pdf(
            session_mgr.current_session,
            present_students_data,
            absent_students_data,
            pdf_path
        )
        
        # Reset session
        session_mgr.reset_session()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session stopped and PDF exported',
                'pdf_file': pdf_filename,
                'stats': {
                    'total': len(roster),
                    'present': len(present_students_data),
                    'absent': len(absent_students_data)
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Session stopped but PDF generation failed'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/close_attendance', methods=['POST'])
def close_attendance():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if not session_mgr.current_session:
        return jsonify({'success': False, 'message': 'No active session to close'})
    
    # Get statistics
    total, present = db.get_today_stats()
    absent = total - present
    
    # Get scanned student names
    scanned_students = []
    for uid in session_mgr.scanned_uids:
        student = db.get_student_by_uid(uid)
        if student:
            scanned_students.append(student[0])
    
    # Get absent students
    absent_students_data = db.get_absent_students(list(session_mgr.scanned_uids))
    absent_students = [student[0] for student in absent_students_data]
    
    # Generate report file
    filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(f"static/reports/{filename}", 'w', encoding='utf-8') as f:
            f.write("TAP & TRACK PRO - FINAL ATTENDANCE REPORT\n")
            f.write("=" * 55 + "\n")
            f.write(f"Session: {session_mgr.current_session['name']}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Students: {total}\n")
            f.write(f"Present: {present}\n")
            f.write(f"Absent: {absent}\n")
            f.write(f"Attendance Rate: {(present/total*100) if total > 0 else 0:.1f}%\n\n")
            
            f.write("PRESENT STUDENTS:\n")
            f.write("-" * 20 + "\n")
            for i, student in enumerate(scanned_students, 1):
                f.write(f"{i}. {student}\n")
            
            f.write("\nABSENT STUDENTS:\n")
            f.write("-" * 20 + "\n")
            for i, student in enumerate(absent_students, 1):
                f.write(f"{i}. {student}\n")
    except Exception as e:
        print(f"Failed to create report file: {e}")
        filename = None
    
    # Reset session
    session_mgr.reset_session()
    voice_feedback("Attendance closed and report generated")
    
    return jsonify({
        'success': True,
        'message': 'Attendance closed successfully',
        'report': {
            'total': total,
            'present': present,
            'absent': absent,
            'present_students': scanned_students,
            'absent_students': absent_students,
            'filename': filename
        }
    })

@app.route('/api/add_student', methods=['POST'])
def add_student():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json()
    name = data.get('name', '').strip()
    enroll_no = data.get('enroll_no', '')
    roll_no = data.get('roll_no', '')
    section = data.get('section', '')
    subject = data.get('subject', '')
    uid = data.get('uid', '')
    
    if not name:
        return jsonify({'success': False, 'message': 'Student name is required'})
    
    success = db.add_student(name, enroll_no, roll_no, section, subject, uid)
    if success:
        session_mgr.scanned_uids.add(uid)
        voice_feedback(f"Student {name} added successfully")
        return jsonify({'success': True, 'message': f'Student {name} registered successfully'})
    else:
        return jsonify({'success': False, 'message': 'This NFC card is already registered!'})

@app.route('/api/get_stats')
def get_stats():
    total, present = db.get_today_stats()
    return jsonify({
        'total': total,
        'present': present,
        'absent': total - present
    })

@app.route('/api/get_students')
def get_students():
    students = db.get_all_students()
    return jsonify([{
        'name': student[0],
        'enroll_no': student[1],
        'roll_no': student[2],
        'section': student[3],
        'subject': student[4],
        'uid': student[5]
    } for student in students])

@app.route('/api/get_recent_attendance')
def get_recent_attendance():
    recent = db.get_recent_attendance(limit=10)
    return jsonify([{
        'name': item[0],
        'time': item[1]
    } for item in recent])

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'status': 'Connected to NFC Attendance System'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/api/get_status')
def get_status():
    total, present = db.get_today_stats()
    absent = total - present
    return jsonify({
        'status': web_handler.last_status,
        'last_attendance': web_handler.last_attendance,
        'stats': { 'total': total, 'present': present, 'absent': absent }
    })

@app.route('/api/scan_uid')
def api_scan_uid():
    """Block briefly and return the next detected card UID."""
    try:
        from smartcard.System import readers
        from smartcard.Exceptions import NoCardException, CardConnectionException
        import time

        timeout_seconds = 10
        start = time.time()
        GET_UIDS = [
            [0xFF, 0xCA, 0x00, 0x00, 0x00],
            [0xFF, 0xCA, 0x00, 0x00, 0x04],
            [0xFF, 0xCA, 0x00, 0x00, 0x07],
        ]

        while time.time() - start < timeout_seconds:
            try:
                rdrs = readers()
                if not rdrs:
                    time.sleep(0.3)
                    continue
                # Prefer contactless readers
                cand = [r for r in rdrs if 'contactless' in str(r).lower()]
                if not cand:
                    cand = rdrs
                for r in cand:
                    try:
                        conn = r.createConnection()
                        conn.connect()
                        for cmd in GET_UIDS:
                            try:
                                resp, sw1, sw2 = conn.transmit(cmd)
                                if sw1 == 0x90 and sw2 == 0x00 and resp:
                                    uid = ''.join(f"{b:02X}" for b in resp)
                                    try:
                                        conn.disconnect()
                                    except Exception:
                                        pass
                                    return jsonify({'success': True, 'uid': uid})
                            except Exception:
                                pass
                        try:
                            conn.disconnect()
                        except Exception:
                            pass
                    except (NoCardException, CardConnectionException):
                        pass
                    except Exception:
                        pass
                time.sleep(0.3)
            except Exception:
                time.sleep(0.3)
        return jsonify({'success': False, 'message': 'Timeout: no card scanned in 10s'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/available_sections')
def available_sections():
    import os
    os.makedirs('data/sections', exist_ok=True)
    files = [f for f in os.listdir('data/sections') if f.lower().endswith('.xlsx')]
    sections = [os.path.splitext(f)[0] for f in files]
    return jsonify({'sections': sections})

@app.route('/api/create_section_excels', methods=['POST'])
def create_section_excels():
    ensure_section_excels()
    return jsonify({'success': True})

@app.route('/api/seed_sections', methods=['POST'])
def api_seed_sections():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    try:
        seed_section_excels()
        # Automatically import all seeded sections
        summary = []
        for sec in ['A2','B2','C2','D2']:
            ok, added, skipped, err = import_section_from_excel(sec)
            if ok:
                summary.append({'section': sec, 'added': added, 'skipped': skipped})
            else:
                summary.append({'section': sec, 'error': err})
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def import_section_from_excel(section, replace=False):
    import os
    import pandas as pd
    path = os.path.join('data/sections', f'{section}.xlsx')
    if not os.path.exists(path):
        return False, 0, 0, f'Section file not found: {path}'

    # Try to read the sheet matching the section; fallback to first sheet
    try:
        df = pd.read_excel(path, sheet_name=section, dtype=str)
    except Exception:
        df = pd.read_excel(path, dtype=str)

    # Normalize columns
    df.columns = [str(c).strip() for c in df.columns]
    required_cols = {'Name','Section'}
    if not required_cols.issubset(set(df.columns)):
        return False, 0, 0, 'Excel must contain at least Name and Section columns'

    df = df.fillna('')

    added = 0
    skipped = 0

    # If replace, remove existing students (and their attendance) for this section first
    if replace:
        try:
            with db.lock:
                # Get existing UIDs in section from students file
                stu_df = pd.read_excel(db.students_file, sheet_name='Students', dtype=str)
                stu_df = stu_df.fillna('')
                uids_to_remove = set()
                for _, row in stu_df.iterrows():
                    if str(row.get('Section', '')).strip().upper() == section.upper():
                        uid = str(row.get('NFC UID', '')).strip()
                        if uid:
                            uids_to_remove.add(uid)
                
                # Remove attendance records for these UIDs
                if uids_to_remove:
                    att_df = pd.read_excel(db.attendance_file, sheet_name='Attendance', dtype=str)
                    att_df = att_df.fillna('')
                    att_df_filtered = att_df[~att_df['Student UID'].isin(uids_to_remove)]
                    att_df_filtered.to_excel(db.attendance_file, index=False, sheet_name='Attendance')
                
                # Remove students from this section
                stu_df_filtered = stu_df[stu_df['Section'].astype(str).str.strip().str.upper() != section.upper()]
                stu_df_filtered.to_excel(db.students_file, index=False, sheet_name='Students')
        except Exception as e:
            print(f"[DEBUG] Replace failed: {e}")
            pass

    for _, row in df.iterrows():
        name = str(row.get('Name') or '').strip()
        enroll = str(row.get('Enrollment No') or '').strip()
        roll = str(row.get('Roll No') or '').strip()
        subj = str(row.get('Subject') or '').strip()
        sec = str(row.get('Section') or '').strip() or section
        uid = str(row.get('UID') or '').strip().upper()
        if not name or not uid:
            skipped += 1
            continue
        ok = db.add_student(name, enroll, roll, sec, subj, uid)
        if ok:
            added += 1
    return True, added, skipped, None

@app.route('/api/import_section', methods=['POST'])
def import_section():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    data = request.get_json() or {}
    section = data.get('section')
    replace = bool(data.get('replace'))
    if not section:
        return jsonify({'success': False, 'message': 'Section is required'})
    try:
        ok, added, skipped, err = import_section_from_excel(section, replace=replace)
        if not ok:
            return jsonify({'success': False, 'message': err})
        return jsonify({'success': True, 'added': added, 'skipped': skipped})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/export_students', methods=['POST'])
def export_students():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    from datetime import datetime
    filename = f"students_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    filepath = f"static/reports/{filename}"
    
    success, message = db.export_students_to_excel(filepath)
    
    return jsonify({
        'success': success,
        'message': message,
        'filename': filename if success else None
    })

@app.route('/api/export_attendance', methods=['POST'])
def export_attendance():
    if 'authenticated' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    data = request.get_json() or {}
    date = data.get('date')  # Optional date filter
    
    from datetime import datetime
    date_str = date or datetime.now().strftime('%Y-%m-%d')
    filename = f"attendance_export_{date_str.replace('-', '')}.xlsx"
    filepath = f"static/reports/{filename}"
    
    success, message = db.export_attendance_to_excel(filepath, date)
    
    return jsonify({
        'success': success,
        'message': message,
        'filename': filename if success else None
    })

def ensure_section_excels():
    import os
    os.makedirs('data/sections', exist_ok=True)
    try:
        import pandas as pd
        templates = ['A2', 'B2', 'C2', 'D2']
        for sec in templates:
            path = os.path.join('data/sections', f'{sec}.xlsx')
            if not os.path.exists(path):
                df = pd.DataFrame(columns=['Name','Enrollment No','Roll No','Subject','Section','UID'])
                df.to_excel(path, index=False, sheet_name=sec)
    except Exception as e:
        print(f"[WARN] Could not create section templates: {e}")

def seed_section_excels():
    """Create four Excel sheets A2,B2,C2,D2 with random demo data and include the user's name in D2."""
    import os, random, string
    import pandas as pd

    os.makedirs('data/sections', exist_ok=True)

    first_names = [
        'Aarav','Vivaan','Aditya','Arjun','Vihaan','Reyansh','Muhammad','Sai','Arnav','Atharv',
        'Ishaan','Kabir','Krishna','Rudra','Rohan','Yash','Kartik','Dev','Parth','Veer'
    ]
    last_names = [
        'Sharma','Verma','Gupta','Bhardwaj','Singh','Kumar','Mehta','Patel','Agarwal','Joshi',
        'Reddy','Nair','Bose','Chopra','Kapoor','Malhotra','Pandey','Rajput','Nath','Ghosh'
    ]

    def rand_uid():
        return ''.join(random.choice('0123456789ABCDEF') for _ in range(8))

    sections = ['A2','B2','C2','D2']
    for sec in sections:
        rows = []
        used_uids = set()
        # Generate 12 students per section
        for i in range(12):
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            name = f"{fn} {ln}"
            enroll = f"{sec}{100+i:03d}"
            roll = f"{i+1}"
            subject = 'General'
            # UID unique
            uid = rand_uid()
            while uid in used_uids:
                uid = rand_uid()
            used_uids.add(uid)
            rows.append({
                'Name': name,
                'Enrollment No': enroll,
                'Roll No': roll,
                'Subject': subject,
                'Section': sec,
                'UID': uid
            })
        # Ensure user's name in D2 with known UID if available
        if sec == 'D2':
            # Try to reuse existing known UID for Aditya Bhardwaj if in DB
            try:
                # Pull last scanned or known sample UID from earlier; fallback to fixed
                user_name = 'Aditya Bhardwaj'
                known_uid = '2297951A'
                # Put at first row so it appears quickly
                rows[0] = {
                    'Name': user_name,
                    'Enrollment No': f'{sec}900',
                    'Roll No': '1',
                    'Subject': 'Major',
                    'Section': sec,
                    'UID': known_uid
                }
            except Exception:
                pass
        df = pd.DataFrame(rows, columns=['Name','Enrollment No','Roll No','Subject','Section','UID'])
        out_path = os.path.join('data/sections', f'{sec}.xlsx')
        df.to_excel(out_path, index=False, sheet_name=sec)

    return True

def generate_session_pdf(session_data, present_students, absent_students, filename):
    """Generate a professional PDF report for the session."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from datetime import datetime
        
        doc = SimpleDocTemplate(filename, pagesize=letter,
                               rightMargin=0.5*inch, leftMargin=0.5*inch,
                               topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph('NFC ATTENDANCE SYSTEM - SESSION REPORT', title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Session Info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_LEFT
        )
        
        session_info = f"""<b>Session Details:</b><br/>
        <b>Section:</b> {session_data.get('section', 'N/A')}<br/>
        <b>Subject:</b> {session_data.get('subject', 'N/A')}<br/>
        <b>Start Time:</b> {session_data.get('start_time', 'N/A')}<br/>
        <b>End Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        elements.append(Paragraph(session_info, info_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Statistics
        total = len(present_students) + len(absent_students)
        attendance_rate = (len(present_students) / total * 100) if total > 0 else 0
        
        stats_text = f"""<b>Attendance Statistics:</b><br/>
        <b>Total Students:</b> {total}<br/>
        <b>Present:</b> {len(present_students)} ({attendance_rate:.1f}%)<br/>
        <b>Absent:</b> {len(absent_students)} ({100-attendance_rate:.1f}%)
        """
        elements.append(Paragraph(stats_text, info_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Present Students Table
        elements.append(Paragraph('<b>PRESENT STUDENTS</b>', styles['Heading2']))
        if present_students:
            present_data = [['#', 'Name', 'Enrollment No', 'Roll No']]
            for i, student in enumerate(present_students, 1):
                present_data.append([str(i), student[0], student[1], student[2]])
            
            present_table = Table(present_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 0.8*inch])
            present_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            elements.append(present_table)
        else:
            elements.append(Paragraph('<i>No students present</i>', styles['Normal']))
        
        elements.append(Spacer(1, 0.3*inch))
        
        # Absent Students Table
        elements.append(Paragraph('<b>ABSENT STUDENTS</b>', styles['Heading2']))
        if absent_students:
            absent_data = [['#', 'Name', 'Enrollment No', 'Roll No']]
            for i, student in enumerate(absent_students, 1):
                absent_data.append([str(i), student[0], student[1], student[2]])
            
            absent_table = Table(absent_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 0.8*inch])
            absent_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#cc0000')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightcoral),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ffe6e6')])
            ]))
            elements.append(absent_table)
        else:
            elements.append(Paragraph('<i>All students present</i>', styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        return True
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        return False

def initialize_sections_if_empty():
    try:
        import pandas as pd
        with db.lock:
            stu_df = pd.read_excel(db.students_file, sheet_name='Students', dtype=str)
            count = len(stu_df)
        if count == 0:
            print('[INIT] No students found. Seeding and importing demo sections...')
            seed_section_excels()
            for sec in ['A2','B2','C2','D2']:
                try:
                    import_section_from_excel(sec)
                except Exception:
                    pass
    except Exception as e:
        print(f"[WARN] init sections failed: {e}")

if __name__ == '__main__':
    # Create reports directory if it doesn't exist
    import os
    os.makedirs('static/reports', exist_ok=True)
    os.makedirs('data/sections', exist_ok=True)
    ensure_section_excels()
    initialize_sections_if_empty()
    
    # Run the Flask-SocketIO app
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
