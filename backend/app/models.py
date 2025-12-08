from typing import List

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionCreateResponse(BaseModel):
    session_id: str


class SessionSummary(BaseModel):
    session_id: str


class SessionListResponse(BaseModel):
    sessions: List[SessionSummary]


class ChatRequest(BaseModel):
    session_id: str
    message: str


class Message(BaseModel):
    role: str
    message: str
    timestamp: str


class ChatResponse(BaseModel):
    session_id: str
    messages: List[Message]
