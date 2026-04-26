from __future__ import annotations

from pydantic import BaseModel


class WorkerCreate(BaseModel):
    name: str | None = None
    location: str
    country_code: str | None = None
    raw_experience: str


class WorkerResponse(BaseModel):
    id: int
    name: str | None
    location: str
    country_code: str | None = None
    raw_experience: str

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    location: str
    country_code: str | None = None
    description: str


class JobResponse(BaseModel):
    id: int
    title: str
    location: str
    country_code: str | None = None
    description: str

    class Config:
        from_attributes = True
