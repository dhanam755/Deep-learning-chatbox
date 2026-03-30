import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "chatbot_db"
COLLECTION_NAME = "conversations"
MODEL_PATH = "models/bert_intent_model"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")