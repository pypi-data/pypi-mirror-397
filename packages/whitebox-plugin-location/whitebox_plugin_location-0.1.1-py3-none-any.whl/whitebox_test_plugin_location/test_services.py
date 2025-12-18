from unittest.mock import patch, MagicMock, AsyncMock
from django.test import TestCase
from django.utils import timezone

from whitebox_plugin_location.services import LocationService
from whitebox.events import event_emitter


class TestLocationService(TestCase):
    @patch("whitebox_plugin_location.services.reversion.create_revision")
    @patch("whitebox_plugin_location.services.reversion.set_comment")
    @patch("whitebox_plugin_location.services.EventLog.objects.create")
    @patch("whitebox_plugin_location.services.Location.objects.create")
    async def test_update_location(
        self,
        mock_location_create,
        mock_eventlog_create,
        mock_set_comment,
        mock_create_revision,
    ):
        timestamp = timezone.now()
        mock_event = MagicMock()
        mock_location = MagicMock()
        mock_eventlog_create.return_value = mock_event
        mock_location_create.return_value = mock_location

        mock_revision_context = MagicMock()
        mock_create_revision.return_value = mock_revision_context
        mock_revision_context.__enter__ = MagicMock()
        mock_revision_context.__exit__ = MagicMock()

        location = await LocationService.update_location(
            37.7749,
            -122.4194,
            10.0,
            timestamp,
        )

        mock_create_revision.assert_called_once()
        mock_eventlog_create.assert_called_once_with(timestamp=timestamp)
        mock_location_create.assert_called_once_with(
            latitude=37.7749,
            longitude=-122.4194,
            altitude=10.0,
            event=mock_event,
        )
        mock_set_comment.assert_called_once_with("Location updated")
        self.assertEqual(location, mock_location)

    @patch("whitebox_plugin_location.services.Location.objects.latest")
    async def test_get_latest_location(self, mock_latest):
        mock_location = MagicMock()
        mock_latest.return_value = mock_location

        location = await LocationService.get_latest_location()

        mock_latest.assert_called_once_with("event__timestamp")
        self.assertEqual(location, mock_location)

    @patch.object(event_emitter, "emit", new_callable=AsyncMock)
    async def test_emit_location_update(self, mock_emit):
        await LocationService.emit_location_update(37.7749, -122.4194, 10.0)

        mock_emit.assert_awaited_once_with(
            "location.update",
            {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "altitude": 10.0,
            },
        )
