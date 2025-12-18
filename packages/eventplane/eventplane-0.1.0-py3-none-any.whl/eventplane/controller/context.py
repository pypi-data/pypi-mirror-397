from dataclasses import dataclass
from eventplane.event.model import Event


@dataclass(frozen=True)
class ControllerContext:
    event: Event
    now: float
