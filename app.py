from flask import Flask, render_template, request, jsonify
from deep_model import get_response
import os

# remove tensorflow spam
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")

        bot_response = get_response(user_message)

        return jsonify({"response": bot_response})

    except Exception as e:
        print("Chat Error:", e)
        return jsonify({"response": "Internal server error occurred."})

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)