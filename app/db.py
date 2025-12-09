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
    db = None
else:
    db: Database = client.get_database(db_name)


def create_user(user_data: models.User) -> InsertOneResult:
    return db.users.insert_one(
        {
            "username": user_data.username,
            "password_hash": user_data.password_hash,
        }
    )


def find_user_by_username(username: str):
    return db.users.find_one({"username": username})


def find_user_by_id(user_id: str | ObjectId):
    if isinstance(user_id, str):
        return db.users.find_one({"_id": ObjectId(user_id)})
    return db.users.find_one({"_id": user_id})


def create_session(session_id: str, user_id: str) -> InsertOneResult:
    return db.sessions.insert_one(
        {
            "session_id": session_id,
            "user_id": user_id,
            "messages": [],
            "files": [],
        }
    )


def list_sessions_for_user(user_id: str) -> list:
    return list(db.sessions.find({"user_id": user_id}))


def get_session(session_id: str, user_id: str | None = None):
    query = {"session_id": session_id}
    if user_id is not None:
        query["user_id"] = user_id
    return db.sessions.find_one(query)


def add_message_to_session(session_id: str, role: str, message: str) -> UpdateResult:
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
