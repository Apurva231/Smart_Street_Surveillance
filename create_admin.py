# Modified create_admin.py
import os
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import getpass

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]
users = db[os.getenv("MONGODB_USERS_COLLECTION", "users")]

if users.find_one({"username": "admin"}) is None:
    plain_password = getpass.getpass("Enter new admin password: ")
    password = generate_password_hash(plain_password)
    users.insert_one({
        "username": "admin",
        "email": "admin@example.com",
        "password": password
    })
    print("✅ Admin user created.")
else:
    print("ℹ️ Admin user already exists.")
