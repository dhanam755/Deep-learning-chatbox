import jwt
import datetime
from config import JWT_SECRET

def create_token(email):

    payload = {
        "email":email,
        "exp": datetime.datetime.utcnow()+datetime.timedelta(hours=2)
    }

    token = jwt.encode(payload,JWT_SECRET,algorithm="HS256")

    return token


def verify_token(token):

    try:
        payload = jwt.decode(token,JWT_SECRET,algorithms=["HS256"])
        return payload["email"]

    except:
        return None