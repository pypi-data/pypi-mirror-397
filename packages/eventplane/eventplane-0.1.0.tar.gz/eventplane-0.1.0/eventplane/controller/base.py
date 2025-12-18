from abc import ABC, abstractmethod
from typing import Set

from eventplane.controller.context import ControllerContext
from eventplane.controller.decision import ControllerDecision


class Controller(ABC):
    NAME: str = "unnamed"
    WATCH_EVENTS: Set[str] = set()

    def root_event_type(self, event_type: str) -> str:
        return event_type.split(".", 1)[0]    

    # ---- lifecycle ----

    def can_handle(self, event) -> bool:
        return (
            not self.WATCH_EVENTS
            or self.root_event_type(event.event_type) in self.WATCH_EVENTS
        )
        #return not self.WATCH_EVENTS or event.event_type in self.WATCH_EVENTS

    def authorize(self, ctx: ControllerContext) -> None:
        """
        RBAC hook.
        Raise exception if not authorized.
        """
        return None

    @abstractmethod
    def reconcile(self, ctx: ControllerContext) -> ControllerDecision | None:
        """
        Return a decision that will produce a NEW event.
        """
        raise NotImplementedError
