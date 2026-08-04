# ChatBox AI

A production-oriented Flask chat application with Flask-Login authentication, MongoDB Atlas persistence, Groq-powered model selection, streamed responses, and a ChatGPT-inspired responsive UI.

## Features

- Email/password signup and login
- Flask-Login session authentication
- bcrypt password hashing
- CSRF protection and rate limiting
- MongoDB users, chats, and messages collections
- Groq model selection and streaming responses
- Markdown, code blocks, copy buttons, and auto-scroll
- Dark/light theme persistence
- TXT and PDF export
- Mobile-friendly sidebar and composer

## Environment

Create a `.env` file from `.env.example` and set:

- `SECRET_KEY`
- `MONGO_URI`
- `MONGO_DBNAME`
- `GROQ_API_KEY`

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

The app starts on `http://127.0.0.1:5000` by default.

## MongoDB Collections

### users

```json
{
  "_id": "ObjectId",
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password_hash": "bcrypt-hash",
  "created_at": "datetime"
}
```

### chats

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "title": "Machine Learning Discussion",
  "model": "llama-3.1-8b-instant",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": 2
}
```

### messages

```json
{
  "_id": "ObjectId",
  "chat_id": "ObjectId",
  "role": "user",
  "content": "Explain machine learning",
  "timestamp": "datetime"
}
```

## Setup

1. Create a MongoDB Atlas cluster and database user.
2. Copy `.env.example` to `.env` and fill in your credentials.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run `python app.py`.
5. Open the app and create a new account.
6. Log in and start chatting.

## Notes

- Streaming is exposed through `POST /api/chat/stream`.
- The non-stream endpoint `POST /api/chat` is available for simpler clients.
- Chat exports are available at `GET /api/export/<chat_id>.txt` and `GET /api/export/<chat_id>.pdf`.
