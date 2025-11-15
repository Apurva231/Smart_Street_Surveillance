const mongoose = require('mongoose');

const weatherSchema = new mongoose.Schema({
    log_id: String, // ✅ Changed to String (e.g., "log_123456789")
    timestamp: { type: Date, default: Date.now },
    temperature: Number,
    humidity: Number,
    co2_level: Number
});

const Weather = mongoose.model('weather_logs', weatherSchema); // ✅ Collection name remains 'weather_logs'
module.exports = Weather;
