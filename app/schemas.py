from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostBase(BaseModel):
    category: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    password: str = Field(min_length=1, max_length=255)


class PostUpdate(PostBase):
    password: str = Field(min_length=1, max_length=255)


class PasswordVerifyRequest(BaseModel):
    password: str = Field(min_length=1, max_length=255)


class PasswordVerifyResponse(BaseModel):
    verified: bool


class PostRead(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    view_count: int
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    items: list[PostRead]
    total: int
    page: int
    page_size: int
    total_pages: int
