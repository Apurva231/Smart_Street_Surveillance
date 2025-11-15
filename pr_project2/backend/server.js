const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const mongoose = require("mongoose");
const axios = require("axios");
const Weather = require("./models/Weather");
const Alert = require("./models/Alert"); // Import Alerts Model

dotenv.config();
const connectDB = require("./config/db");

const app = express();
app.use(express.json({ limit: "10mb" }));
app.use(cors());

connectDB().catch((err) => {
  console.error("❌ MongoDB Connection Error:", err);
  process.exit(1);
});

const alertRoutes = require("./routes/alerts");
app.use("/api/alerts", alertRoutes);

// API to Receive Screenshot and Store with Alert
app.post("/api/screenshot", async (req, res) => {
  try {
    const { image, alert_type, location } = req.body;

    if (!image) {
      return res.status(400).json({ error: "No image data received" });
    }

    const newAlert = new Alert({
      alert_type: alert_type || "Unknown Alert",
      location: location || "Unknown Location",
      timestamp: new Date(),
      status: "New",
      image_url: image // Storing image as base64
    });

    await newAlert.save();

    console.log("✅ Screenshot stored with alert:", newAlert);
    res.json({ message: "Screenshot stored successfully!", alert: newAlert });
  } catch (error) {
    console.error("❌ Error saving screenshot:", error);
    res.status(500).json({ error: "Failed to save screenshot" });
  }
});

// ✅ API to Get Latest Weather Entry
app.get("/api/weather/latest", async (req, res) => {
  try {
      const latestWeather = await Weather.findOne().sort({ timestamp: -1 });
      if (!latestWeather) {
          return res.status(404).json({ message: "No weather data found" });
      }
      res.json(latestWeather);
  } catch (error) {
      console.error("❌ Fetch error:", error);
      res.status(500).json({ error: "Failed to fetch latest data" });
  }
});

// ✅ Fetch Sensor Data from Flask API and Update MongoDB
const fetchAndStoreSensorData = async () => {
  try {
      console.log("📡 Fetching sensor data from Flask...");
      const response = await axios.get("http://localhost:5000/get_data");
      const sensorData = response.data.sensor_data;

      if (!sensorData) {
          console.warn("⚠ No valid sensor data received.");
          return;
      }

      // Extract sensor data assuming format: "temperature,humidity,co2_level"
      const [temperature, humidity, co2_level] = sensorData.split(",").map(Number);

      if (isNaN(temperature) || isNaN(humidity) || isNaN(co2_level)) {
          console.error("❌ Invalid sensor data format:", sensorData);
          return;
      }

      // ✅ Update latest weather entry OR insert new one if none exists
      const latestWeather = await Weather.findOne().sort({ timestamp: -1 });

      const weatherData = {
          temperature,
          humidity,
          co2_level,
          timestamp: new Date()
      };

      if (latestWeather) {
          await Weather.updateOne({ _id: latestWeather._id }, { $set: weatherData });
          console.log("🌦 Updated latest weather data:", weatherData);
      } else {
          const newWeather = new Weather(weatherData);
          await newWeather.save();
          console.log("🌦 Inserted first weather data:", newWeather);
      }

  } catch (error) {
      console.error("❌ Error fetching sensor data:", error);
  }
};

// ✅ Automatically fetch sensor data every 5 seconds
setInterval(fetchAndStoreSensorData, 5000);


const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});
