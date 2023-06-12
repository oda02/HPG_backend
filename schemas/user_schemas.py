from typing import Optional

from pydantic import BaseModel, HttpUrl


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: str
    real_surname: str
    vk_link: HttpUrl
    description: str


class UserLogin(BaseModel):
    username: str
    password: str
