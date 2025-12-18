from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID


@dataclass(frozen=True)
class ControllerDecision:
    status: Dict
    finalizer: str
    completed: bool = True

    emit_event_type: Optional[str] = None
    emit_spec: Optional[Dict] = None    

    aggregate_id: Optional[UUID] = None
