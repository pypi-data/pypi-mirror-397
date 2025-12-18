import asyncio
import json
import logging
from typing import Callable, Awaitable

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg

from eventplane.event.model import Event

logger = logging.getLogger("eventplane.consumer")


class EventConsumer:
    """
    NATS-based Event Consumer for Eventplane

    Responsibilities:
    - Subscribe to subjects
    - Deserialize events
    - Delegate handling to runtime
    - NEVER mutate events
    """

    def __init__(
        self,
        nc: NATS,
        subject: str,
        handler: Callable[[Event], Awaitable[None]],
        queue_group: str | None = None,
    ):
        """
        :param nc: Connected NATS client
        :param subject: Subscription subject (wildcards allowed)
        :param handler: Async function that handles Event
        :param queue_group: Optional queue group for load balancing
        """
        self.nc = nc
        self.subject = subject
        self.handler = handler
        self.queue_group = queue_group
        self._sub = None

    async def start(self):
        """
        Start consuming events from NATS.
        """

        async def _on_message(msg: Msg):
            try:
                event = self._decode_event(msg)
            except Exception as exc:
                logger.exception(
                    "Failed to decode event from NATS",
                    extra={"subject": msg.subject},
                )
                return

            try:
                await self.handler(event)
            except Exception as exc:
                # IMPORTANT:
                # - Do NOT ack / retry here
                # - Eventplane relies on DB + replay
                logger.exception(
                    "Error while handling event",
                    extra={
                        "event_id": str(event.id),
                        "event_type": event.event_type,
                        "aggregate_id": str(event.aggregate_id),
                    },
                )

        logger.info(
            "Subscribing to NATS",
            extra={
                "subject": self.subject,
                "queue_group": self.queue_group,
            },
        )

        self._sub = await self.nc.subscribe(
            subject=self.subject,
            queue=self.queue_group,
            cb=_on_message,
        )

    async def stop(self):
        """
        Gracefully stop consuming.
        """
        if self._sub:
            await self._sub.unsubscribe()
            self._sub = None

    @staticmethod
    def _decode_event(msg: Msg) -> Event:
        """
        Deserialize NATS message into Eventplane Event.
        """
        payload = msg.data.decode("utf-8")
        return Event.model_validate_json(payload)
