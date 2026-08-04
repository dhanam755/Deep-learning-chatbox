import os
from datetime import timedelta
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from dotenv import load_dotenv


load_dotenv(override=True)


def database_name_from_uri(uri: str, fallback: str = "chatbox") -> str:
	parsed = urlparse(uri or "")
	name = (parsed.path or "").strip("/")
	return name or fallback


def normalize_mongo_uri(uri: str) -> str:
	parsed = urlparse(uri or "")
	if parsed.scheme != "mongodb+srv" or not parsed.username:
		return uri

	query = dict(parse_qsl(parsed.query, keep_blank_values=True))
	query.setdefault("retryWrites", "true")
	query.setdefault("w", "majority")
	query.setdefault("authSource", "admin")
	return urlunparse(parsed._replace(query=urlencode(query)))


class Config:
	SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")
	MONGO_URI = normalize_mongo_uri(os.getenv("MONGO_URI", "mongodb://localhost:27017/chatbox"))
	MONGO_DBNAME = os.getenv("MONGO_DBNAME") or database_name_from_uri(MONGO_URI)
	MONGO_SERVER_SELECTION_TIMEOUT_MS = int(os.getenv("MONGO_SERVER_SELECTION_TIMEOUT_MS", "15000"))
	MONGO_CONNECT_TIMEOUT_MS = int(os.getenv("MONGO_CONNECT_TIMEOUT_MS", "15000"))
	GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
	SESSION_COOKIE_HTTPONLY = True
	SESSION_COOKIE_SAMESITE = "Lax"
	SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
	PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.getenv("SESSION_HOURS", "8")))
	RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")
	RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
	MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(2 * 1024 * 1024)))
	BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", "12"))
