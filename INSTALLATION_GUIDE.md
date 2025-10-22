# 📦 Python Library Installation Guide

## 🚀 Quick Install (Recommended)

Copy and paste this command in PowerShell or Command Prompt:

### Option 1: Using requirements.txt (Easiest)
```powershell
pip install -r requirements.txt
```

### Option 2: Individual Installation
```powershell
pip install Flask==2.3.3 Flask-SocketIO==5.3.5 python-socketio==5.9.0 python-engineio==4.7.1 pyscard==2.0.7 pyttsx3==2.90 reportlab==4.0.4 pandas==2.0.3 openpyxl==3.1.2 opencv-python==4.8.0.76 Pillow==10.0.0 python-dotenv==1.0.0
```

## 📋 All Required Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **Flask** | 2.3.3 | Web framework |
| **Flask-SocketIO** | 5.3.5 | Real-time communication |
| **python-socketio** | 5.9.0 | Socket.IO support |
| **python-engineio** | 4.7.1 | Engine.IO support |
| **pyscard** | 2.0.7 | NFC card reading |
| **pyttsx3** | 2.90 | Text-to-speech feedback |
| **reportlab** | 4.0.4 | PDF generation |
| **pandas** | 2.0.3 | Data handling |
| **openpyxl** | 3.1.2 | Excel file handling |
| **opencv-python** | 4.8.0.76 | Camera/Webcam capture |
| **Pillow** | 10.0.0 | Image processing |
| **python-dotenv** | 1.0.0 | Environment variables |

## 💾 Installation Steps

### Step 1: Open Command Prompt or PowerShell
- Press `Win + R`
- Type `powershell` or `cmd`
- Press Enter

### Step 2: Navigate to Project Directory
```powershell
cd C:\Users\Admin\Desktop\nfc_aditya
```

### Step 3: Install All Libraries
```powershell
pip install -r requirements.txt
```

### Step 4: Verify Installation
```powershell
python -c "import flask; import cv2; import openpyxl; import reportlab; print('✅ All libraries installed successfully!')"
```

## 🔧 Step-by-Step Commands

If you prefer to install each library individually, use these commands:

```powershell
# Web Framework
pip install Flask==2.3.3

# Real-time Communication
pip install Flask-SocketIO==5.3.5
pip install python-socketio==5.9.0
pip install python-engineio==4.7.1

# NFC Card Reader
pip install pyscard==2.0.7

# Audio Feedback
pip install pyttsx3==2.90

# Report Generation
pip install reportlab==4.0.4

# Data Handling
pip install pandas==2.0.3
pip install openpyxl==3.1.2

# Camera/Webcam
pip install opencv-python==4.8.0.76
pip install Pillow==10.0.0

# Utilities
pip install python-dotenv==1.0.0
```

## 🎯 Upgrade pip (Optional but Recommended)

Before installing, ensure pip is up to date:

```powershell
python -m pip install --upgrade pip
```

## ⚠️ Troubleshooting

### Issue: "pip is not recognized"
**Solution:** Python might not be in PATH. Try:
```powershell
python -m pip install -r requirements.txt
```

### Issue: "No module named 'pyscard'"
**Solution:** This requires smartcard drivers. Install:
```powershell
pip install pyscard
# Also install PC/SC library if on Windows:
# https://github.com/clausecker/pcsclite
```

### Issue: OpenCV installation fails
**Solution:** Try the headless version:
```powershell
pip install opencv-python-headless
```

Or install with specific version:
```powershell
pip install opencv-python==4.8.0.76 --no-binary opencv-python
```

### Issue: "Permission denied"
**Solution:** Run Command Prompt as Administrator:
1. Right-click Command Prompt
2. Select "Run as administrator"
3. Run the pip install command

### Issue: Module imports but doesn't work
**Solution:** Reinstall the problematic library:
```powershell
pip uninstall package_name
pip install package_name==version
```

## ✅ Verification Commands

Test each library:

```powershell
# Flask
python -c "import flask; print('✅ Flask:', flask.__version__)"

# Flask-SocketIO
python -c "import flask_socketio; print('✅ Flask-SocketIO')"

# pyscard
python -c "import smartcard; print('✅ pyscard')"

# pyttsx3
python -c "import pyttsx3; print('✅ pyttsx3')"

# reportlab
python -c "import reportlab; print('✅ reportlab')"

# pandas
python -c "import pandas; print('✅ pandas:', pandas.__version__)"

# openpyxl
python -c "import openpyxl; print('✅ openpyxl')"

# OpenCV
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"

# Pillow
python -c "import PIL; print('✅ Pillow:', PIL.__version__)"

# python-dotenv
python -c "import dotenv; print('✅ python-dotenv')"

# All together
python -c "import flask, flask_socketio, pyscard, pyttsx3, reportlab, pandas, openpyxl, cv2, PIL, dotenv; print('✅ All libraries installed!')"
```

## 🚀 Start the Application

After installation:

```powershell
# Navigate to project directory (if not already there)
cd C:\Users\Admin\Desktop\nfc_aditya

# Run the application
python app.py

# Or with Flask development server
flask run

# Or with SocketIO support
python -m flask run
```

The application will be available at: `http://localhost:5000`

## 💡 Quick Commands Cheat Sheet

```powershell
# Install from requirements.txt
pip install -r requirements.txt

# Upgrade all packages
pip install --upgrade -r requirements.txt

# List installed packages
pip list

# Show specific package info
pip show package_name

# Install specific version
pip install package_name==version

# Uninstall package
pip uninstall package_name

# Generate requirements.txt
pip freeze > requirements.txt

# Install from URL
pip install git+https://github.com/user/repo.git
```

## 📝 Requirements.txt Location

The `requirements.txt` file is located at:
```
C:\Users\Admin\Desktop\nfc_aditya\requirements.txt
```

## 🔗 Environment Setup

### Create Virtual Environment (Optional but Recommended)

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Deactivate when done
deactivate
```

## 📞 Getting Help

If you encounter issues:

1. **Check Python version:** `python --version` (Should be 3.7+)
2. **Check pip version:** `pip --version`
3. **Search error online:** Copy the error message into Google
4. **Check library documentation:** Visit PyPI.org/project/package-name
5. **Try different version:** Some libraries have version conflicts

## 🎉 You're Ready!

Once all libraries are installed:

```powershell
python app.py
```

Then open: `http://localhost:5000`

Enjoy! 🚀
