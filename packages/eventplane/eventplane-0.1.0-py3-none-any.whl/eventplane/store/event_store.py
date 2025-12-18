from typing import AsyncIterator, Optional
from uuid import UUID
import json

from eventplane.event.model import Event, EventModel
from sb_utils import sb_table
from apps.organization.models import Organization, OrganizationStatus


class EventStore:
    def __init__(self, db = None):
        self.db = db

    async def append(self, event: Event) -> None:
        """
        Append event to store (immutable).
        """
        sb_table(EventModel).insert(event.model_dump(mode="json"))

        print(event)


        

    async def load(
        self,
        *,
        tenant_id: UUID,
        after_seq: int = 0,
        limit: int = 1000,
    ) -> AsyncIterator[Event]:
        """
        Load events for replay.
        """
        rows = await self.db.fetch(
            """
            SELECT *
            FROM events
            WHERE tenant_id = $1
              AND seq > $2
            ORDER BY seq ASC
            LIMIT $3
            """,
            tenant_id,
            after_seq,
            limit,
        )

        for row in rows:
            yield self._row_to_event(row)

    async def load_aggregate(
        self,
        *,
        tenant_id: UUID,
        aggregate_type: str,
        aggregate_id: UUID,
    ) -> AsyncIterator[Event]:
        """
        Load events for a single aggregate.
        """
        rows = await self.db.fetch(
            """
            SELECT *
            FROM events
            WHERE tenant_id = $1
              AND aggregate_type = $2
              AND aggregate_id = $3
            ORDER BY seq ASC
            """,
            tenant_id,
            aggregate_type,
            aggregate_id,
        )

        for row in rows:
            yield self._row_to_event(row)

    def _row_to_event(self, row) -> Event:
        return Event(
            id=row["id"],
            tenant_id=row["tenant_id"],
            aggregate_type=row["aggregate_type"],
            aggregate_id=row["aggregate_id"],
            event_type=row["event_type"],
            event_version=row["event_version"],
            spec=row["spec"],
            status=row["status"],
            finalizers=row["finalizers"],
            caused_by=row["caused_by"],
            correlation_id=row["correlation_id"],
            causation_id=row["causation_id"],
        )
