const express = require("express");
const router = express.Router();
const Alert = require("../models/Alert");

// Get All Alerts (Now includes screenshots)
router.get("/", async (req, res) => {
  try {
    const alerts = await Alert.find().sort({ timestamp: -1 });
    res.json(alerts);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Store a new Alert (Now includes screenshot)
router.post("/", async (req, res) => {
  const { alert_type, location, image } = req.body;

  try {
    const newAlert = new Alert({
      alert_type,
      location,
      timestamp: new Date(),
      status: "New",
      image_url: image || null // Store the image URL or base64
    });

    await newAlert.save();
    res.json({ message: "Alert Saved", alert: newAlert });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
