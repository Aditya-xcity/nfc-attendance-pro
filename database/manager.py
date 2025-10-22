# database/manager.py - Excel-based database operations
import pandas as pd
import os
from datetime import datetime
from threading import Lock
from config import Config

class ExcelDatabaseManager:
    def __init__(self):
        self.lock = Lock()
        self.students_file = "data/students.xlsx"
        self.attendance_file = "data/attendance.xlsx"
        self.ensure_files_exist()

    def ensure_files_exist(self):
        """Create Excel files if they don't exist"""
        os.makedirs("data", exist_ok=True)
        
        # Create students file
        if not os.path.exists(self.students_file):
            df = pd.DataFrame(columns=['Name', 'Enrollment No', 'Roll No', 'Section', 'Subject', 'NFC UID'])
            df.to_excel(self.students_file, index=False, sheet_name='Students')
            print(f"[DEBUG] Created {self.students_file}")
        
        # Create attendance file
        if not os.path.exists(self.attendance_file):
            df = pd.DataFrame(columns=['Student UID', 'Date', 'Time', 'Timestamp'])
            df.to_excel(self.attendance_file, index=False, sheet_name='Attendance')
            print(f"[DEBUG] Created {self.attendance_file}")

    def get_student_by_uid(self, uid):
        """Get student by NFC UID"""
        with self.lock:
            try:
                df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                df = df.fillna('')
                # Normalize column names
                df.columns = [col.strip().lower() for col in df.columns]
                
                for _, row in df.iterrows():
                    if str(row.get('nfc uid', '')).strip().upper() == uid.upper():
                        return (
                            row.get('name', ''),
                            row.get('enrollment no', ''),
                            row.get('roll no', ''),
                            row.get('section', ''),
                            row.get('subject', '')
                        )
                return None
            except Exception as e:
                print(f"[DEBUG] Error in get_student_by_uid: {e}")
                return None

    def add_student(self, name, enroll_no, roll_no, section, subject, uid):
        """Add new student to Excel"""
        with self.lock:
            try:
                df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                df = df.fillna('')
                
                # Check if UID already exists
                df_normalized = df.copy()
                df_normalized.columns = [col.strip().lower() for col in df_normalized.columns]
                for _, row in df_normalized.iterrows():
                    if str(row.get('nfc uid', '')).strip().upper() == uid.upper():
                        print(f"[DEBUG] UID already exists: {uid}")
                        return False
                
                # Add new row
                new_row = {
                    'Name': name,
                    'Enrollment No': enroll_no,
                    'Roll No': roll_no,
                    'Section': section,
                    'Subject': subject,
                    'NFC UID': uid
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(self.students_file, index=False, sheet_name='Students')
                print(f"[DEBUG] Added student: {name} with UID: {uid}")
                return True
            except Exception as e:
                print(f"[DEBUG] Error in add_student: {e}")
                return False

    def log_attendance(self, uid):
        """Log attendance for a student"""
        with self.lock:
            try:
                now = datetime.utcnow() + Config.TIMEZONE_OFFSET
                date = now.strftime("%Y-%m-%d")
                time_str = now.strftime("%H:%M:%S")
                timestamp = now.isoformat()
                
                df = pd.read_excel(self.attendance_file, sheet_name='Attendance', dtype=str)
                df = df.fillna('')
                
                new_row = {
                    'Student UID': uid,
                    'Date': date,
                    'Time': time_str,
                    'Timestamp': timestamp
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(self.attendance_file, index=False, sheet_name='Attendance')
                print(f"[DEBUG] Logged attendance for UID: {uid}")
            except Exception as e:
                print(f"[DEBUG] Error in log_attendance: {e}")

    def get_today_stats(self):
        """Get today's attendance statistics"""
        with self.lock:
            try:
                today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
                
                # Total students
                students_df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                total = len(students_df)
                
                # Present today
                attendance_df = pd.read_excel(self.attendance_file, sheet_name='Attendance', dtype=str)
                attendance_df = attendance_df.fillna('')
                today_attendance = attendance_df[attendance_df['Date'].astype(str) == today]
                present = len(today_attendance['Student UID'].unique())
                
                return total, present
            except Exception as e:
                print(f"[DEBUG] Error in get_today_stats: {e}")
                return 0, 0

    def authenticate_admin(self, username, password):
        """Authenticate admin (hardcoded for now)"""
        # In a real app, store this in a separate file or use environment variables
        return username == "admin" and password == "admin123"

    def get_recent_attendance(self, limit=10):
        """Get recent attendance records"""
        with self.lock:
            try:
                today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
                
                attendance_df = pd.read_excel(self.attendance_file, sheet_name='Attendance', dtype=str)
                students_df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                
                attendance_df = attendance_df.fillna('')
                students_df = students_df.fillna('')
                
                # Get today's attendance
                today_attendance = attendance_df[attendance_df['Date'].astype(str) == today].copy()
                
                # Join with students to get names
                students_df_lower = students_df.copy()
                students_df_lower.columns = [col.strip().lower() for col in students_df_lower.columns]
                today_attendance_lower = today_attendance.copy()
                today_attendance_lower.columns = [col.strip().lower() for col in today_attendance_lower.columns]
                
                result = []
                for _, att_row in today_attendance_lower.iloc[-limit:].iterrows():
                    uid = str(att_row.get('student uid', '')).strip()
                    time_val = str(att_row.get('time', '')).strip()
                    
                    # Find student name
                    for _, stu_row in students_df_lower.iterrows():
                        if str(stu_row.get('nfc uid', '')).strip().upper() == uid.upper():
                            result.append((stu_row.get('name', 'Unknown'), time_val))
                            break
                
                return result[::-1]  # Most recent first
            except Exception as e:
                print(f"[DEBUG] Error in get_recent_attendance: {e}")
                return []

    def get_all_students(self):
        """Get all students"""
        with self.lock:
            try:
                df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                df = df.fillna('')
                
                result = []
                for _, row in df.iterrows():
                    result.append((
                        row.get('Name', ''),
                        row.get('Enrollment No', ''),
                        row.get('Roll No', ''),
                        row.get('Section', ''),
                        row.get('Subject', ''),
                        row.get('NFC UID', '')
                    ))
                return result
            except Exception as e:
                print(f"[DEBUG] Error in get_all_students: {e}")
                return []

    def get_students_by_section(self, section):
        """Get students by section"""
        with self.lock:
            try:
                df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                df = df.fillna('')
                
                result = []
                for _, row in df.iterrows():
                    if str(row.get('Section', '')).strip().upper() == section.upper():
                        result.append((
                            row.get('Name', ''),
                            row.get('Enrollment No', ''),
                            row.get('Roll No', ''),
                            row.get('Section', ''),
                            row.get('Subject', ''),
                            row.get('NFC UID', '')
                        ))
                return result
            except Exception as e:
                print(f"[DEBUG] Error in get_students_by_section: {e}")
                return []

    def get_present_uids_today(self):
        """Get all UIDs present today"""
        with self.lock:
            try:
                today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
                
                attendance_df = pd.read_excel(self.attendance_file, sheet_name='Attendance', dtype=str)
                attendance_df = attendance_df.fillna('')
                
                today_attendance = attendance_df[attendance_df['Date'].astype(str) == today]
                uids = set(today_attendance['Student UID'].unique())
                return uids
            except Exception as e:
                print(f"[DEBUG] Error in get_present_uids_today: {e}")
                return set()

    def get_present_uids_today_by_section(self, section):
        """Get UIDs present today for a specific section"""
        with self.lock:
            try:
                today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
                
                attendance_df = pd.read_excel(self.attendance_file, sheet_name='Attendance', dtype=str)
                students_df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                
                attendance_df = attendance_df.fillna('')
                students_df = students_df.fillna('')
                
                # Get students in section
                section_uids = set()
                for _, row in students_df.iterrows():
                    if str(row.get('Section', '')).strip().upper() == section.upper():
                        section_uids.add(str(row.get('NFC UID', '')).strip())
                
                # Get today's attendance
                today_attendance = attendance_df[attendance_df['Date'].astype(str) == today]
                present_uids = set(today_attendance['Student UID'].unique())
                
                # Intersection
                return present_uids & section_uids
            except Exception as e:
                print(f"[DEBUG] Error in get_present_uids_today_by_section: {e}")
                return set()

    def get_absent_students(self, present_uids):
        """Get absent students (not in present_uids)"""
        with self.lock:
            try:
                df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                df = df.fillna('')
                
                if not present_uids:
                    # All students are absent
                    result = []
                    for _, row in df.iterrows():
                        result.append((
                            row.get('Name', ''),
                            row.get('Enrollment No', ''),
                            row.get('Roll No', ''),
                            row.get('Section', ''),
                            row.get('Subject', ''),
                            row.get('NFC UID', '')
                        ))
                    return result
                
                # Find absent students
                result = []
                for _, row in df.iterrows():
                    uid = str(row.get('NFC UID', '')).strip()
                    if uid not in present_uids and uid:
                        result.append((
                            row.get('Name', ''),
                            row.get('Enrollment No', ''),
                            row.get('Roll No', ''),
                            row.get('Section', ''),
                            row.get('Subject', ''),
                            uid
                        ))
                return result
            except Exception as e:
                print(f"[DEBUG] Error in get_absent_students: {e}")
                return []

    def get_all_students_dict(self):
        """Get all students as list of dictionaries"""
        students_tuples = self.get_all_students()
        result = []
        for student in students_tuples:
            result.append({
                'name': student[0],
                'enroll_no': student[1],
                'roll_no': student[2],
                'section': student[3],
                'subject': student[4],
                'uid': student[5]
            })
        return result
    
    def get_students_by_section_dict(self, section):
        """Get students by section as list of dictionaries"""
        students_tuples = self.get_students_by_section(section)
        result = []
        for student in students_tuples:
            result.append({
                'name': student[0],
                'enroll_no': student[1],
                'roll_no': student[2],
                'section': student[3],
                'subject': student[4],
                'uid': student[5]
            })
        return result

    def export_students_to_excel(self, filename):
        """Export all students data to Excel file"""
        with self.lock:
            try:
                df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                if len(df) == 0:
                    return False, "No students to export"
                
                df.to_excel(filename, index=False, sheet_name='Students')
                return True, f"Exported {len(df)} students to {filename}"
            except Exception as e:
                return False, f"Export failed: {str(e)}"

    def export_attendance_to_excel(self, filename, date=None):
        """Export attendance data to Excel file"""
        with self.lock:
            try:
                if not date:
                    date = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
                
                attendance_df = pd.read_excel(self.attendance_file, sheet_name='Attendance', dtype=str)
                students_df = pd.read_excel(self.students_file, sheet_name='Students', dtype=str)
                
                attendance_df = attendance_df.fillna('')
                students_df = students_df.fillna('')
                
                # Filter by date
                today_attendance = attendance_df[attendance_df['Date'].astype(str) == date]
                if len(today_attendance) == 0:
                    return False, f"No attendance data for {date}"
                
                # Join with students
                students_df.columns = [col.strip().lower() for col in students_df.columns]
                today_attendance_lower = today_attendance.copy()
                today_attendance_lower.columns = [col.strip().lower() for col in today_attendance_lower.columns]
                
                result = []
                for _, att_row in today_attendance_lower.iterrows():
                    uid = str(att_row.get('student uid', '')).strip()
                    for _, stu_row in students_df.iterrows():
                        if str(stu_row.get('nfc uid', '')).strip().upper() == uid.upper():
                            result.append({
                                'Name': stu_row.get('name', ''),
                                'Enrollment No': stu_row.get('enrollment no', ''),
                                'Roll No': stu_row.get('roll no', ''),
                                'Section': stu_row.get('section', ''),
                                'Subject': stu_row.get('subject', ''),
                                'Time': att_row.get('time', ''),
                                'Date': att_row.get('date', '')
                            })
                            break
                
                if not result:
                    return False, f"No attendance data for {date}"
                
                df_export = pd.DataFrame(result)
                df_export.to_excel(filename, index=False, sheet_name='Attendance')
                return True, f"Exported {len(result)} attendance records to {filename}"
            except Exception as e:
                return False, f"Export failed: {str(e)}"
