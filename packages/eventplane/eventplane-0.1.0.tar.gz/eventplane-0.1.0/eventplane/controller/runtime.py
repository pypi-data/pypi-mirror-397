# eventplane/controller/runtime.py
import time
from eventplane.controller.context import ControllerContext
#from eventplane.event.envelope import mutate_event
from eventplane.event.mutate import mutate_event
from eventplane.store.event_store import EventStore




class ControllerRuntime:

    def __init__(self, controllers, producer, event_store):
        self.controllers = controllers
        self.producer = producer
        self.event_store: EventStore = event_store

    async def handle(self, event):
        for controller in self.controllers:
            if not controller.can_handle(event):
                continue

            ctx = ControllerContext(event=event, now=time.time())
            controller.authorize(ctx)

            decision = controller.reconcile(ctx)
            if not decision:
                continue

            new_event_type = decision.emit_event_type if decision.emit_event_type else f"{event.event_type}.{decision.finalizer}"
            
                
            new_event = mutate_event(
                source=event,
                event_type=new_event_type,
                status=decision.status,
                finalizer=decision.finalizer,
                completed=decision.completed,
                aggregate_id=decision.aggregate_id
            )     

            await self.event_store.append(new_event)

            await self.producer.publish(new_event)
