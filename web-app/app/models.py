"""Models used throughout the code"""

# pylint: disable=C0115

from typing import Annotated, Optional

from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class UserCreate(BaseModel):
    username: str
    password: str


class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    username: str
    password_hash: str
    sessions: Optional[list[PyObjectId]] = None


class SessionCreateResponse(BaseModel):
    session_id: str


class SessionSummary(BaseModel):
    session_id: str


class SessionListResponse(BaseModel):
    sessions: list[SessionSummary]


class ChatRequest(BaseModel):
    session_id: str
    message: str


class Message(BaseModel):
    role: str
    message: str
    timestamp: str


class ChatResponse(BaseModel):
    session_id: str
    messages: list[Message]
