# from pymongo import MongoClient
# from config import MONGO_URI
# from datetime import datetime

# client = MongoClient(MONGO_URI)
# db = client["chatbot_db"]

# chat_collection = db["chats"]


# # SAVE CHAT
# def save_chat(user_email, user_message, bot_response):
#     chat_collection.insert_one({
#         "user": user_email,
#         "user_message": user_message,
#         "bot_response": bot_response,
#         "time": datetime.now()
#     })


# # GET CHAT HISTORY
# def get_chat_history(user_email):
#     chats = chat_collection.find(
#         {"user": user_email}
#     ).sort("time", 1)

#     history = []

#     for chat in chats:
#         history.append({
#             "user": chat["user_message"],
#             "bot": chat["bot_response"]
#         })

#     return history

from pymongo import MongoClient
import os
from datetime import datetime

# Get Mongo URI from Render environment variable
MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["chatbot_db"]

chat_collection = db["chats"]


# SAVE CHAT
def save_chat(user_email, user_message, bot_response):
    chat_collection.insert_one({
        "user": user_email,
        "user_message": user_message,
        "bot_response": bot_response,
        "time": datetime.now()
    })


# GET CHAT HISTORY
def get_chat_history(user_email):
    chats = chat_collection.find(
        {"user": user_email}
    ).sort("time", 1)

    history = []

    for chat in chats:
        history.append({
            "user": chat["user_message"],
            "bot": chat["bot_response"]
        })

    return history
