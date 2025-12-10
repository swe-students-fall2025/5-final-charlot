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


class Session(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: PyObjectId
    messages: list
    files: list
