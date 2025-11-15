const express = require("express");
const router = express.Router();
const twilio = require("twilio");
const nodemailer = require("nodemailer");
const EmergencyContact = require("../models/EmergencyContact");

// Twilio Configuration
const accountSid = process.env.TWILIO_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilioPhoneNumber = process.env.TWILIO_PHONE_NUMBER;
const client = new twilio(accountSid, authToken);

// Email Configuration
const transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS,
    },
});

// Trigger Emergency Alert
router.post("/trigger", async (req, res) => {
    const { type, location } = req.body;

    try {
        const contacts = await EmergencyContact.find({ role: type.toLowerCase() });

        if (contacts.length === 0) {
            return res.status(404).json({ message: "No emergency contacts found." });
        }

        // Send SMS & Email to each contact
        for (const contact of contacts) {
            // Send SMS
            await client.messages.create({
                body: `EMERGENCY ALERT! \nType: ${type}\nLocation: ${location}`,
                from: twilioPhoneNumber,
                to: contact.phone_number,
            });

            // Send Email
            const mailOptions = {
                from: process.env.EMAIL_USER,
                to: contact.email,
                subject: "Emergency Alert 🚨",
                text: `EMERGENCY ALERT!\nType: ${type}\nLocation: ${location}\nImmediate action required!`,
            };
            await transporter.sendMail(mailOptions);
        }

        res.json({ message: "Emergency alerts sent successfully!" });
    } catch (error) {
        console.error("Error sending emergency alerts:", error);
        res.status(500).json({ error: "Failed to send alerts" });
    }
});

module.exports = router;
