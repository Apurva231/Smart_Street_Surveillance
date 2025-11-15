const mongoose = require("mongoose");

const EmergencyContactSchema = new mongoose.Schema({
    contact_id: Number,
    name: String,
    role: String, // police, ambulance
    phone_number: String,
    email: String,
});

module.exports = mongoose.model("emergency_contacts", EmergencyContactSchema);
