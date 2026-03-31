# 📘 Roomba-900-Local-Connect (v2.1.0)

## Local API Suite for iRobot Roomba 900 Series*

This project provides a robust, local-only Python implementation for controlling iRobot Roomba 900 series vacuums (960, 980, etc.). It specifically solves the **Legacy SSL** and **DH Key Too Small** errors common in modern Python (3.10+) and OpenSSL 3.0 environments.

## 🧩 Features
* **Unified Extraction**: One tool to find your BLID and Password.
* **Modern SSL Context**: Pre-configured to allow secure connections to older hardware.
* **REST API**: Control your robot via simple HTTP requests.
* **Real-time Status**: Monitor battery, bins, and X/Y coordinates.

## 🚀 Quick Start
1. **Clone & Install**:
   ```bash
   pip install paho-mqtt fastapi uvicorn python-dotenv roombapy
   ```
2. **Extract Credentials**:
   Put your Roomba in pairing mode (Hold HOME until it plays a tune) and run:
   ```bash
   python roomba_unified_extractor.py --ip 192.168.1.XX
   ```
3. **Configure `.env`**:
   Create a `.env` file based on the extracted values.

4. **Launch Dashboard**:
   ```bash
   python main.py
   ```

## ⚠️ Important Note
**Close the iRobot App**: The Roomba 980 only allows **one** local connection at a time. If the official app is open on your phone, this script will be rejected with an "Unauthorized" error.

## 🏁 API Endpoints
* `GET /status`: Full JSON status report.
* `GET /control/start`: Starts the cleaning mission.
* `GET /control/dock`: Returns the robot to its base.

---

### 5. Supporting Files

### .env.example:
```text
ROOMBA_IP=
ROOMBA_BLID=
ROOMBA_PASSWORD=
```

#### .gitignore:
```text
.env
__pycache__/
*.pyc
```
