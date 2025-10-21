# Stop Session & PDF Export Feature

## Overview
This feature allows you to stop an active NFC attendance session and automatically generate a professional PDF report with attendance statistics.

## Features

### 1. Stop Session Endpoint
**Endpoint:** `POST /api/stop_session`

**Purpose:**
- Stops the current NFC scanning session
- Gathers attendance data (present/absent students)
- Generates a PDF report
- Automatically resets the session

**Response:**
```json
{
  "success": true,
  "message": "Session stopped and PDF exported",
  "pdf_file": "session_report_D2_20251021_231715.pdf",
  "stats": {
    "total": 68,
    "present": 3,
    "absent": 65
  }
}
```

### 2. PDF Report Contents

The generated PDF includes:

- **Header:** "NFC ATTENDANCE SYSTEM - SESSION REPORT"
- **Session Details:**
  - Section
  - Subject
  - Start Time
  - End Time
  - Report Generated Time
- **Attendance Statistics:**
  - Total Students
  - Present Count & Percentage
  - Absent Count & Percentage
- **Present Students Table:**
  - Student Number
  - Name
  - Enrollment Number
  - Roll Number
- **Absent Students Table:**
  - Student Number
  - Name
  - Enrollment Number
  - Roll Number

### 3. PDF Location

All generated PDFs are saved to: `static/reports/session_report_[SECTION]_[TIMESTAMP].pdf`

Example: `session_report_D2_20251021_231715.pdf`

## Usage

### Via API
```bash
curl -X POST http://localhost:5000/api/stop_session \
  -H "Content-Type: application/json" \
  -b "session=YOUR_SESSION_COOKIE"
```

### How It Works

1. **Start Session** - Begin NFC scanning with `/api/start_class_session`
2. **Scan Cards** - Students scan their NFC cards during the session
3. **Stop Session** - Call `/api/stop_session` to end the session
4. **PDF Generated** - Professional report is automatically created
5. **Download** - PDF file is saved in `static/reports/`

## Features

✓ **Professional Formatting** - Color-coded tables (blue for present, red for absent)
✓ **Complete Statistics** - Shows total, present, and absent counts
✓ **Automatic Filename** - Includes section and timestamp
✓ **Error Handling** - Gracefully handles missing data
✓ **Thread-Safe** - Safe concurrent access to attendance data

## Dependencies

- `reportlab==4.0.4` - PDF generation library

## Example Workflow

```
1. POST /api/start_class_session
   {
     "subject": "Mathematics",
     "section": "D2",
     "class_start": "09:00",
     "class_end": "10:00"
   }

2. [Students scan cards...]

3. POST /api/stop_session
   Returns:
   {
     "success": true,
     "pdf_file": "session_report_D2_20251021_231715.pdf",
     "stats": {
       "total": 68,
       "present": 5,
       "absent": 63
     }
   }

4. Download PDF from static/reports/session_report_D2_20251021_231715.pdf
```

## PDF Styling

- **Header Colors:** Blue (#0066cc) for title
- **Present Table:** Blue header, light beige rows
- **Absent Table:** Red header (#cc0000), light red rows
- **Font:** Helvetica (standard PDF font)
- **Page Size:** Letter (8.5" x 11")

## Session Data Used

The PDF is generated from:
1. **Session Info** - From `session_mgr.current_session`
2. **Present Students** - From `session_mgr.scanned_uids` (students who scanned)
3. **Roster** - From `data/sections/[SECTION].xlsx` (all students in section)
4. **Absent Students** - Calculated as: Roster - Present

## Error Handling

If PDF generation fails:
```json
{
  "success": false,
  "message": "Session stopped but PDF generation failed"
}
```

Session will still be stopped and reset even if PDF generation fails.

## Future Enhancements

Potential improvements:
- Email PDF to administrators
- Add QR code with session ID
- Include timestamp for each student scan
- Export to other formats (Excel, CSV)
- Add signature field for instructor
- Include class notes or remarks
