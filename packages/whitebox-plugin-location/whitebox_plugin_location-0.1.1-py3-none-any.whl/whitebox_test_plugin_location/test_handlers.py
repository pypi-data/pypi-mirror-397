from django.test import TestCase
from unittest.mock import patch, AsyncMock, ANY, MagicMock

from whitebox_plugin_location.handlers import (
    LocationUpdateHandler,
    channel_layer,
)


class TestLocationUpdateHandler(TestCase):
    @patch(
        "whitebox_plugin_location.handlers.LocationService.update_location",
        new_callable=AsyncMock,
    )
    async def test_handle(self, mock_update_location):
        data = {
            "latitude": 37.77,
            "longitude": -122.40,
            "altitude": 100,
        }
        sentinel = object()
        mock_update_location.return_value = sentinel

        handler = LocationUpdateHandler()
        response = await handler.handle(data)

        self.assertEqual(
            response,
            {
                "location": sentinel,
            },
        )
        mock_update_location.assert_awaited_once_with(37.77, -122.40, 100, ANY)

    @patch.object(channel_layer, "group_send")
    async def test_callback(self, mock_group_send):
        sentinel = object()
        data = {
            "latitude": sentinel,
            "longitude": sentinel,
            "altitude": sentinel,
        }
        mock_ctx = MagicMock()

        await LocationUpdateHandler.emit_location_update(data, mock_ctx)

        mock_group_send.assert_awaited_once_with(
            "flight",
            {
                "type": "location.update",
                "location": {
                    "latitude": mock_ctx["location"].latitude,
                    "longitude": mock_ctx["location"].longitude,
                    "altitude": mock_ctx["location"].altitude,
                    "timestamp": mock_ctx["location"].event.timestamp.isoformat(),
                },
            },
        )
