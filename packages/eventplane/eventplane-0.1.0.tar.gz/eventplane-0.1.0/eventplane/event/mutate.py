import uuid
from typing import Optional

from eventplane.event.model import Event


def mutate_event(
    *,
    source: Event,
    event_type: str,
    status: dict,
    finalizer: str,
    completed: bool,
    aggregate_id: Optional[uuid.UUID] = None,
) -> Event:
    """
    Create a NEW event derived from a source event.
    """

    kind = "internal"
    if completed:
        kind = "fact"

    # Determine aggregate_id
    if aggregate_id is None:
        aggregate_id = source.aggregate_id

    # correlation_id rules
    correlation_id = source.correlation_id or source.id

    return Event(
        id=uuid.uuid4(),
        tenant_id=source.tenant_id,

        kind=kind,

        aggregate_type=source.aggregate_type,
        aggregate_id=aggregate_id,

        event_type=event_type,
        event_version=source.event_version,

        spec=source.spec,
        status={**(source.status or {}), **status},
        finalizers={
            **(source.finalizers or {}),
            finalizer: {
                "completed": completed
            },
        },

        caused_by={
            "event_id": str(source.id),
            "controller": finalizer,
        },

        correlation_id=correlation_id,
        causation_id=source.id,
    )
