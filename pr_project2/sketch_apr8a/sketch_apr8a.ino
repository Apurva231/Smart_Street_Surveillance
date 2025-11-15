#include <DHT.h>
#include <SoftwareSerial.h>

// Pin Definitions
#define DHTPIN  5       // DHT11 sensor pin
#define DHTTYPE DHT11   // DHT sensor type
#define PIRPIN 7        // PIR sensor pin
#define CO2PIN A0       // CO2 sensor pin (Analog)
#define LDRPIN A1       // LDR sensor pin (Analog)
#define ALARMPIN 4      // Alarm pin (Buzzer)
#define LEDPIN 6        // LED pin for motion indication
#define VRX 2           // Voice Recognition Module RX
#define VTX 3           // Voice Recognition Module TX

// DHT Sensor
DHT dht(DHTPIN, DHTTYPE);

// Software Serial for Voice Recognition Module
SoftwareSerial voiceSerial(VRX, VTX);

void setup() {
  Serial.begin(115200);  // Serial communication with Raspberry Pi
  dht.begin();
  voiceSerial.begin(9600);  // Voice module baud rate

  pinMode(PIRPIN, INPUT);
  pinMode(ALARMPIN, OUTPUT);
  pinMode(LEDPIN, OUTPUT);

  Serial.println("Arduino Ready...");
}

void loop() {
  // Read Sensor Data
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int co2Value = analogRead(CO2PIN);
  int motionDetected = digitalRead(PIRPIN);
  int ldrValue = analogRead(LDRPIN);  // Read LDR value

  // Define light threshold for LED control
  int lightThreshold = 500; 

  // LED control logic: Turn ON if motion is detected and light is low
  if (motionDetected && ldrValue < lightThreshold) {
    digitalWrite(LEDPIN, HIGH);
  } else {
    digitalWrite(LEDPIN, LOW);
  }

  // Read from Voice Recognition Module
  int emergencyDetected = 0;
  if (voiceSerial.available()) {
    int command = voiceSerial.read();
    Serial.print("Voice Command Received: ");
    Serial.println(command);

    if (command == 0 || command == 1 || command == 2 ) {
      emergencyDetected = 1; // Emergency triggered
      Serial.println("🚨 Emergency detected! Triggering alarm...");
      triggerEmergency();
    } else {
      Serial.println("Unknown voice command received.");
    }
  }

  // Send Data to Raspberry Pi over Serial
  sendDataToRPi(temperature, humidity, co2Value, motionDetected, emergencyDetected, ldrValue);

  delay(1000);  // Wait before the next loop
}

// Function to trigger emergency
void triggerEmergency() {
  digitalWrite(ALARMPIN, HIGH);
  delay(5000);
  digitalWrite(ALARMPIN, LOW);
}

// Function to send sensor data to Raspberry Pi
void sendDataToRPi(float temp, float hum, int co2, int motion, int emergency, int ldr) {
  String payload = "{";
  payload += "\"temperature\":" + String(temp) + ",";
  payload += "\"humidity\":" + String(hum) + ",";
  payload += "\"co2\":" + String(co2) + ",";
  payload += "\"motion\":" + String(motion) + ",";
  payload += "\"emergency\":" + String(emergency) + ",";
  payload += "\"ldr\":" + String(ldr);
  payload += "}";

  Serial.println(payload);  // Send JSON data to Raspberry Pi
}