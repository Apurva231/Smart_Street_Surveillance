import serial
import time
import json
import os
import cv2
from flask import Flask, jsonify, render_template, Response, request, url_for, redirect, session
from twilio.rest import Client
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from pymongo import DESCENDING
from werkzeug.security import generate_password_hash, check_password_hash
from geopy.geocoders import Nominatim

# Load environment variables
load_dotenv()

# MongoDB setup
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION")
MONGODB_EMERGENCY_COLLECTION = os.getenv("MONGODB_EMERGENCY_COLLECTION", "emergencies")
MONGODB_USERS_COLLECTION = os.getenv("MONGODB_USERS_COLLECTION", "users")

mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DB]
sensor_collection = mongo_db[MONGODB_COLLECTION]
emergency_collection = mongo_db[MONGODB_EMERGENCY_COLLECTION]
users_collection = mongo_db[MONGODB_USERS_COLLECTION]

# Twilio setup
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
EMERGENCY_CONTACT_NUMBER = os.getenv('EMERGENCY_CONTACT_NUMBER')

# Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")  # Required for sessions

twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Globals
emergency_sent = False
latest_frame = None

# Image path
IMAGE_DIR = os.path.join("static", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# Arduino connection
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    try:
        Arduino = serial.Serial(port="COM12", baudrate=115200, timeout=1)
        time.sleep(2)
        print("✅ Arduino connected")
    except serial.SerialException as e:
        print(f"❌ Arduino connection failed: {e}")
        Arduino = None
else:
    Arduino = None

# ---------------------------------------
# 🔐 LOGIN ROUTES
# ---------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------------------------

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    initial_data = {"temperature": None, "humidity": None, "co2": None, "motion": None, "emergency": None}
    return render_template('index.html', data=initial_data)

@app.route('/get_data')
def get_data():
    global emergency_sent, latest_frame

    if Arduino is None:
        return jsonify({"error": "Arduino not connected"}), 500

    try:
        Arduino.reset_input_buffer()

        for _ in range(10):
            if Arduino.in_waiting > 0:
                raw_data = Arduino.readline().strip()
                print(f"[RAW] {raw_data}")

                try:
                    decoded = raw_data.decode('utf-8')
                    print(f"[DECODED] {decoded}")

                    if decoded.startswith("{") and decoded.endswith("}"):
                        sensor_data = json.loads(decoded)

                        # Reset flag
                        if sensor_data.get("emergency") != 1:
                            emergency_sent = False

                        # Emergency handling
                        if sensor_data.get("emergency") == 1:
                            if not emergency_sent:
                                try:
                                    message = twilio_client.messages.create(
                                        body="🚨 Emergency Detected! Please check the surveillance dashboard.",
                                        from_=TWILIO_PHONE_NUMBER,
                                        to=EMERGENCY_CONTACT_NUMBER
                                    )
                                    print("📨 SMS sent. SID:", message.sid)
                                    emergency_sent = True
                                except Exception as sms_error:
                                    print("❌ Failed to send SMS:", sms_error)

                            if latest_frame is not None:
                                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                                filename = f"emergency_{timestamp}.jpg"
                                filepath = os.path.join(IMAGE_DIR, filename)
                                cv2.imwrite(filepath, latest_frame)
                                sensor_data["image_path"] = f"images/{filename}"
                        else:
                            sensor_data["image_path"] = None

                        sensor_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        try:
                            sensor_collection.insert_one(sensor_data)
                            print("✅ Sensor data stored in DB")
                        except Exception as db_error:
                            print("❌ DB Insertion Error:", db_error)

                        sensor_data.pop('_id', None)
                        return jsonify({"sensor_data": sensor_data})
                    else:
                        print("❗ Incomplete JSON")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    print(f"🔍 Problem String: {raw_data}")
            time.sleep(0.1)

        return jsonify({"error": "No complete data received from Arduino"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/data')
def view_data():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        records = list(sensor_collection.find().sort("timestamp", -1).limit(100))
        for record in records:
            record["_id"] = str(record["_id"])
        return render_template('data.html', records=records)
    except Exception as e:
        return f"<h2>Error fetching data from DB: {e}</h2>"

@app.route('/video_feed')
def video_feed():
    return Response(gen_camera_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_camera_feed():
    global latest_frame
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        latest_frame = frame.copy()
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    cap.release()

@app.route('/emergency', methods=['POST'])
def handle_emergency():
    data = request.get_json()
    try:
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid coordinates"}), 400

    try:
        latest_emergency = sensor_collection.find_one({"emergency": 1}, sort=[("timestamp", DESCENDING)])
        if not latest_emergency:
            return jsonify({"status": "error", "message": "No emergency record found"}), 404
        
        city, state = get_city_state(lat, lon)

        sensor_collection.update_one(
            {"_id": latest_emergency["_id"]},
            {"$set": {
                "latitude": lat,
                "longitude": lon,
                "city": city,
                "state": state
            }}
        )
        print(f"📍 Location added to existing emergency: ({lat}, {lon}) → {city}, {state}")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print("❌ Error saving emergency:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_emergencies')
def get_emergencies():
    try:
        records = list(sensor_collection.find(
            {"emergency": 1, "latitude": {"$exists": True}, "longitude": {"$exists": True}},
            {"_id": 0, "latitude": 1, "longitude": 1, "image_path": 1, "timestamp": 1}
        ))
        return jsonify(records)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/map')
def show_map():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("map.html")

@app.route('/detected_images')
def show_detected_images():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    detected_folder = os.path.join(app.static_folder, 'detected_images')
    try:
        image_cards = []
        for img in os.listdir(detected_folder):
            if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                static_path = f"detected_images/{img}"
                full_db_path = f"images/{img}"

                doc = sensor_collection.find_one({"image_path": full_db_path})
                if doc:
                    image_cards.append({
                        "img_path": static_path,
                        "timestamp": doc.get("timestamp", "N/A"),
                        "latitude": doc.get("latitude", "N/A"),
                        "longitude": doc.get("longitude", "N/A")
                    })
                else:
                    image_cards.append({
                        "img_path": static_path,
                        "timestamp": "Not found",
                        "latitude": "Not found",
                        "longitude": "Not found"
                    })

        return render_template("detected_images.html", image_cards=image_cards)
    except Exception as e:
        return f"Error loading images: {str(e)}"
    
geolocator = Nominatim(user_agent="smart_surveillance_dashboard")

def get_city_state(lat, lon):
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language='en')
        if location and location.raw and 'address' in location.raw:
            address = location.raw['address']
            city = address.get('city') or address.get('town') or address.get('village') or ''
            state = address.get('state') or ''
            return city, state
    except Exception as e:
        print(f"❌ Geocoding error for ({lat}, {lon}):", e)
    return '', ''

@app.route('/reports')
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    pipeline = [
        {"$match": {"emergency": 1, "state": {"$exists": True, "$ne": ""}}},
        {"$group": {"_id": "$state", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    state_counts = list(sensor_collection.aggregate(pipeline))

    states = [entry['_id'] for entry in state_counts]
    counts = [entry['count'] for entry in state_counts]

    return render_template("reports.html", states=states, counts=counts)


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5050, debug=True)
