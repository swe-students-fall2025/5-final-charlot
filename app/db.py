from datetime import datetime
from typing import Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.results import InsertOneResult

import app.models as models
from app.config import get_settings

_settings = get_settings()

# Connect to MongoDB
client = MongoClient(_settings.mongodb_uri)
db = client[_settings.mongodb_db]

# Collections exposed for tests
users_collection = db["users"]
sessions_collection = db["sessions"]


def create_user(username: str, password_hash: str) -> InsertOneResult:
    """Create a new user in the db"""

    return users_collection.insert_one(
        {"username": username, "password_hash": password_hash, "sessions": []}
    )


def find_user_by_username(username: str) -> Optional[models.User]:
    """Find a user by username"""

    data = users_collection.find_one({"username": username})
    if data:
        return models.User.model_validate(data)
    else:
        return None


def find_user_by_id(user_id: str):
    """Find a user by id"""

    return models.User.model_validate(users_collection.find_one({"_id": ObjectId(user_id)}))


def create_session(session_id: str, user_id: str) -> None:
    """Create a session"""

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
