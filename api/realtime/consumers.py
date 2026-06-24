from channels.generic.websocket import AsyncJsonWebsocketConsumer
from api.constants import DASHBOARD_GROUP


class DashboardConsumer(AsyncJsonWebsocketConsumer):
    """Live websocket that pushes new transaction events to open dashboards."""

    joined = False

    async def connect(self):
        """Add a logged-in dashboard to the group, reject everyone else."""
        user = self.scope.get("user")
        if user is None or not user.is_authenticated:
            await self.close(code=4401)
            return
        await self.channel_layer.group_add(DASHBOARD_GROUP, self.channel_name)
        self.joined = True
        await self.accept()

    async def disconnect(self, code):
        """Remove the dashboard from the group when it closes."""
        if self.joined:
            await self.channel_layer.group_discard(DASHBOARD_GROUP, self.channel_name)

    async def transaction_created(self, event):
        """Forward a transaction event to the dashboard."""
        await self.send_json(event["payload"])
