from database.mongo import db
import bcrypt

users = db.users

def register_user(username, email, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = {
        "username": username,
        "email": email,
        "password": hashed
    }

    users.insert_one(user)

def login_user(email, password):
    user = users.find_one({"email": email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password"]):
        return user
    return None