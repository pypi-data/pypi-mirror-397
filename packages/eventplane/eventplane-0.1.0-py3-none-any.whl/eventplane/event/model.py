from pydantic import BaseModel
from sqlalchemy import text, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

from ..models import UUIDMixin, TimestampMixin


class Event(BaseModel):
    id: UUID
    tenant_id: UUID

    kind: str

    aggregate_type: str
    aggregate_id: Optional[UUID]

    event_type: str
    event_version: int = 1

    spec: Dict[str, Any]
    status: Optional[Dict[str, Any]] = None
    finalizers: Optional[Dict[str, Any]] = None

    caused_by: Dict[str, Any]

    correlation_id: Optional[UUID]
    causation_id: Optional[UUID]


class EventModel(UUIDMixin, TimestampMixin, Event, SQLModel, table=True):
    __tablename__ = "events"

    spec: dict = Field(default=None, sa_column=Column(JSONB))
    status: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    finalizers: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    caused_by: dict = Field(default=None, sa_column=Column(JSONB))    
            