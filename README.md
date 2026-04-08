# 🛡️ Smart Street Surveillance System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![Arduino](https://img.shields.io/badge/Arduino-IoT-00979D?style=for-the-badge&logo=arduino&logoColor=white)
![YOLOv5](https://img.shields.io/badge/YOLOv5-Object%20Detection-FF6F00?style=for-the-badge&logo=pytorch&logoColor=white)
![Twilio](https://img.shields.io/badge/Twilio-Alerts-F22F46?style=for-the-badge&logo=twilio&logoColor=white)

**An IoT and AI-powered smart surveillance system for women's safety** — integrating Arduino sensors, YOLOv5 object detection, real-time geo-location tracking, voice-based distress detection, and instant emergency alerts.

[Features](#-features) • [Tech Stack](#-tech-stack) • [Project Structure](#-project-structure) • [Getting Started](#-getting-started) • [How It Works](#-how-it-works)

</div>

---

## 🚨 The Problem

Women's safety in public spaces remains a critical concern. Existing surveillance systems are largely passive — they record, but don't respond. This project aims to change that by building a system that **detects threats in real time and acts immediately**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📷 **Live Camera Monitoring** | Real-time video feed with continuous surveillance |
| 🤖 **YOLOv5 Object Detection** | Detects people, suspicious objects, and threat scenarios |
| 🎤 **Voice Distress Detection** | Identifies distress calls or screams in the environment |
| 🚨 **Emergency Alerts** | Instant SMS/call alerts to authorities via Twilio |
| 📍 **Geo-Location Tracking** | Real-time location pinpointing on an interactive map |
| 🗺️ **Live Map Dashboard** | Visual map interface showing surveillance zones and alerts |
| 📊 **Reports & Analytics** | Historical data view of detected incidents |
| 🔐 **Admin Login** | Secure access to the monitoring dashboard |
| 🔌 **Arduino IoT Sensors** | Hardware-level integration for physical environment sensing |

---

## 🧰 Tech Stack

**AI / Detection**
- YOLOv5 (PyTorch) — object & person detection
- OpenCV — image processing and camera feed
- Custom voice detection pipeline

**Backend**
- Python, Flask
- Twilio API — SMS & voice emergency alerts
- MongoDB / SQLite — incident logging

**Frontend**
- HTML5, CSS3, JavaScript
- Jinja2 templates (Flask)
- Leaflet.js / Google Maps — geo-location map

**Hardware**
- Arduino (`.ino` sketches) — sensor integration
- IoT sensors for environment monitoring

---

## 📁 Project Structure

```
PR_PROJECT/
│
├── arduino_code/
│   └── arduino_code.ino        # Arduino sensor integration code
│
├── sketch_apr8a/
│   ├── sketch_apr2a/
│   └── sketch_apr8a.ino        # Arduino sketch (alternate version)
│
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # Frontend JavaScript
│   ├── images/                 # Static assets
│   └── detected_images/        # Runtime: YOLO detection snapshots
│
├── templates/
│   ├── index.html              # Main dashboard
│   ├── login.html              # Admin login page
│   ├── map.html                # Live geo-location map
│   ├── data.html               # Sensor data view
│   ├── detected_images.html    # Detection results gallery
│   └── reports.html            # Incident reports
│
├── server.py                   # Flask application entry point
├── img_detect.py               # YOLOv5 image detection pipeline
├── create_admin.py             # Script to create admin user
├── yolov5s.pt                  # YOLOv5 model weights (not committed)
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (not committed)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Arduino IDE (for hardware setup)
- Twilio account (for emergency alerts)
- Webcam / IP camera

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Smart_Street_Surveillance.git
cd Smart_Street_Surveillance
```

### 2. Set Up Python Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number
EMERGENCY_CONTACT=recipient_phone_number
SECRET_KEY=your_flask_secret_key
```

### 4. Download YOLOv5 Weights

```bash
# Download yolov5s.pt manually from:
# https://github.com/ultralytics/yolov5/releases
# Place it in the project root directory
```

### 5. Create Admin User

```bash
python create_admin.py
```

### 6. Run the Server

```bash
python server.py
```

Visit `http://localhost:5000` to access the dashboard.

### 7. Arduino Setup

1. Open `arduino_code/arduino_code.ino` in Arduino IDE
2. Select your board and COM port
3. Upload the sketch to your Arduino device

---

## 🔍 How It Works

```
Camera Feed → YOLOv5 Detection → Threat Analysis
                                        │
                    ┌───────────────────┼───────────────────┐
                    ▼                   ▼                   ▼
             Save Snapshot      Trigger SMS Alert     Log to Database
                    │                   │                   │
                    ▼                   ▼                   ▼
            Detection Gallery    Twilio Sends Alert    Reports Dashboard
                                        │
                                        ▼
                               Real-time Map Update
```

1. **Camera** continuously streams video to the Flask server
2. **YOLOv5** processes frames to detect people and suspicious scenarios
3. On a **threat trigger**, the system captures a snapshot and logs the incident
4. **Twilio** immediately dispatches an SMS/call to the emergency contact
5. **Geo-location** is updated on the live map dashboard
6. **Arduino sensors** feed additional environmental data (sound, motion, etc.)

---

## 📸 Dashboard Pages

| Page | Route | Description |
|---|---|---|
| Dashboard | `/` | Live camera feed + detection status |
| Login | `/login` | Admin authentication |
| Map | `/map` | Real-time geo-location tracking |
| Detections | `/detected_images` | Gallery of flagged snapshots |
| Reports | `/reports` | Historical incident log |
| Sensor Data | `/data` | Arduino sensor readings |

---

## ⚠️ Important Notes

- `yolov5s.pt` is **not included** in the repo (>50MB). Download it separately from [Ultralytics](https://github.com/ultralytics/yolov5/releases).
- Never commit your `.env` file — it contains sensitive Twilio credentials.
- `static/detected_images/` is excluded from version control as it contains runtime-generated files.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

<div align="center">

**Built for women's safety — because every street should be safe. 💜**

If this project helped you, please consider giving it a ⭐

</div>