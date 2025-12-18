from datetime import datetime
from eventplane.utils import utc_now
from sqlalchemy import text, Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel
from typing import Optional, Any
from uuid import UUID
from ..utils import generate_uuid


class MetaMixin(SQLModel):
    meta: Optional[dict] = Field(
        default={},
        sa_type=JSONB
    )

    class Config:
        arbitrary_types_allowed = True    


class TimestampMixin(SQLModel):
    created_at: datetime = Field(
        default_factory=utc_now,
        nullable=False,
        sa_column_kwargs={
            "server_default": text("(now() at time zone 'utc')")
        },
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, 
        nullable=False,
        sa_column_kwargs={
            "server_default": text("(now() at time zone 'utc')")
        },      
    )
    deleted_at: Optional[datetime] = Field(
        default=None, 
        nullable=True
    )
    
    class Config:
        arbitrary_types_allowed = True


class UUIDMixin(SQLModel):  
    id: UUID = Field(default_factory=generate_uuid, nullable=False, primary_key=True, 
                     sa_column_kwargs={"server_default": text("gen_random_uuid()")})  
    
    class Config:
        arbitrary_types_allowed = True    

