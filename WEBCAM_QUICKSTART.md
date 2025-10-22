# 📷 Webcam Feature - Quick Start

## ⚡ 30-Second Setup

```bash
# 1. Install OpenCV
pip install opencv-python

# 2. Connect webcam

# 3. Start server and visit http://localhost:5000

# Done! ✅
```

## 🎯 How It Works

```
Card Scan → Photo Captured → Photo Displayed → Photo Saved
                ↓                 ↓              ↓
             100ms            Instant         Disk
```

## 📸 What Happens

| When | What |
|------|------|
| **Card Scanned** | Camera captures photo automatically |
| **Photo Shows** | Within 0.5 seconds on screen |
| **Student Name** | Displayed with timestamp |
| **Next Scan** | Photo replaces with new one |
| **After 30s** | Photo auto-hides |
| **Stored** | All photos in `static/photos/` |

## 🔌 What You Need

- ✅ Webcam/USB camera
- ✅ OpenCV installed
- ✅ Storage space (~25MB for 100 photos)

## 🚀 Usage

1. **Start Session** → Camera initializes
2. **See "Ready"** → Status shows green
3. **Scan Card** → Photo appears instantly
4. **Next Scan** → Photo replaces
5. **That's it!** → All automatic

## 📊 Photo Storage

```
static/photos/
├── 20241021_184512_001_John_Doe.jpg
├── 20241021_184545_234_Jane_Smith.jpg
└── [up to 100 photos, auto-cleaned]
```

## 🔧 Configuration

**Default settings work great!** But you can customize:

```python
# In utils/webcam_capture.py

# Different camera
get_webcam(camera_index=1)

# Different location
get_webcam(storage_dir="/custom/path")

# Keep more photos
cleanup_old_photos(keep_count=200)
```

## ✅ Verification

```bash
# Test webcam works
python utils/webcam_capture.py

# Should output:
# ✅ Webcam initialized
# ✅ Photo saved: ...
```

## 📞 Troubleshooting

| Issue | Fix |
|-------|-----|
| **Camera not found** | Check it's connected; try `python utils/webcam_capture.py` |
| **Photos not saving** | Check `static/photos/` writable |
| **Photo not showing** | Clear browser cache (Ctrl+Shift+Delete) |
| **Blurry photos** | Check lighting; clean lens |

## 📚 Full Docs

- `CAMERA_FEATURE.md` - Complete feature guide
- `WEBCAM_IMPLEMENTATION_COMPLETE.md` - Technical details

## 🎉 You're Ready!

Install OpenCV and you're done!

```bash
pip install opencv-python
```

Then just start a session and scan cards. Photos appear automatically! 📸
