# database/manager.py - Database operations
import sqlite3
from datetime import datetime
from threading import Lock
from config import Config

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_FILE, check_same_thread=False)
        self.create_tables()
        self.lock = Lock()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS students
                                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  name TEXT NOT NULL, 
                                  enroll_no TEXT,
                                  roll_no TEXT, 
                                  uid TEXT UNIQUE NOT NULL)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS attendance
                                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                  student_uid TEXT, 
                                  date TEXT,
                                  time TEXT, 
                                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
            self.conn.execute('''CREATE TABLE IF NOT EXISTS admins
                                 (username TEXT PRIMARY KEY, 
                                  password TEXT)''')
            
            # Insert default admin if not exists
            self.conn.execute("INSERT OR IGNORE INTO admins VALUES (?, ?)", ("admin", "admin123"))

    def get_student_by_uid(self, uid):
        with self.lock:
            cursor = self.conn.execute("SELECT name, enroll_no, roll_no FROM students WHERE uid=?", (uid,))
            return cursor.fetchone()

    def add_student(self, name, enroll_no, roll_no, uid):
        with self.lock:
            try:
                self.conn.execute("INSERT INTO students (name, enroll_no, roll_no, uid) VALUES (?, ?, ?, ?)",
                                (name, enroll_no, roll_no, uid))
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # UID already exists

    def log_attendance(self, uid):
        now = datetime.utcnow() + Config.TIMEZONE_OFFSET
        date = now.strftime("%Y-%m-%d")
        t = now.strftime("%H:%M:%S")
        with self.lock:
            self.conn.execute("INSERT INTO attendance (student_uid, date, time) VALUES (?, ?, ?)",
                            (uid, date, t))
            self.conn.commit()

    def get_today_stats(self):
        with self.lock:
            today = (datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d")
            total = self.conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] or 0
            present = self.conn.execute("SELECT COUNT(DISTINCT student_uid) FROM attendance WHERE date=?",
                                      (today,)).fetchone()[0] or 0
            return total, present

    def authenticate_admin(self, username, password):
        with self.lock:
            cursor = self.conn.execute("SELECT password FROM admins WHERE username=?", (username,))
            row = cursor.fetchone()
            return row and row[0] == password

    def get_recent_attendance(self, limit=10):
        with self.lock:
            cursor = self.conn.execute('''
                SELECT s.name, a.time 
                FROM attendance a 
                JOIN students s ON a.student_uid = s.uid 
                WHERE a.date = ? 
                ORDER BY a.timestamp DESC 
                LIMIT ?
            ''', ((datetime.utcnow() + Config.TIMEZONE_OFFSET).strftime("%Y-%m-%d"), limit))
            return cursor.fetchall()

    def get_all_students(self):
        with self.lock:
            cursor = self.conn.execute("SELECT name, enroll_no, roll_no, uid FROM students ORDER BY name")
            return cursor.fetchall()

    def get_absent_students(self, present_uids):
        """Get list of students who are absent (not in present_uids)"""
        with self.lock:
            if not present_uids:
                # If no students are present, all are absent
                return self.get_all_students()
            
            placeholders = ','.join('?' * len(present_uids))
            query = f"SELECT name, enroll_no, roll_no, uid FROM students WHERE uid NOT IN ({placeholders}) ORDER BY name"
            cursor = self.conn.execute(query, present_uids)
            return cursor.fetchall()