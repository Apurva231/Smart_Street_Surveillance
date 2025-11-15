#include <DHT.h>
#include <SoftwareSerial.h>

// Pin Definitions
#define DHTPIN  5
#define DHTTYPE DHT11
#define PIRPIN 7
#define CO2PIN A0
#define LDRPIN A1
#define ALARMPIN 4
#define LEDPIN 6
#define VRX 2
#define VTX 3

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial voiceSerial(VRX, VTX);

void setup() {
  Serial.begin(115200);
  dht.begin();
  voiceSerial.begin(9600);

  pinMode(PIRPIN, INPUT);
  pinMode(ALARMPIN, OUTPUT);
  pinMode(LEDPIN, OUTPUT);

  Serial.println("Arduino Ready...");
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int co2Value = analogRead(CO2PIN);
  int motionDetected = digitalRead(PIRPIN);
  int ldrValue = analogRead(LDRPIN);

  int lightThreshold = 500;
  if (motionDetected && ldrValue < lightThreshold) {
    digitalWrite(LEDPIN, HIGH);
  } else {
    digitalWrite(LEDPIN, LOW);
  }

  int emergencyDetected = 0;
  if (voiceSerial.available()) {
    int command = voiceSerial.read();
    Serial.print("Voice Command Received: ");
    Serial.println(command);

    if (command == 0 || command == 1 || command == 2 ) {
      emergencyDetected = 1;
      Serial.println("🚨 Emergency detected! Triggering alarm...");
      triggerEmergency();
    } else {
      Serial.println("Unknown voice command received.");
    }
  }

  sendDataToRPi(temperature, humidity, co2Value, motionDetected, emergencyDetected, ldrValue);
  delay(1000);
}

void triggerEmergency() {
  digitalWrite(ALARMPIN, HIGH);
  delay(5000);
  digitalWrite(ALARMPIN, LOW);
}

void sendDataToRPi(float temp, float hum, int co2, int motion, int emergency, int ldr) {
  Serial.print("{\"temperature\":");
  Serial.print(temp);
  Serial.print(",\"humidity\":");
  Serial.print(hum);
  Serial.print(",\"co2\":");
  Serial.print(co2);
  Serial.print(",\"motion\":");
  Serial.print(motion);
  Serial.print(",\"emergency\":");
  Serial.print(emergency);
  Serial.print(",\"ldr\":");
  Serial.print(ldr);
  Serial.println("}");
}

