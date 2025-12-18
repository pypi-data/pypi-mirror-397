import json
import logging
from typing import Optional

from nats.aio.client import Client as NATS

from eventplane.event.model import Event

logger = logging.getLogger("eventplane.producer")


class EventProducer:
    """
    Eventplane Event Producer (Transport layer)

    Responsibilities:
    - Serialize Event
    - Publish to NATS
    - NEVER mutate or persist Event
    """

    def __init__(
        self,
        nc: NATS,
        *,
        subject_prefix: str = "eventplane",
        timeout: float = 2.0,
    ):
        """
        :param nc: Connected NATS client
        :param subject_prefix: Root subject namespace
        :param timeout: Publish timeout (best-effort)
        """
        self.nc = nc
        self.subject_prefix = subject_prefix
        self.timeout = timeout

    async def publish(self, event: Event) -> None:
        """
        Publish an Eventplane event to NATS.

        IMPORTANT:
        - Event MUST already be persisted before calling this.
        - Fire-and-forget semantics.
        """

        subject = self._build_subject(event)
        payload = event.model_dump_json().encode()

        try:
            await self.nc.publish(subject, payload)
            logger.debug(
                "Event published",
                extra={
                    "subject": subject,
                    "event_id": str(event.id),
                    "event_type": event.event_type,
                },
            )
        except Exception as exc:
            # DO NOT retry here
            # Persistence + replay guarantees correctness
            logger.exception(
                "Failed to publish event to NATS",
                extra={
                    "subject": subject,
                    "event_id": str(event.id),
                },
            )
            raise

    def _build_subject(self, event: Event) -> str:
        """
        eventplane.<tenant>.<aggregate_type>.<event_type>
        """
        return (
            f"{self.subject_prefix}."
            f"{event.kind}."
            f"{event.aggregate_type}."
            f"{event.event_type}"
        )
