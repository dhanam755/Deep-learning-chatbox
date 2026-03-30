# from pymongo import MongoClient
# from config import MONGO_URI, DB_NAME, COLLECTION_NAME
# from datetime import datetime

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]
# collection = db[COLLECTION_NAME]
# users = db["users"]
# chats = db["chats"]

# def save_chat(user_message, bot_response):
#     chat_data = {
#         "user": user_message,
#         "bot": bot_response,
#         "timestamp": datetime.utcnow()
#     }
#     collection.insert_one(chat_data)
    
# def save_chat(user_email, message, response):
    
#     chats.insert_one({
#         "user_email": user_email,
#         "message": message,
#         "response": response
#     })
    
# def get_chat_history(user_email):
    
#     history = chats.find(
#         {"user_email": user_email},
#         {"_id": 0}
#     )

#     return list(history)


# @app.route("/chat", methods=["POST"])
# def chat():

#     data = request.json
#     message = data["message"]

#     response = chatbot_response(message)

#     chat_collection.insert_one({
#         "username": session["user"],
#         "message": message,
#         "response": response
#     })

#     return jsonify({"response": response})


from pymongo import MongoClient
from config import MONGO_URI
from datetime import datetime

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