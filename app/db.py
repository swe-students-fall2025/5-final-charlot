"""Database operations for the app"""

import os
import pathlib
from datetime import datetime

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult

from app import models

ROOT_DIR = pathlib.Path(__file__).parent.parent
load_dotenv(ROOT_DIR / ".env", override=True)

# Connect to MongoDB

client = MongoClient(os.getenv("MONGODB_URI"))
db_name = os.getenv("MONGODB_NAME")

if not db_name:
    print("WARNING: MONGO_DB not set — running UI without DB")
    db = None  # pylint: disable=invalid-name
else:
    db: Database = client.get_database(db_name)  # pylint: disable=invalid-name


def create_user(user_data: models.User) -> InsertOneResult:
    """Create and insert a new user"""

    return db.users.insert_one(
        {
            "username": user_data.username,
            "password_hash": user_data.password_hash,
            "sessions": []
        }
    )


def find_user_by_username(username: str):
    """Find a user by username"""

    return db.users.find_one({"username": username})


def find_user_by_id(user_id: str | ObjectId):
    """Find a user by _id (either str or ObjectId)"""

    if isinstance(user_id, str):
        return db.users.find_one({"_id": ObjectId(user_id)})
    return db.users.find_one({"_id": user_id})


def create_session(user_id: str) -> InsertOneResult:
    """Create a new chat session"""

    with client.start_session() as mongo_session:
        mongo_session.start_transaction()
        res = db.sessions.insert_one(
            {
                "user_id": ObjectId(user_id),
                "messages": [],
                "files": []
            }
        )
        user = db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$push": {"sessions": res.inserted_id}}
        )
        if not user:
            mongo_session.abort_transaction()
            raise ValueError("User does not exist")
        mongo_session.commit_transaction()
    return res


def get_session(session_id: str, user_id: str):
    """Get a single session by session id"""

    query = {"session_id": session_id, "user_id": user_id}
    return db.sessions.find_one(query)


def add_message_to_session(session_id: str, role: str, message: str) -> UpdateResult:
    """Add a message to a chat session"""

    return db.sessions.update_one(
        {"session_id": session_id},
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


def add_file_to_session(session_id: str, filename: str, path: str) -> UpdateResult:
    """Add a file to a chat session"""

    return db.sessions.update_one(
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
