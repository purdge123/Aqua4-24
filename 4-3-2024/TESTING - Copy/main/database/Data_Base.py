from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB connection string
db = client["login_page"]  # Create or use the signup_db database
users_collection = db["login_signup"]  # Create a collection named users for storing signup data

