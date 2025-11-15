const mongoose = require("mongoose");

const AlertSchema = new mongoose.Schema({
  alert_type: { type: String, required: true },
  location: { type: String, required: true },
  timestamp: { type: Date, default: Date.now },
  status: { type: String, enum: ["New", "Resolved"], default: "New" },
  image_url: { type: String, default: null } // Store screenshot URL or base64
});

module.exports = mongoose.model("alerts", AlertSchema);
