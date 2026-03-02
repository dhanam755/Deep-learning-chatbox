
from flask import Flask, render_template, request, jsonify
import logging
from services.groq_service import get_groq_response
from database.mongo import save_chat

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_bot_response(user_message):
    try:
        bot_reply = get_groq_response(user_message)

        if not bot_reply:
            return "I couldn't generate a response."

        return bot_reply

    except Exception as e:
        logging.error(f"Error in bot response: {e}")
        return "Sorry, something went wrong."

@app.route("/")
def home():
    return render_template("index.html")
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

        save_chat(user_message, bot_response)

        print("BOT RESPONSE:", bot_response)

        return jsonify({"response": bot_response})

    except Exception as e:
        logging.error(f"Chat route error: {e}")
        return jsonify({"response": "Server error occurred."})



if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)