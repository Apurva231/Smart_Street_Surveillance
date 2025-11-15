const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
    user_id: Number,
    name: String,
    email: String,
    password_hash: String,
    role: String
});

module.exports = mongoose.model("users", UserSchema);
