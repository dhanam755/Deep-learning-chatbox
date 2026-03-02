from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def save_chat(user_message, bot_response):
    chat_data = {
        "user": user_message,
        "bot": bot_response,
        "timestamp": datetime.utcnow()
    }
    collection.insert_one(chat_data)