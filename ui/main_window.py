# ui/main_window.py - Main GUI class with Close Attendance feature
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from threading import Thread
from datetime import datetime

from config import Config
from database import db
from models import session_mgr, voice_feedback
from nfc import nfc_scan_loop
from .components import ModernButton, ModernCard, DigitalDisplay

class ModernAttendanceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Tap & Track Pro - NFC Attendance System")
        self.root.geometry("1200x700")
        self.root.configure(bg=Config.GUI_BG)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Make window slightly transparent for modern look
        self.root.attributes('-alpha', 0.95)
        
        self.setup_styles()
        self.create_main_layout()
        self.scan_thread = None

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('Modern.TFrame', background=Config.GUI_BG)
        self.style.configure('Card.TFrame', background=Config.GUI_CARD_BG)

    def create_main_layout(self):
        # Header with gradient effect
        header_frame = tk.Frame(self.root, bg=Config.GUI_BG, height=100)
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)
        
        # Main title with icon
        title_frame = tk.Frame(header_frame, bg=Config.GUI_BG)
        title_frame.pack(side='left', fill='y')
        
        tk.Label(
            title_frame, 
            text="🎨", 
            font=("Segoe UI Emoji", 32),
            bg=Config.GUI_BG, 
            fg=Config.GUI_ACCENT
        ).pack(side='left')
        
        tk.Label(
            title_frame, 
            text="Tap & Track Pro", 
            font=(Config.GUI_FONT_PRIMARY, 28, 'bold'),
            bg=Config.GUI_BG, 
            fg=Config.GUI_ACCENT
        ).pack(side='left', padx=(10, 0))
        
        tk.Label(
            title_frame,
            text="NFC Attendance Management System",
            font=(Config.GUI_FONT_PRIMARY, 12),
            bg=Config.GUI_BG,
            fg=Config.GUI_TEXT_SECONDARY
        ).pack(side='left', padx=(20, 0))
        
        # Status indicator
        status_frame = tk.Frame(header_frame, bg=Config.GUI_BG)
        status_frame.pack(side='right', fill='y')
        
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=(Config.GUI_FONT_PRIMARY, 24),
            bg=Config.GUI_BG,
            fg=Config.GUI_WARNING
        )
        self.status_indicator.pack(side='top')
        
        self.status_label = tk.Label(
            status_frame,
            text="System Ready",
            font=(Config.GUI_FONT_PRIMARY, 10),
            bg=Config.GUI_BG,
            fg=Config.GUI_TEXT_SECONDARY
        )
        self.status_label.pack(side='top')
        
        # Main content area
        main_container = tk.Frame(self.root, bg=Config.GUI_BG)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - Stats and Controls (40% width)
        left_panel = ModernCard(main_container, title="📊 DASHBOARD")
        left_panel.pack(side='left', fill='both', expand=False, padx=(0, 10), ipadx=10)
        left_panel.config(width=400)
        
        # Right panel - Recent Activity (60% width)
        right_panel = ModernCard(main_container, title="🕒 RECENT ACTIVITY")
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.setup_left_panel(left_panel)
        self.setup_right_panel(right_panel)
        
        # Initialize dashboard
        self.update_dashboard()

    def setup_left_panel(self, parent):
        # Statistics in a grid layout
        stats_frame = tk.Frame(parent, bg=Config.GUI_CARD_BG)
        stats_frame.pack(fill='x', padx=20, pady=20)
        
        # Total Students Card
        total_card = ModernCard(stats_frame, title="TOTAL STUDENTS")
        total_card.pack(fill='x', pady=(0, 15))
        
        self.total_display = DigitalDisplay(total_card, text="0")
        self.total_display.pack(pady=10)
        
        # Present Today Card
        present_card = ModernCard(stats_frame, title="PRESENT TODAY")
        present_card.pack(fill='x', pady=(0, 15))
        
        self.present_display = DigitalDisplay(present_card, text="0")
        self.present_display.pack(pady=10)
        
        # Absent Today Card
        absent_card = ModernCard(stats_frame, title="ABSENT TODAY")
        absent_card.pack(fill='x', pady=(0, 15))
        
        self.absent_display = DigitalDisplay(absent_card, text="0")
        self.absent_display.pack(pady=10)
        
        # Session Controls
        control_frame = tk.Frame(parent, bg=Config.GUI_CARD_BG)
        control_frame.pack(fill='x', padx=20, pady=10)
        
        self.start_btn = ModernButton(
            control_frame, 
            text="🚀 START ATTENDANCE SESSION", 
            command=self.start_session,
            bg=Config.GUI_SUCCESS,
            fg=Config.GUI_TEXT
        )
        self.start_btn.pack(fill='x', pady=5)
        
        self.end_btn = ModernButton(
            control_frame, 
            text="🛑 END SESSION", 
            command=self.end_session,
            bg=Config.GUI_ERROR,
            fg=Config.GUI_TEXT
        )
        self.end_btn.pack(fill='x', pady=5)
        
        # NEW: Close Attendance Button
        self.close_btn = ModernButton(
            control_frame, 
            text="📋 CLOSE ATTENDANCE & REPORT", 
            command=self.close_attendance,
            bg=Config.GUI_WARNING,
            fg=Config.GUI_TEXT
        )
        self.close_btn.pack(fill='x', pady=5)
        
        # Quick Actions
        action_frame = tk.Frame(parent, bg=Config.GUI_CARD_BG)
        action_frame.pack(fill='x', padx=20, pady=20)
        
        ModernButton(
            action_frame, 
            text="👥 MANAGE STUDENTS", 
            command=self.manage_students,
            bg=Config.GUI_ACCENT,
            fg=Config.GUI_TEXT
        ).pack(fill='x', pady=2)
        
        ModernButton(
            action_frame, 
            text="📊 VIEW REPORTS", 
            command=self.view_reports,
            bg=Config.GUI_ACCENT,
            fg=Config.GUI_TEXT
        ).pack(fill='x', pady=2)
        
        ModernButton(
            action_frame, 
            text="⚙️ ADMIN SETTINGS", 
            command=self.admin_settings,
            bg=Config.GUI_WARNING,
            fg=Config.GUI_TEXT
        ).pack(fill='x', pady=2)

    def setup_right_panel(self, parent):
        # Activity frame with scrollbar
        activity_container = tk.Frame(parent, bg=Config.GUI_CARD_BG)
        activity_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create a canvas and scrollbar for the activity list
        canvas = tk.Canvas(activity_container, bg=Config.GUI_CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(activity_container, orient="vertical", command=canvas.yview)
        self.activity_list = tk.Frame(canvas, bg=Config.GUI_CARD_BG)
        
        self.activity_list.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.activity_list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Placeholder for activity items
        self.no_activity_label = tk.Label(
            self.activity_list,
            text="No recent activity\n\nTap NFC cards to see attendance records here",
            font=(Config.GUI_FONT_PRIMARY, 11),
            bg=Config.GUI_CARD_BG,
            fg=Config.GUI_TEXT_SECONDARY,
            justify='center'
        )
        self.no_activity_label.pack(pady=50)

    def update_status(self, msg, success=False, warning=False, error=False):
        self.status_label.config(text=msg)
        
        if success:
            color = Config.GUI_SUCCESS
        elif warning:
            color = Config.GUI_WARNING
        elif error:
            color = Config.GUI_ERROR
        else:
            color = Config.GUI_ACCENT
            
        self.status_label.config(fg=color)
        self.status_indicator.config(fg=color)

    def update_dashboard(self):
        try:
            total, present = db.get_today_stats()
            absent = total - present
            
            self.total_display.config(text=str(total))
            self.present_display.config(text=str(present))
            self.absent_display.config(text=str(absent))
            
            # Update display colors based on status
            self.present_display.config(fg=Config.GUI_SUCCESS if present > 0 else Config.GUI_TEXT_SECONDARY)
            self.absent_display.config(fg=Config.GUI_ERROR if absent > 0 else Config.GUI_TEXT_SECONDARY)
            
        except Exception as e:
            print(f"Dashboard update error: {e}")
        
        self.root.after(3000, self.update_dashboard)

    def add_recent_activity(self, name, time_str):
        if hasattr(self, 'no_activity_label') and self.no_activity_label.winfo_exists():
            self.no_activity_label.destroy()
        
        activity_item = ModernCard(self.activity_list)
        activity_item.pack(fill='x', pady=5, padx=5)
        
        content_frame = tk.Frame(activity_item, bg=Config.GUI_CARD_BG)
        content_frame.pack(fill='x', padx=10, pady=8)
        
        icon_label = tk.Label(
            content_frame,
            text="🎯",
            font=("Segoe UI Emoji", 14),
            bg=Config.GUI_CARD_BG,
            fg=Config.GUI_SUCCESS
        )
        icon_label.pack(side='left', padx=(0, 10))
        
        name_label = tk.Label(
            content_frame,
            text=name,
            font=(Config.GUI_FONT_PRIMARY, 11, 'bold'),
            bg=Config.GUI_CARD_BG,
            fg=Config.GUI_TEXT
        )
        name_label.pack(side='left', fill='x', expand=True)
        
        time_label = tk.Label(
            content_frame,
            text=time_str,
            font=(Config.GUI_FONT_PRIMARY, 10),
            bg=Config.GUI_CARD_BG,
            fg=Config.GUI_TEXT_SECONDARY
        )
        time_label.pack(side='right')
        
        if len(self.activity_list.winfo_children()) > 15:
            self.activity_list.winfo_children()[0].destroy()

    def add_recent_attendance(self, name):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.add_recent_activity(name, time_str)

    def show_add_student_dialog(self, uid):
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Register New Student")
        dialog.geometry("450x400")
        dialog.configure(bg=Config.GUI_BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.geometry(f"+{self.root.winfo_x()+200}+{self.root.winfo_y()+100}")
        
        header_frame = tk.Frame(dialog, bg=Config.GUI_BG)
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🎓 New Student Registration",
            font=(Config.GUI_FONT_PRIMARY, 18, 'bold'),
            bg=Config.GUI_BG,
            fg=Config.GUI_ACCENT
        ).pack()
        
        tk.Label(
            header_frame,
            text=f"NFC Card Detected: {uid}",
            font=(Config.GUI_FONT_SECONDARY, 10),
            bg=Config.GUI_BG,
            fg=Config.GUI_TEXT_SECONDARY
        ).pack(pady=(5, 0))
        
        form_frame = ModernCard(dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(form_frame, text="Full Name *", bg=Config.GUI_CARD_BG, fg=Config.GUI_TEXT, 
                font=(Config.GUI_FONT_PRIMARY, 10, 'bold')).pack(anchor='w', pady=(15, 5))
        name_var = tk.StringVar()
        name_entry = tk.Entry(form_frame, textvariable=name_var, font=(Config.GUI_FONT_PRIMARY, 11),
                             bg="#2a2a4a", fg=Config.GUI_TEXT, insertbackground=Config.GUI_ACCENT)
        name_entry.pack(fill='x', padx=10, pady=2, ipady=5)
        name_entry.focus()
        
        tk.Label(form_frame, text="Enrollment No", bg=Config.GUI_CARD_BG, fg=Config.GUI_TEXT,
                font=(Config.GUI_FONT_PRIMARY, 10, 'bold')).pack(anchor='w', pady=(15, 5))
        enroll_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=enroll_var, font=(Config.GUI_FONT_PRIMARY, 11),
                bg="#2a2a4a", fg=Config.GUI_TEXT, insertbackground=Config.GUI_ACCENT).pack(fill='x', padx=10, pady=2, ipady=5)
        
        tk.Label(form_frame, text="Roll No", bg=Config.GUI_CARD_BG, fg=Config.GUI_TEXT,
                font=(Config.GUI_FONT_PRIMARY, 10, 'bold')).pack(anchor='w', pady=(15, 5))
        roll_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=roll_var, font=(Config.GUI_FONT_PRIMARY, 11),
                bg="#2a2a4a", fg=Config.GUI_TEXT, insertbackground=Config.GUI_ACCENT).pack(fill='x', padx=10, pady=2, ipady=5)
        
        def save_student():
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter student name", parent=dialog)
                name_entry.focus()
                return
                
            success = db.add_student(name, enroll_var.get(), roll_var.get(), uid)
            if success:
                session_mgr.scanned_uids.add(uid)
                voice_feedback(f"Student {name} added successfully")
                self.update_status(f"✅ Student registered: {name}", success=True)
                self.update_dashboard()
                self.add_recent_activity(f"Registered: {name}", "Now")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "This NFC card is already registered!", parent=dialog)

        btn_frame = tk.Frame(form_frame, bg=Config.GUI_CARD_BG)
        btn_frame.pack(fill='x', padx=10, pady=20)
        
        ModernButton(
            btn_frame, 
            text="💾 Save Student", 
            command=save_student,
            bg=Config.GUI_SUCCESS
        ).pack(side='right', padx=(10, 0))
        
        ModernButton(
            btn_frame, 
            text="❌ Cancel", 
            command=dialog.destroy,
            bg=Config.GUI_ERROR
        ).pack(side='right')
        
        dialog.bind('<Return>', lambda e: save_student())

    def start_session(self):
        username = simpledialog.askstring("Admin Login", "Username:", parent=self.root)
        if not username:
            return
            
        password = simpledialog.askstring("Admin Login", "Password:", show="*", parent=self.root)
        if not password:
            return
            
        if not db.authenticate_admin(username, password):
            messagebox.showerror("Authentication Failed", "Invalid admin credentials!", parent=self.root)
            return
            
        session_mgr.start_session(name=f"Session by {username}")
        self.update_status("🚀 Session started - Ready for scanning", success=True)
        voice_feedback("Session started. Ready for scanning.")
        
        if self.scan_thread and self.scan_thread.is_alive():
            self.scan_thread.join(timeout=1.0)
            
        self.scan_thread = Thread(target=nfc_scan_loop, args=(self,), daemon=True)
        self.scan_thread.start()

    def end_session(self):
        session_mgr.end_session()
        self.update_status("🛑 Session ended", warning=True)
        voice_feedback("Session ended")
        
        total, present = db.get_today_stats()
        messagebox.showinfo(
            "Session Summary", 
            f"Session completed!\n\n📊 Attendance Summary:\n• Total Students: {total}\n• Present Today: {present}\n• Absent: {total - present}",
            parent=self.root
        )

    # NEW: Close Attendance Method
    def close_attendance(self):
        """Close attendance session and generate final report"""
        if not session_mgr.current_session:
            messagebox.showwarning("No Active Session", "There is no active attendance session to close!", parent=self.root)
            return
        
        # Admin authentication
        username = simpledialog.askstring("Admin Login", "Username:", parent=self.root)
        if not username:
            return
            
        password = simpledialog.askstring("Admin Login", "Password:", show="*", parent=self.root)
        if not password:
            return
            
        if not db.authenticate_admin(username, password):
            messagebox.showerror("Authentication Failed", "Invalid admin credentials!", parent=self.root)
            return
        
        # Get statistics
        total, present = db.get_today_stats()
        absent = total - present
        
        # Get scanned student names
        scanned_students = []
        for uid in session_mgr.scanned_uids:
            student = db.get_student_by_uid(uid)
            if student:
                scanned_students.append(student[0])
        
        # Generate comprehensive report
        report_summary = f"""
📊 FINAL ATTENDANCE REPORT
──────────────────────────
Session: {session_mgr.current_session['name']}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Total Students: {total}
Present: {present}
Absent: {absent}
Attendance Rate: {(present/total*100) if total > 0 else 0:.1f}%

PRESENT STUDENTS ({len(scanned_students)}):
"""
        
        for i, student_name in enumerate(scanned_students, 1):
            report_summary += f"{i}. {student_name}\n"
        
        # Get absent students
        absent_students_data = db.get_absent_students(list(session_mgr.scanned_uids))
        if absent_students_data:
            report_summary += f"\nABSENT STUDENTS ({len(absent_students_data)}):\n"
            for i, student in enumerate(absent_students_data, 1):
                report_summary += f"{i}. {student[0]}\n"  # student[0] is name
        
        # Show final report
        messagebox.showinfo(
            "📋 Attendance Closed - Final Report", 
            report_summary,
            parent=self.root
        )
        
        # Export to file
        self.export_attendance_report(total, present, absent, scanned_students, absent_students_data)
        
        # Reset session
        session_mgr.reset_session()
        self.update_status("📋 Attendance closed - Report generated", success=True)
        voice_feedback("Attendance closed and report generated")
        self.update_dashboard()

    def export_attendance_report(self, total, present, absent, scanned_students, absent_students):
        """Export attendance report to a text file"""
        try:
            filename = f"attendance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
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
                    f.write(f"{i}. {student[0]}\n")  # student[0] is name
            
            messagebox.showinfo(
                "Report Exported", 
                f"Attendance report exported to:\n{filename}",
                parent=self.root
            )
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}", parent=self.root)

    def manage_students(self):
        manage_dialog = tk.Toplevel(self.root)
        manage_dialog.title("👥 Student Management")
        manage_dialog.geometry("600x400")
        manage_dialog.configure(bg=Config.GUI_BG)
        manage_dialog.transient(self.root)
        
        tk.Label(
            manage_dialog,
            text="Student Database",
            font=(Config.GUI_FONT_PRIMARY, 16, 'bold'),
            bg=Config.GUI_BG,
            fg=Config.GUI_ACCENT
        ).pack(pady=10)
        
        tree_frame = ModernCard(manage_dialog)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        columns = ("Name", "Enrollment", "Roll No", "UID")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        students = db.get_all_students()
        for student in students:
            tree.insert("", "end", values=student)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def view_reports(self):
        messagebox.showinfo(
            "Reports", 
            "📈 Reporting Features:\n\n• Daily attendance reports\n• Monthly analytics\n• Student-wise reports\n• Export to Excel/PDF\n\nThis feature will be available in the next update!",
            parent=self.root
        )

    def admin_settings(self):
        messagebox.showinfo(
            "Admin Settings", 
            "⚙️ Admin Features:\n\n• Change admin password\n• System configuration\n• Database management\n• Backup & restore\n\nThis feature will be available in the next update!",
            parent=self.root
        )