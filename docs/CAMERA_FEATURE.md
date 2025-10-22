# 📷 Camera/Webcam Feature

## Overview

When a student's NFC card is scanned during attendance, the system automatically captures a photo from the webcam showing the student. The photo is displayed prominently until the next student scans their card, then saved to disk for record-keeping.

## ✨ Features

✅ **Auto-capture on Scan** - Photo taken automatically when card is scanned
✅ **Live Display** - Photo shown immediately on screen with student name
✅ **Auto-replace** - Photo replaces automatically when next student scans
✅ **Auto-hide** - Photo hides after 30 seconds of inactivity
✅ **Persistent Storage** - All photos saved to `static/photos/` folder
✅ **Timestamped** - Each photo includes scan date/time and student name
✅ **Space Management** - Keeps recent photos, auto-deletes old ones
✅ **Status Indicator** - Shows camera status (Ready/Capturing/Error/Offline)

## 📸 How It Works

### 1. Card Scan Workflow
```
Student scans card
    ↓
NFC UID detected
    ↓
Student name identified
    ↓
/api/capture_photo called
    ↓
Webcam captures frame
    ↓
Timestamp & name added to image
    ↓
Photo saved to static/photos/
    ↓
Photo displayed on UI
    ↓
Status updated to show student name
    ↓
After 30 seconds → Photo auto-hides
```

### 2. Photo Naming
Files are named: `YYYYMMDD_HHMMSS_mmm_StudentName.jpg`

Example: `20241021_184512_345_Aditya_Bhardwaj.jpg`

### 3. Storage Location
```
static/
├── photos/              [All captured photos]
│   ├── 20241021_184512_001_John_Doe.jpg
│   ├── 20241021_184545_234_Jane_Smith.jpg
│   ├── 20241021_185012_567_Bob_Wilson.jpg
│   └── ... (more photos)
```

## 🔧 Requirements

### Dependencies
```bash
pip install opencv-python
```

OpenCV (cv2) - Already included in most Python installations

### Hardware
- Working webcam/USB camera connected to system
- Camera device accessible as `/dev/video0` (Linux) or `Camera` (Windows)

## 🚀 Setup

### 1. Install Requirements
```bash
pip install opencv-python
```

### 2. Connect Webcam
Plug in your USB webcam or use built-in camera

### 3. Verify Setup
The system auto-detects the camera on first session start. Check the status indicator:
- 🟢 **Ready** - Camera working
- 🔴 **Offline** - Camera not found
- 🔴 **Error** - Camera initialization failed

## 📋 UI Components

### Camera Display Area
Located at the top of the session page:
```
┌─────────────────────────────────────┐
│ 📷 Camera Feed          Ready        │
├─────────────────────────────────────┤
│                                     │
│    [Photo displays here]            │
│    or                               │
│    📷 Waiting for card scan...      │
│                                     │
└─────────────────────────────────────┘
```

### Photo Display
- **Size**: 16:9 aspect ratio (responsive)
- **Duration**: Shown until next card scanned or 30 seconds
- **Info**: Student name shown below timestamp
- **Update**: Instantly replaced when new card scanned

### Status Indicator
Shows camera state:
- `Ready` - Waiting for scan
- `📷 StudentName` - Currently displaying photo
- `Offline` - Camera not available
- `Error` - Something went wrong

## 🎯 Camera Controls

### Automatic Controls
- ✅ Auto-capture on card scan
- ✅ Auto-display of captured photo
- ✅ Auto-replace when next card scanned
- ✅ Auto-hide after 30 seconds

### Storage Management
- Keeps last 100 photos by default
- Automatically deletes oldest photos when limit exceeded
- All photos saved to `static/photos/`

## 📊 API Endpoints

### Capture Photo
```
POST /api/capture_photo
{
  "student_name": "John Doe"
}

Response:
{
  "success": true,
  "photo_url": "/static/photos/20241021_184512_123_John_Doe.jpg",
  "filename": "20241021_184512_123_John_Doe.jpg",
  "message": "Photo captured for John Doe"
}
```

### Photo Statistics
```
GET /api/photo_stats

Response:
{
  "success": true,
  "stats": {
    "photo_count": 45,
    "total_size_kb": 12345.6,
    "storage_dir": "static/photos"
  }
}
```

## 🛠️ Configuration

Edit `utils/webcam_capture.py` to customize:

```python
# Camera index (0 = default, 1 = USB camera, etc.)
get_webcam(camera_index=0)

# Storage directory
get_webcam(storage_dir="static/photos")

# Photo retention (in cleanup_old_photos)
keep_count=100  # Keep 100 most recent photos

# Camera resolution
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Width
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Height
```

## 🔍 Troubleshooting

### Camera Not Detected
**Problem:** "Camera not available" message

**Solutions:**
1. Check camera is connected
2. Verify camera works in other apps
3. Check camera permissions (Linux: `sudo usermod -a -G video $USER`)
4. Try different camera index in config

### Photos Not Saving
**Problem:** Photos captured but not appearing in folder

**Solutions:**
1. Check `static/photos/` directory exists and is writable
2. Verify disk space available
3. Check file permissions on `static/` folder
4. Try running with admin/sudo

### Photos Not Displaying
**Problem:** Photos captured but not shown on screen

**Solutions:**
1. Check browser cache (clear with Ctrl+Shift+Delete)
2. Verify browser has permission to display local images
3. Check browser console for errors (F12 → Console)
4. Try different browser

### Low Photo Quality
**Problem:** Captured photos are blurry

**Solutions:**
1. Adjust lighting in room
2. Check camera lens is clean
3. Increase camera focus time (add small delay before capture)
4. Adjust camera settings in code:
   ```python
   self.cap.set(cv2.CAP_PROP_FOCUS, 0)  # Manual focus
   self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Auto focus
   ```

## 📈 Performance

| Operation | Time |
|-----------|------|
| Initialize camera | ~500ms |
| Capture photo | ~100ms |
| Save to disk | ~50ms |
| Display on UI | <10ms |
| Auto-cleanup | ~200ms |

## 💾 Storage Considerations

### Photo Size
- Average: 200-300 KB per photo
- 100 photos: ~25-30 MB
- 1000 photos: ~250-300 MB

### Retention Policy
- Default: Keep last 100 photos
- Automatic cleanup every session
- Manual cleanup available via API

### Disk Space Management
```python
# Get storage stats
webcam = get_webcam()
stats = webcam.get_storage_stats()
print(f"Photos: {stats['photo_count']}")
print(f"Size: {stats['total_size_kb']} KB")

# Manual cleanup
deleted = webcam.cleanup_old_photos(keep_count=50)
```

## 🔐 Privacy & Security

### Data Handling
- Photos are local files only
- No cloud upload
- Stored in `static/photos/` visible to authenticated users
- Recommended: Implement access control to this folder

### Recommendations
1. Restrict access to `static/photos/` folder
2. Implement session-based access control
3. Regular backup of photos
4. Implement retention policies per regulations
5. Encrypt photos if required by policy

## 📝 Log Output

Camera operations are logged to console:

```
[INFO] Webcam initialized successfully
[INFO] Photo saved: 20241021_184512_123_John_Doe.jpg (256.3 KB)
[INFO] Camera released
[INFO] Cleaned up 15 old photos
```

## 🎓 Usage Examples

### Check Camera Status
```javascript
// In browser console
fetch('/api/photo_stats')
  .then(r => r.json())
  .then(d => console.log(d.stats))
```

### Manual Photo Cleanup
```python
from utils.webcam_capture import get_webcam

webcam = get_webcam()
# Keep only 50 most recent photos
deleted = webcam.cleanup_old_photos(keep_count=50)
print(f"Deleted {deleted} old photos")
```

### Custom Camera Index
```python
# Use different camera (e.g., USB camera as device 1)
from utils.webcam_capture import WebcamCapture

webcam = WebcamCapture(camera_index=1)
webcam.start_capture_thread()
filename = webcam.capture_photo("Test Student")
```

## 🚀 Integration with Main System

The camera feature is **fully integrated** with:
- ✅ NFC card scanning
- ✅ Student attendance marking
- ✅ Session management
- ✅ Report generation
- ✅ Web interface

**Key Integration Points:**
1. `app.py` - API endpoints for photo capture
2. `class_session.html` - Camera display UI
3. `class_session.js` - Frontend photo capture logic
4. `utils/webcam_capture.py` - Backend camera control

## 📞 Support

For camera issues, check:
1. OpenCV installation: `python -c "import cv2; print(cv2.__version__)"`
2. Camera availability: `python utils/webcam_capture.py`
3. Browser console (F12) for JavaScript errors
4. Server console for Python errors
5. File permissions on `static/photos/`

## ✅ Checklist

Before using camera feature:
- [ ] OpenCV installed (`pip install opencv-python`)
- [ ] Webcam connected and tested
- [ ] `static/photos/` directory exists
- [ ] Write permissions on `static/` folder
- [ ] Browser cache cleared
- [ ] JavaScript console shows no errors
- [ ] Server log shows successful initialization

## 🎉 You're Ready!

The camera feature is now active. When you start a session:
1. Camera will initialize automatically
2. Status will show "Ready"
3. When student scans card, photo captured instantly
4. Photo displayed with student name
5. Next scan replaces photo

Enjoy hands-free attendance with photos! 📸
