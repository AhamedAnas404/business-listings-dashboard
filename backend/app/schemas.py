from typing import Literal
from pydantic import BaseModel, Field, field_validator


class ListingIn(BaseModel):
    business_name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=1000)
    phone: str | None = Field(default=None, max_length=100)
    source: str = Field(min_length=1, max_length=100)
    source_ref: str | None = Field(default=None, max_length=128)
    data_origin: Literal['real', 'sample'] = 'real'

    @field_validator('business_name', 'category', 'city', 'address', 'source', mode='before')
    @classmethod
    def strip_required(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator('phone', 'source_ref', mode='before')
    @classmethod
    def blank_to_none(cls, value):
        if value is None:
            return None
        return value.strip() or None if isinstance(value, str) else value


class BulkInsert(BaseModel):
    listings: list[ListingIn] = Field(min_length=1, max_length=5000)
