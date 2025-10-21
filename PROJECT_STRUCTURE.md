# NFC Attendance System - Project Structure

## Directory Layout

```
nfc_aditya/
│
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── LICENSE                         # License file
├── .gitignore                      # Git ignore file
│
├── FEATURE_STOP_SESSION_PDF.md     # Stop session & PDF feature documentation
├── PROJECT_STRUCTURE.md            # This file
│
├── data/                           # Data directory
│   ├── students.xlsx               # Main student database (Excel)
│   ├── attendance.xlsx             # Attendance records (Excel)
│   └── sections/                   # Section rosters
│       ├── A2.xlsx                 # Section A2 roster
│       ├── B2.xlsx                 # Section B2 roster
│       ├── C2.xlsx                 # Section C2 roster
│       └── D2.xlsx                 # Section D2 roster
│
├── database/                       # Database manager
│   ├── __init__.py                 # Module initialization
│   └── manager.py                  # Excel-based database operations
│
├── models/                         # Data models
│   ├── __init__.py                 # Module initialization
│   ├── session.py                  # Session management
│   └── voice.py                    # Voice feedback
│
├── nfc/                            # NFC scanner module
│   ├── __init__.py                 # Module initialization
│   └── broadcom_scanner.py         # Broadcom NFC reader interface
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css               # Stylesheet
│   ├── js/
│   │   └── class_session.js        # Frontend JavaScript
│   └── reports/                    # Generated PDF reports
│       └── session_report_*.pdf    # Session attendance reports
│
├── templates/                      # HTML templates
│   ├── login.html                  # Login page
│   ├── class_session.html          # Class session page
│   └── students.html               # Students management page
│
└── utils/                          # Utilities
    ├── __init__.py                 # Module initialization
    └── helpers.py                  # Helper functions
```

## Files Deleted (Cleanup)

The following unnecessary files were removed:
- ❌ `simple_web_test.py` - Old test file
- ❌ `test_attendance_flow.py` - Old test file
- ❌ `test_nfc_read.py` - Old test file
- ❌ `web_main.py` - Old alternate entry point
- ❌ `tempCodeRunnerFile.py` - VSCode temp files
- ❌ `Attendance.xlsx` - Old data file
- ❌ `DATA.xlsx` - Old data file
- ❌ `__pycache__/` directories - Python cache files

## Core Files

### Application Files
- **app.py** - Main Flask application with all endpoints
- **config.py** - Configuration (colors, timezone, delays)
- **requirements.txt** - Python dependencies

### Data Layer
- **database/manager.py** - Excel-based database operations
- **data/students.xlsx** - Student records
- **data/attendance.xlsx** - Daily attendance logs
- **data/sections/*.xlsx** - Section rosters for import

### Business Logic
- **models/session.py** - Session management
- **models/voice.py** - Voice feedback system
- **nfc/broadcom_scanner.py** - NFC card scanning

### Frontend
- **templates/*.html** - Web pages (login, session, students)
- **static/css/style.css** - Styling
- **static/js/class_session.js** - Frontend logic
- **static/reports/** - Generated PDF reports

## Data Files

### Excel Files (Stored in `data/`)
1. **students.xlsx** - Master student database
   - Columns: Name, Enrollment No, Roll No, Section, Subject, NFC UID
   - Auto-updated when new students are added

2. **attendance.xlsx** - Daily attendance records
   - Columns: Student UID, Date, Time, Timestamp
   - Populated during NFC scanning

3. **sections/*.xlsx** - Section rosters
   - Used for bulk student import
   - Can be updated manually
   - Auto-synced with main database

## Key Features

✅ **NFC Scanning** - Real-time card detection and logging  
✅ **Excel Storage** - No database required, data in Excel files  
✅ **Session Management** - Start/stop attendance sessions  
✅ **PDF Reports** - Auto-generate session attendance reports  
✅ **Auto-Sync** - Database students appear in sessions automatically  
✅ **Multi-Section** - Support for A2, B2, C2, D2 sections  
✅ **Statistics** - Real-time stats and analytics  

## Dependencies

See `requirements.txt`:
```
pyscard==2.0.4          # NFC reader interface
pyttsx3==2.90           # Text-to-speech
flask==2.3.2            # Web framework
flask-socketio==5.3.5   # Real-time updates
pandas==2.0.3           # Excel data handling
openpyxl==3.1.2         # Excel file operations
reportlab==4.0.4        # PDF generation
```

## How to Run

```powershell
# Install dependencies
pip install -r requirements.txt

# Run application
python app.py

# Access at http://127.0.0.1:5000
# Login: admin / admin123
```

## Environment

- **OS:** Windows
- **Python:** 3.10+
- **Storage:** Excel files in `data/` directory
- **Port:** 5000 (configurable in app.py)

## Size & Performance

- **Project Size:** ~2 MB (after cleanup)
- **Database Size:** ~20 KB (Excel files)
- **RAM Usage:** ~100 MB (during operation)
- **Scalability:** Supports up to ~1000 students per section
