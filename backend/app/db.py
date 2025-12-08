from datetime import datetime

from pymongo import MongoClient

from .config import get_settings

_settings = get_settings()

# Connect to MongoDB
client = MongoClient(_settings.mongodb_uri)
db = client[_settings.mongodb_db]

# Collections exposed for tests
users_collection = db["users"]
sessions_collection = db["sessions"]


def create_user(user_id: str, email: str, password_hash: str) -> None:
    users_collection.insert_one(
        {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash,
        }
    )


def find_user_by_email(email: str):
    return users_collection.find_one({"email": email})


def find_user_by_id(user_id: str):
    return users_collection.find_one({"user_id": user_id})


def create_session(session_id: str, user_id: str) -> None:
    sessions_collection.insert_one(
        {
            "session_id": session_id,
            "user_id": user_id,
            "messages": [],
            "files": [],
        }
    )


def list_sessions_for_user(user_id: str):
    return list(sessions_collection.find({"user_id": user_id}))


def get_session(session_id: str, user_id: str | None = None):
    query = {"session_id": session_id}
    if user_id is not None:
        query["user_id"] = user_id
    return sessions_collection.find_one(query)


def add_message_to_session(session_id: str, role: str, message: str) -> None:
    sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "message": message,
                    "timestamp": datetime.utcnow(),
                }
            }
        },
    )


def add_file_to_session(session_id: str, filename: str, path: str) -> None:
    sessions_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {
                "files": {
                    "filename": filename,
                    "path": path,
                }
            }
        },
    )
