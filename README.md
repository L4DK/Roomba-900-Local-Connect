# 🧹 Roomba-900-Local-Connect

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi)](https://fastapi.tiangolo.com/)

> **A high-performance, local-only MQTT & REST API bridge for iRobot Roomba 900 series vacuums.**

This project provides a robust solution for controlling legacy iRobot hardware (960, 980, etc.) in modern environments. It specifically resolves the **"DH Key Too Small"** and **"Legacy SSL Renegotiation"** errors introduced in OpenSSL 3.0 and Python 3.10+.

---

## 🧩 Key Features

* **Zero-Cloud Dependency**: Communicate directly with your robot over your local Wi-Fi.
* **Modern SSL Context**: Pre-configured engine to handle legacy iRobot encryption safely.
* **Unified Credential Extractor**: A high-integrity tool to retrieve your `BLID` and `Password` in seconds.
* **FastAPI Dashboard**: A lightweight REST API to monitor status and trigger missions via HTTP.
* **Real-time Telemetry**: Access battery levels, bin status, and X/Y coordinates for map building.

---

## 🏗 System Architecture

The project is divided into three core modules designed for maximum stability:

1. **The Extractor**: Uses UDP discovery and pairing handshakes to find credentials.
2. **The Engine**: A multi-threaded MQTT client that maintains a persistent local socket.
3. **The API**: A FastAPI layer that exposes the robot's state to your smart home or dashboard.

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/L4DK/Roomba-900-Local-Connect.git
cd Roomba-900-Local-Connect
pip install -r requirements.txt
```

### 2. Extract Your Credentials

Your Roomba requires a unique **BLID** (Username) and **Password** (16-char string).

1. Place the Roomba in the charging dock.
2. Hold the **HOME** button for ~2-5 seconds until a melody plays and the Wi-Fi icon flashes.
3. Run the extractor immediately:

    ```bash
    python roomba_unified_extractor.py --ip 192.168.1.XX
    ```

### 3. Configuration

Rename `.env.example` to `.env` and fill in your details:

```env
ROOMBA_IP=192.168.1.XX
ROOMBA_BLID=YOUR_BLID_HERE
ROOMBA_PASSWORD=YOUR_CLEAN_PASSWORD_HERE
```

### 4. Launch the Server

```bash
python main.py
```

Your API will now be live at `http://localhost:8000`.

---

## 🏁 API Documentation

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | System metadata and connection health. |
| `/status` | `GET` | Full telemetry (Battery, Bin, Position, Sensors). |
| `/info` | `GET` | Technical connection and MQTT details. |
| `/control/{cmd}` | `GET` | Validates and sends: `start`, `stop`, `pause`, `resume`, `dock`. |

---

## ⚠️ Important Considerations

### The "One Connection" Rule

The Roomba 900 series hardware only allows **one local MQTT connection at a time**.
**CRITICAL**: You must fully close the official iRobot app on your mobile device before running this script. If the app is active, the script will return an **"Unauthorized"** or **"Connection Refused"** error.

### Security

This suite uses absolute pathing logic for `.env` files. Ensure your `.env` is never committed to a public repository (the included `.gitignore` handles this automatically).

---

## 🛠 Troubleshooting

* **SSL Errors?** Ensure you are using Python 3.10+. The `roomba_logic.py` automatically sets `SECLEVEL=1` to allow the Roomba’s older certificates.
* **Not Authorized?** Check that your `ROOMBA_PASSWORD` in `.env` is the clean 16-character string, not the full raw pairing response.
* **No Data?** Ensure your robot is on the same subnet as your server. Some "Guest" Wi-Fi networks block local device-to-device communication.

---

## 👨‍💻 Author

**Michael Landbo** - *Lead Developer*

---

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.

---

### Supporting Files (For your reference)

**`.env.example`**

```text
ROOMBA_IP=192.168.1.XX
ROOMBA_BLID=YOUR_BLID_HERE
ROOMBA_PASSWORD=YOUR_CLEAN_PASSWORD_HERE
```

**`.gitignore`**

```text
.env
__pycache__/
*.py[cod]
*.swp
.DS_Store
```
