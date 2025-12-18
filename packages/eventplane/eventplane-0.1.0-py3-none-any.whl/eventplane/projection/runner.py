# eventplane/projection/runner.py

class ProjectionRunner:

    def __init__(self, projections, store):
        self.projections = projections
        self.store = store

    async def replay(self, tenant_id):
        async for event in self.store.iter_events(tenant_id):
            await self._dispatch(event)

    async def handle(self, event):
        await self._dispatch(event)

    async def _dispatch(self, event):
        for proj in self.projections:
            if proj.can_handle(event):
                await proj.apply(event)
