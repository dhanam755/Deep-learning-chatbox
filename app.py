# from flask import Flask, render_template, request, jsonify
# import logging

# from utils.nlp_preprocess import preprocess_text
# from services.bert_service import predict_intent
# from services.gpt_service import get_gpt_response
# from database.mongo import save_chat

# app = Flask(__name__)
# logging.basicConfig(level=logging.INFO)


# def get_bot_response(user_message):
#     processed = preprocess_text(user_message)

#     intent, confidence = predict_intent(processed)

#     logging.info(f"Intent: {intent}, Confidence: {confidence}")

#     # 🔹 High confidence → Use Intent-based reply
#     if confidence > 0.6:
#         if intent == "greeting":
#             return "Hello! How can I help you today?"
#         elif intent == "feeling":
#             return "I'm doing great! How about you?"
#         elif intent == "goodbye":
#             return "Goodbye! Have a nice day!"
#         elif intent == "thanks":
#             return "You're welcome!"

#     # 🔹 Low confidence → Use GPT (ChatGPT-style)
#     return get_gpt_response(user_message)


# @app.route("/")
# def home():
#     return render_template("index.html")


# @app.route("/chat", methods=["POST"])
# def chat():
#     data = request.get_json()
#     user_message = data.get("message", "")

#     if not user_message.strip():
#         return jsonify({"response": "Please type something."})

#     bot_response = get_bot_response(user_message)

#     # Save conversation to MongoDB
#     save_chat(user_message, bot_response)

#     return jsonify({"response": bot_response})


# if __name__ == "__main__":
#     app.run(debug=True)


# //  background good//
# from flask import Flask, render_template, request, jsonify
# import logging

# # Groq LLM
# from services.groq_service import get_groq_response

# # MongoDB
# from database.mongo import save_chat

# app = Flask(__name__)
# logging.basicConfig(level=logging.INFO)


# # 🔹 Main Bot Logic
# def get_bot_response(user_message):
#     try:
#         bot_reply = get_groq_response(user_message)

#         if not bot_reply:
#             return "I couldn't generate a response."

#         return bot_reply

#     except Exception as e:
#         logging.error(f"Error in bot response: {e}")
#         return "Sorry, something went wrong."


# # 🔹 Home Route
# @app.route("/")
# def home():
#     return render_template("index.html")


# # 🔹 Chat API Route
# @app.route("/chat", methods=["POST"])
# def chat():
#     try:
#         data = request.get_json()
#         user_message = data.get("message", "")

#         if not user_message.strip():
#             return jsonify({"response": "Please type something."})

#         bot_response = get_bot_response(user_message)

#         if not bot_response:
#             bot_response = "I couldn't generate a response."

#         # Save to MongoDB
#         save_chat(user_message, bot_response)

#         print("BOT RESPONSE:", bot_response)

#         return jsonify({"response": bot_response})

#     except Exception as e:
#         logging.error(f"Chat route error: {e}")
#         return jsonify({"response": "Server error occurred."})


# # 🔹 Run App
# if __name__ == "__main__":
#     app.run(debug=True)




from flask import Flask, render_template, request, jsonify
import logging

# Groq LLM
from services.groq_service import get_groq_response

# MongoDB
from database.mongo import save_chat

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


# 🔹 Main Bot Logic
def get_bot_response(user_message):
    try:
        bot_reply = get_groq_response(user_message)

        if not bot_reply:
            return "I couldn't generate a response."

        return bot_reply

    except Exception as e:
        logging.error(f"Error in bot response: {e}")
        return "Sorry, something went wrong."


# 🔹 Home Route
@app.route("/")
def home():
    return render_template("index.html")


# 🔹 Chat API Route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message.strip():
            return jsonify({"response": "Please type something."})

        bot_response = get_bot_response(user_message)

        if not bot_response:
            bot_response = "I couldn't generate a response."

        # Save to MongoDB
        save_chat(user_message, bot_response)

        print("BOT RESPONSE:", bot_response)

        return jsonify({"response": bot_response})

    except Exception as e:
        logging.error(f"Chat route error: {e}")
        return jsonify({"response": "Server error occurred."})


# 🔹 Run App (Windows-safe)
if __name__ == "__main__":
    # Disable reloader to avoid Thread-2 socket errors on Windows
    app.run(debug=True, use_reloader=False)