# main.py - Entry point for NFC Attendance Pro
import tkinter as tk
from tkinter import messagebox
from ui.main_window import ModernAttendanceUI

def main():
    try:
        root = tk.Tk()
        app = ModernAttendanceUI(root)
        
        # Set window icon (if available)
        try:
            root.iconbitmap("attendance_icon.ico")
        except:
            pass
            
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")

if __name__ == "__main__":
    main()