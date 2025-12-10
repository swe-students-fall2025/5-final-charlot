"""DB operations"""

# from datetime import datetime
from datetime import datetime
from typing import Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.results import InsertOneResult

from app import models
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
    return None


def find_user_by_id(user_id: str) -> Optional[models.User]:
    """Find a user by id"""

    data = users_collection.find_one({"_id": ObjectId(user_id)})
    if data:
        return models.User.model_validate(data)
    return None


def create_session(user_id: str, title: str) -> ObjectId:
    """Create a session"""

    inserted = sessions_collection.insert_one(
        {"user_id": ObjectId(user_id), "title": title, "messages": [], "date_created": datetime.now()}
    )
    users_collection.find_one_and_update(
        {"_id": ObjectId(user_id)}, {"$push": {"sessions": inserted.inserted_id}}
    )

    return inserted.inserted_id


def list_sessions_for_user(user_id: str) -> Optional[list[models.Session]]:
    """List all sessions for a user"""

    user = find_user_by_id(user_id)
    if not user:
        return None
    res = [
        models.Session.model_validate(sessions_collection.find_one({"_id": ObjectId(session_id)}))
        for session_id in user.sessions
    ]
    return res


def get_session_info(session_id: str, user_id: str) -> Optional[models.Session]:
    """Get information on a session"""

    query = {"_id": ObjectId(session_id), "user_id": ObjectId(user_id)}
    session = sessions_collection.find_one(query)
    if session:
        return models.Session.model_validate(session)
    return None


def add_message_to_session(session_id: str, role: str, message: str) -> None:
    """Add a message to the chat"""

    sessions_collection.find_one_and_update(
        {"_id": ObjectId(session_id)},
        {
            "$push": {
                "messages": {
                    "role": role,
                    "message": message,
                    "timestamp": datetime.now(),
                }
            }
        },
    )


def delete_session(user_id: str, session_id: str) -> bool:
    """Delete a session and remove its reference from the user."""
    query = {"_id": ObjectId(session_id), "user_id": ObjectId(user_id)}
    deleted = sessions_collection.delete_one(query)

    if deleted.deleted_count:
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"sessions": ObjectId(session_id)}}
        )
        return True

    return False
