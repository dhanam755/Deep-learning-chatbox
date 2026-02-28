import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import os

MODEL_PATH = "models/deep_chat_model.h5"
TOKENIZER_PATH = "models/tokenizer.pkl"

texts = [
    "hello",
    "hi",
    "good morning",
    "i want to book a ticket",
    "book flight to chennai",
    "cancel my booking",
    "track my order",
    "where is my parcel"
]

responses = [
    "Hello! How can I help you?",
    "Hi there! What can I do for you?",
    "Good morning! How may I assist?",
    "Sure! Please provide travel date.",
    "Okay, tell me your travel date.",
    "Please provide booking ID to cancel.",
    "Please provide tracking number.",
    "Share tracking ID to check status."
]

tokenizer = Tokenizer(oov_token="<OOV>")
tokenizer.fit_on_texts(texts)

sequences = tokenizer.texts_to_sequences(texts)
padded = pad_sequences(sequences, padding='post')

labels = np.arange(len(responses))

MAX_LEN = padded.shape[1]

if not os.path.exists(MODEL_PATH):

    model = Sequential([
        Embedding(len(tokenizer.word_index)+1, 64),
        LSTM(64),
        Dense(64, activation='relu'),
        Dense(len(responses), activation='softmax')
    ])

    model.compile(loss="sparse_categorical_crossentropy",
                  optimizer="adam",
                  metrics=["accuracy"])

    model.fit(padded, labels, epochs=500, verbose=0)

    os.makedirs("models", exist_ok=True)
    model.save(MODEL_PATH)

    with open(TOKENIZER_PATH, "wb") as f:
        pickle.dump(tokenizer, f)

else:
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(TOKENIZER_PATH, "rb") as f:
        tokenizer = pickle.load(f)


def get_response(user_text):
    try:
        seq = tokenizer.texts_to_sequences([user_text])
        padded_seq = pad_sequences(seq, maxlen=MAX_LEN, padding='post')

        prediction = model.predict(padded_seq, verbose=0)
        index = np.argmax(prediction)

        if index < len(responses):
            return responses[index]
        else:
            return "Sorry, I don't understand."

    except Exception as e:
        print("Model Error:", e)
        return "Server error occurred."