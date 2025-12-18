from django.utils import timezone
from channels.layers import get_channel_layer

from .services import LocationService
from whitebox.events import EventHandler


channel_layer = get_channel_layer()


class LocationUpdateHandler(EventHandler):
    """
    Handler for handling the `location.update` event.
    """

    @staticmethod
    async def emit_location_update(data, ctx):
        location = ctx["location"]

        await channel_layer.group_send(
            "flight",
            {
                "type": "location.update",
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "altitude": location.altitude,
                    "timestamp": location.event.timestamp.isoformat(),
                },
            },
        )

    default_callbacks = [
        emit_location_update,
    ]

    async def handle(self, data):
        location = await LocationService.update_location(
            data["latitude"],
            data["longitude"],
            data["altitude"],
            timezone.now(),
        )

        return {
            "location": location,
        }
