const mongoose = require("mongoose");

const SurveillanceLogSchema = new mongoose.Schema({
    log_id: { type: Number, unique: true },
    timestamp: { type: Date, default: Date.now },
    anomaly_detected: { type: Boolean, required: true },
    audio_triggered: { type: [String], default: [] },
    image_url: { type: String, required: true } // Store Base64 or Cloud URL
});

module.exports = mongoose.model("surveillance_logs", SurveillanceLogSchema);
