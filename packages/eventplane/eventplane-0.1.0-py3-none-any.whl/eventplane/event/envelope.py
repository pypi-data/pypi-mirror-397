# eventplane/event/envelope.py
from uuid import uuid4
from eventplane.event.model import Event

def mutate_event(
    source: Event,
    *,
    event_type: str,
    status: dict,
    finalizer: str,
    completed: bool
) -> Event:

    finalizers = dict(source.finalizers or {})
    finalizers[finalizer] = "done" if completed else "failed"

    return source.model_copy(
        update={
            "id": uuid4(),
            "event_type": event_type,
            "status": status,
            "finalizers": finalizers,
            "causation_id": source.id,
        }
    )
