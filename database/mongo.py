from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import ConfigurationError, OperationFailure, PyMongoError, ServerSelectionTimeoutError
from pymongo import MongoClient, ASCENDING, DESCENDING

from config import Config


_client: MongoClient | None = None


class _CollectionProxy:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    def _collection(self):
        return _get_db()[self.collection_name]

    def __getattr__(self, item):
        return getattr(self._collection(), item)


def _get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(
            Config.MONGO_URI,
            serverSelectionTimeoutMS=Config.MONGO_SERVER_SELECTION_TIMEOUT_MS,
            connectTimeoutMS=Config.MONGO_CONNECT_TIMEOUT_MS,
        )
    return _client


def _get_db():
    return _get_client()[Config.MONGO_DBNAME]


users = _CollectionProxy("users")
chats = _CollectionProxy("chats")
messages = _CollectionProxy("messages")


def _database_error_message(exc: Exception) -> str:
    message = str(exc).lower()
    if isinstance(exc, OperationFailure) and ("bad auth" in message or getattr(exc, "code", None) == 8000):
        return (
            "MongoDB Atlas authentication failed. Check that MONGO_URI uses a Database Access user, "
            "the password is correct and URL-encoded, and authSource=admin is present."
        )
    if isinstance(exc, (ConfigurationError, ServerSelectionTimeoutError)) or "dns" in message or "timeout" in message:
        return (
            "MongoDB Atlas connection failed. Check Network Access IP allowlist, DNS/connectivity, "
            "cluster hostname, and MONGO_URI."
        )
    if isinstance(exc, PyMongoError):
        return f"MongoDB error: {exc}"
    return str(exc)


def _with_mongo_error_translation(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except (OperationFailure, ConfigurationError, ServerSelectionTimeoutError, PyMongoError) as exc:
        raise RuntimeError(_database_error_message(exc)) from exc


def ensure_indexes() -> None:
    try:
        users.create_index([("email", ASCENDING)], unique=True)
        chats.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])
        chats.create_index([("user_id", ASCENDING), ("title", ASCENDING)])
        messages.create_index([("chat_id", ASCENDING), ("timestamp", ASCENDING)])
    except OperationFailure as exc:
        if "bad auth" in str(exc).lower() or exc.code == 8000:
            raise RuntimeError(
                "MongoDB Atlas authentication failed. Check that MONGO_URI uses a Database Access user, "
                "the password is correct and URL-encoded, and authSource=admin is present."
            ) from exc
        raise
    except (ConfigurationError, ServerSelectionTimeoutError) as exc:
        raise RuntimeError(
            "MongoDB Atlas connection failed. Check Network Access IP allowlist, DNS/connectivity, "
            "cluster hostname, and MONGO_URI."
        ) from exc
    except PyMongoError as exc:
        raise RuntimeError(f"MongoDB startup check failed: {exc}") from exc


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_object_id(value: Any) -> Optional[ObjectId]:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return None


def candidate_values(value: Any) -> List[Any]:
    candidates: List[Any] = []
    object_id = to_object_id(value)
    if object_id is not None:
        candidates.append(object_id)
    if value is not None and value not in candidates:
        candidates.append(value)
    return candidates


def serialize_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not user:
        return None
    return {
        "id": str(user["_id"]),
        "name": user.get("name", ""),
        "email": user.get("email", ""),
        "created_at": user.get("created_at"),
    }


def serialize_chat(chat: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(chat["_id"]),
        "user_id": str(chat["user_id"]),
        "title": chat.get("title", "New Chat"),
        "created_at": chat.get("created_at"),
        "updated_at": chat.get("updated_at"),
        "model": chat.get("model", "llama-3.1-8b-instant"),
        "message_count": chat.get("message_count", 0),
    }


def serialize_message(message: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(message["_id"]),
        "chat_id": str(message["chat_id"]),
        "role": message.get("role", "assistant"),
        "content": message.get("content", ""),
        "timestamp": message.get("timestamp"),
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    return _with_mongo_error_translation(users.find_one, {"email": email.lower().strip()})


def get_user_by_id(user_id: Any) -> Optional[Dict[str, Any]]:
    object_id = to_object_id(user_id)
    if not object_id:
        return None
    return _with_mongo_error_translation(users.find_one, {"_id": object_id})


def create_user(name: str, email: str, password_hash: str) -> str:
    result = _with_mongo_error_translation(
        users.insert_one,
        {
            "name": name.strip(),
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "created_at": now_utc(),
        },
    )
    return str(result.inserted_id)


def create_chat(user_id: Any, title: str, model: str) -> str:
    result = chats.insert_one(
        {
            "user_id": to_object_id(user_id) or user_id,
            "title": title,
            "model": model,
            "created_at": now_utc(),
            "updated_at": now_utc(),
            "message_count": 0,
        }
    )
    return str(result.inserted_id)


def update_chat_title(chat_id: Any, title: str) -> None:
    chat_candidates = candidate_values(chat_id)
    if chat_candidates:
        chats.update_one({"_id": {"$in": chat_candidates}}, {"$set": {"title": title, "updated_at": now_utc()}})


def delete_chat(chat_id: Any, user_id: Any) -> None:
    chat_candidates = candidate_values(chat_id)
    user_candidates = candidate_values(user_id)
    if not chat_candidates or not user_candidates:
        return
    result = chats.delete_one({"_id": {"$in": chat_candidates}, "user_id": {"$in": user_candidates}})
    if result.deleted_count:
        messages.delete_many({"chat_id": {"$in": chat_candidates}})


def get_chat(chat_id: Any, user_id: Any) -> Optional[Dict[str, Any]]:
    chat_candidates = candidate_values(chat_id)
    user_candidates = candidate_values(user_id)
    if not chat_candidates or not user_candidates:
        return None
    return chats.find_one({"_id": {"$in": chat_candidates}, "user_id": {"$in": user_candidates}})


def list_chats(user_id: Any, search: str = "") -> List[Dict[str, Any]]:
    user_candidates = candidate_values(user_id)
    query: Dict[str, Any] = {"user_id": {"$in": user_candidates}} if user_candidates else {"user_id": user_id}
    if search.strip():
        query["title"] = {"$regex": search.strip(), "$options": "i"}
    cursor = chats.find(query).sort([("updated_at", DESCENDING), ("created_at", DESCENDING)])
    return [serialize_chat(chat) for chat in cursor]


def add_message(chat_id: Any, role: str, content: str) -> str:
    chat_candidates = candidate_values(chat_id)
    if not chat_candidates:
        raise ValueError("Invalid chat id.")

    result = messages.insert_one(
        {
            "chat_id": chat_candidates[0],
            "role": role,
            "content": content,
            "timestamp": now_utc(),
        }
    )
    chats.update_one({"_id": {"$in": chat_candidates}}, {"$set": {"updated_at": now_utc()}, "$inc": {"message_count": 1}})
    return str(result.inserted_id)


def list_messages(chat_id: Any) -> List[Dict[str, Any]]:
    chat_candidates = candidate_values(chat_id)
    if not chat_candidates:
        return []
    cursor = messages.find({"chat_id": {"$in": chat_candidates}}).sort("timestamp", ASCENDING)
    return [serialize_message(message) for message in cursor]


def get_recent_user_messages(chat_id: Any, limit: int = 8) -> List[Dict[str, Any]]:
    chat_candidates = candidate_values(chat_id)
    if not chat_candidates:
        return []
    cursor = messages.find({"chat_id": {"$in": chat_candidates}}).sort("timestamp", DESCENDING).limit(limit)
    return [serialize_message(message) for message in reversed(list(cursor))]


def delete_message(message_id: Any, chat_id: Any = None) -> bool:
    message_candidates = candidate_values(message_id)
    if not message_candidates:
        return False

    query: Dict[str, Any] = {"_id": {"$in": message_candidates}}
    if chat_id is not None:
        chat_candidates = candidate_values(chat_id)
        if not chat_candidates:
            return False
        query["chat_id"] = {"$in": chat_candidates}

    message_doc = messages.find_one(query)
    if not message_doc:
        return False

    messages.delete_one({"_id": message_doc["_id"]})
    chats.update_one(
        {"_id": message_doc["chat_id"]},
        {"$set": {"updated_at": now_utc()}, "$inc": {"message_count": -1}},
    )
    return True


def list_user_messages(user_id: Any, limit: int = 1) -> List[str]:
    cursor = chats.find({"user_id": user_id}).sort([("updated_at", DESCENDING)]).limit(limit)
    return [chat.get("title", "New Chat") for chat in cursor]


def summarize_title(text: str) -> str:
    title = text.strip().replace("\n", " ")
    title = title[:48].strip()
    return title if title else "New Chat"
