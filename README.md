---

## ✅ Requirements

- Python 3.8 or higher
- pip (Python package manager)
- A device on the same WiFi network for student testing using phone

---

## ⚙️ Installation & Setup

### Step 1 — Download / Extract the Project

Extract the ZIP file to any folder on your PC.
Example: `C:\Users\YourName\Desktop\QR Attendance\`

---

### Step 2 — Open Terminal in Project Folder

**Windows:**
- Open the extracted folder
- Click the address bar at the top
- Type `powershell` and press Enter

OR open PowerShell manually and navigate:
```powershell
cd "C:\Users\YourName\Desktop\QR Attendance"
```

---

### Step 3 — Create Virtual Environment

```powershell
python -m venv venv
```

---

### Step 4 — Activate Virtual Environment

**Windows PowerShell:**
```powershell
venv\Scripts\activate
```

You should see `(venv)` appear at the start of the terminal line.

> ⚠️ If you get an execution policy error, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then run the activate command again.

---

### Step 5 — Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs: Flask, Flask-Login, Flask-SQLAlchemy, qrcode, Pillow

---

### Step 6 — Run the Application

```powershell
python app.py
```
---

### Step 7 — Open in Browser

On your PC:
http://127.0.0.1:5000

On a phone (must be on same WiFi):
http://192.168.1.12:5000

Replace `192.168.1.12` with the Network IP shown in your terminal.

---

## 🔑 Demo Login Credentials

| Role    | Username  | Password  |
|---------|-----------|-----------|
| Teacher | teacher1  | teach123  |
| Teacher | teacher2  | teach123  |
| Student | student1  | stud123   |
| Student | student2  | stud123   |
| Student | student3  | stud123   |
| Student | student4  | stud123   |
| Student | student5  | stud123   |

---

## 📱 How to Use — Demo Flow

### Teacher Side (PC Browser)
1. Open `http://127.0.0.1:5000`
2. Login as `teacher1` / `teach123`
3. Click **"+ New Session"**
4. Enter subject name (e.g. DBMS) → Click **"Generate QR Code"**
5. A QR code appears — show it to students
6. Watch the attendance list update live (auto-refreshes every 15s)
7. Click **"⬇️ Export CSV"** to download attendance as a spreadsheet

### Student Side (Phone Browser)
1. Connect phone to **same WiFi** as the PC
2. Open phone browser → go to `http://192.168.1.12:5000`
3. Login as `student1` / `stud123`
4. Click **"Scan QR"**
5. Choose a scanning method:
   - **Option 1 (Recommended):** Open phone Camera or Google Lens → point at QR → tap the link
   - **Option 2:** Use the manual fallback — paste the QR URL or type session number

### Result
- ✅ "Attendance Recorded Successfully!" screen appears
- 🔁 "Already Recorded" if scanned twice
- ❌ Error if expired or wrong network

---

## 🧠 Validation Rules

Every attendance attempt checks:

| Check | Rule |
|-------|------|
| Session exists | Session ID must be in database |
| QR expiry | Must scan within 3 minutes of generation |
| Duplicate | Each student can only mark once per session |
| Network match | Student must be on same WiFi subnet as teacher |

---

## 📊 Export Attendance

- **Single session:** Open any session → click **"⬇️ Export CSV"**
- **All sessions:** Teacher dashboard → click **"⬇️ Export All"**

Downloaded file opens in Microsoft Excel or Google Sheets.

---

## 🗄️ Database

The database is created automatically on first run.
Location: `instance/database.db`

**Tables:**
- `users` — stores teachers and students
- `sessions` — stores each QR attendance session
- `attendance` — stores each student's attendance record

To view the database visually, download:
**DB Browser for SQLite** → https://sqlitebrowser.org/dl/

---

## 🌐 Network Setup for Demo
PC (Teacher)  ──── WiFi Router ──── Phone (Student)
│                                     │
└──────── Same subnet ────────────────┘
192.168.1.x

**Using phone hotspot instead of WiFi router:**
1. Turn on phone hotspot
2. Connect PC to phone hotspot
3. Run `ipconfig` in PowerShell → find new IP
4. Use that IP to access the app from both devices

---

## ⚠️ Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `venv\Scripts\activate` first, then `python app.py` |
| Phone can't connect | Run firewall fix below |
| `source` not recognized | Use `venv\Scripts\activate` (not `source`) on Windows |
| Camera scanner not working | Use phone camera app / Google Lens instead (HTTP limitation) |
| QR expired | Generate a new session — QR is valid for 3 minutes only |
| Network mismatch error | Ensure phone and PC are on the same WiFi network |

**Firewall fix (run PowerShell as Administrator):**
```powershell
netsh advfirewall firewall add rule name="AcadScan Flask" dir=in action=allow protocol=TCP localport=5000
```

---

## 🏗️ Architecture

### Client-Server
Phone / Browser (Client)
│  HTTP Request
▼
Flask Server on PC (Server)
│  Query
▼
SQLite Database

### Layered Architecture
│  Presentation Layer     │  HTML Templates
├─────────────────────────┤
│  Routes Layer           │  Flask Blueprints
├─────────────────────────┤
│  Services Layer         │  Business Logic
├─────────────────────────┤
│  Data Layer             │  SQLAlchemy + SQLite
└─────────────────────────┘

---

## 📦 Dependencies
Flask==3.x
Flask-Login==0.6.x
Flask-SQLAlchemy==3.x
qrcode==7.x
Pillow==10.x

Install all with:
```powershell
pip install -r requirements.txt
```

---

## 👨‍💻 Built With

- **Backend:** Python, Flask
- **Database:** SQLite via Flask-SQLAlchemy
- **QR Generation:** qrcode + Pillow
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Authentication:** Flask-Login

---
