# 🚀 Tap & Track: NFC-Enabled Attendance Management System

> An innovative **NFC-based attendance system** that replaces manual roll calls with a fast, secure, and real-time tracking solution.

---

## 📌 Project Overview

**Tap & Track** is an automated attendance management system that uses **Near-Field Communication (NFC)** technology to simplify attendance tracking. It is designed for schools, colleges, and workplaces to ensure **accuracy, efficiency, and real-time data logging**.

---

## ✨ Features

* ⚡ **Automated Attendance** – Just tap an NFC card to mark attendance instantly.
* 🆕 **Smart Registration** – Automatically detects and registers new NFC cards.
* 🚫 **Duplicate Scan Prevention** – Avoids multiple entries within a short time.
* ⏱️ **Real-Time Logging** – Stores attendance with timestamps.
* 🖥️ **User-Friendly GUI** – Built with Tkinter for easy admin interaction.
* 🔐 **Secure Storage** – Keeps user data and logs safe.

---

## 🛠️ Technologies Used

* **Python** – Core application logic
* **Tkinter** – GUI development
* **NFC Hardware + nfcpy** – Card scanning
* **SQLite / Excel** – Data storage (`pandas`, `openpyxl`)

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Aditya-xcity/nfc-attendance-pro.git
cd nfc-attendance-pro
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:

* **Windows:**

```bash
venv\Scripts\activate
```

* **Linux/Mac:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
python main.py
```

### What you can do:

* Start the attendance system
* Register new users via NFC card scan
* Monitor attendance logs in real-time

---

## 📂 Project Structure

```
nfc-attendance-pro/
├── database/       # Database manager scripts
├── models/         # Data models
├── nfc/            # NFC integration logic
├── ui/             # GUI components
├── utils/          # Helper functions
├── attendance.db   # SQLite database
├── DATA.xlsx       # Excel data storage
├── main.py         # Application entry point
└── requirements.txt
```

---

## 🚧 Future Improvements

* 📊 Attendance analytics & reports
* 👥 Advanced user management (edit/delete)
* 🔒 Data encryption & access control
* ⚙️ Multi-threading for faster NFC scanning
* 🗄️ Full migration to SQLite for better performance

---

## 🤝 Contributing

Contributions are welcome! Fork the repository and submit a pull request.

---

## 📜 License

This project is open-source and free to use for educational purposes.

---

💡 *Built to make attendance effortless and smart.*
