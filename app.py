
# from flask import Flask, render_template, request, jsonify
# import logging
# from services.groq_service import get_groq_response
# from database.mongo import save_chat

# app = Flask(__name__)
# logging.basicConfig(level=logging.INFO)

# def get_bot_response(user_message):
#     try:
#         bot_reply = get_groq_response(user_message)

#         if not bot_reply:
#             return "I couldn't generate a response."

#         return bot_reply

#     except Exception as e:
#         logging.error(f"Error in bot response: {e}")
#         return "Sorry, something went wrong."

# @app.route("/")
# def home():
#     return render_template("index.html")
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

#         save_chat(user_message, bot_response)

#         print("BOT RESPONSE:", bot_response)

#         return jsonify({"response": bot_response})

#     except Exception as e:
#         logging.error(f"Chat route error: {e}")
#         return jsonify({"response": "Server error occurred."})



# if __name__ == "__main__":
#     app.run(debug=True, use_reloader=False)


from flask import Flask, render_template, request, jsonify, redirect, session
import logging

from services.groq_service import get_groq_response
from database.mongo import save_chat, get_chat_history
from services.auth_service import register_user, login_user

app = Flask(__name__)
app.secret_key = "supersecretkey"

logging.basicConfig(level=logging.INFO)


# ---------------- BOT RESPONSE ---------------- #

def get_bot_response(user_message):
    try:
        bot_reply = get_groq_response(user_message)

        if not bot_reply:
            return "I couldn't generate a response."

        return bot_reply

    except Exception as e:
        logging.error(f"Error in bot response: {e}")
        return "Sorry, something went wrong."


# ---------------- HOME PAGE ---------------- #

@app.route("/")
def home():

    if "user" not in session:
        return redirect("/login")

    return render_template("index.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        register_user(username, email, password)

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = login_user(email, password)

        if user:
            session["user"] = email
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")


# ---------------- CHAT API ---------------- #

@app.route("/chat", methods=["POST"])
def chat():
    try:

        if "user" not in session:
            return jsonify({"response": "Please login first."})

        data = request.get_json()
        user_message = data.get("message", "")

        if not user_message.strip():
            return jsonify({"response": "Please type something."})

        bot_response = get_bot_response(user_message)

        if not bot_response:
            bot_response = "I couldn't generate a response."

        # Save chat with user email
        save_chat(session["user"], user_message, bot_response)

        print("BOT RESPONSE:", bot_response)

        return jsonify({"response": bot_response})

    except Exception as e:
        logging.error(f"Chat route error: {e}")
        return jsonify({"response": "Server error occurred."})


# ---------------- CHAT HISTORY ---------------- #

@app.route("/history")
def history():

    if "user" not in session:
        return jsonify([])

    history = get_chat_history(session["user"])

    return jsonify(history)


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)