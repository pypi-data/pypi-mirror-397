from typing import Type

from datetime import datetime

import reversion
from asgiref.sync import sync_to_async

from event.models import EventLog
from whitebox.events import event_emitter
from .models import Location


class LocationService:
    """
    Service class for handling location-related operations.
    """

    @classmethod
    @sync_to_async
    def update_location(
        cls,
        latitude: float,
        longitude: float,
        altitude: float,
        timestamp: datetime,
    ) -> Location:
        """
        Update the location in the database.

        Parameters:
            latitude: The latitude of the location.
            longitude: The longitude of the location.
            altitude: The altitude of the location.
            timestamp: The timestamp of the location.

        Returns:
            The Location object that was created.
        """

        with reversion.create_revision():
            event = EventLog.objects.create(timestamp=timestamp)

            location = Location.objects.create(
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                event=event,
            )
            event.event_source = location
            reversion.set_comment("Location updated")

        return location

    @classmethod
    @sync_to_async
    def get_latest_location(cls: Type[Location]) -> Location:
        """
        Get the latest location from the database.
        """

        return Location.objects.latest("event__timestamp")

    @classmethod
    async def emit_location_update(
        cls,
        latitude: float,
        longitude: float,
        altitude: float,
    ) -> None:
        """
        Emit a location update event to all connected clients and plugins who are listening for location updates.

        Parameters:
            latitude: The latitude of the location.
            longitude: The longitude of the location.
            altitude: The altitude of the location.
        """
        data = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
        }

        await event_emitter.emit("location.update", data)
