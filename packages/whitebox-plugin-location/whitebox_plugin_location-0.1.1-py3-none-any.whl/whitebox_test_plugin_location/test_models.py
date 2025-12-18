import reversion

from django.test import TestCase
from django.db import models
from django.utils import timezone
from decimal import Decimal
from reversion.models import Version

from whitebox_plugin_location.models import Location
from event.models import EventLog


class LocationModelTest(TestCase):
    def setUp(self):
        self.event = EventLog.objects.create(timestamp=timezone.now())
        self.location_data = {
            "latitude": Decimal("37.774929"),
            "longitude": Decimal("-122.419416"),
            "altitude": Decimal("10.5"),
            "event": self.event,
        }
        with reversion.create_revision():
            self.location = Location.objects.create(**self.location_data)

    def test_location_creation(self):
        self.assertTrue(isinstance(self.location, Location))
        self.assertEqual(
            self.location.__str__(),
            f"Location({self.location_data['latitude']}, {self.location_data['longitude']}, {self.location_data['altitude']})",
        )

    def test_field_types(self):
        self.assertIsInstance(Location._meta.get_field("latitude"), models.DecimalField)
        self.assertIsInstance(
            Location._meta.get_field("longitude"), models.DecimalField
        )
        self.assertIsInstance(Location._meta.get_field("altitude"), models.DecimalField)
        self.assertIsInstance(Location._meta.get_field("event"), models.ForeignKey)
        self.assertIsInstance(
            Location._meta.get_field("created_at"), models.DateTimeField
        )

    def test_decimal_field_precision(self):
        for field in ["latitude", "longitude"]:
            self.assertEqual(Location._meta.get_field(field).max_digits, 10)
            self.assertEqual(Location._meta.get_field(field).decimal_places, 7)

    def test_decimal_field_precision_altitude(self):
        self.assertEqual(Location._meta.get_field("altitude").max_digits, 12)
        self.assertEqual(Location._meta.get_field("altitude").decimal_places, 7)

    def test_created_at_auto_now_add(self):
        self.assertTrue(Location._meta.get_field("created_at").auto_now_add)

    def test_meta_attributes(self):
        self.assertEqual(Location._meta.app_label, "whitebox_plugin_location")
        self.assertEqual(
            Location._meta.db_table,
            "whitebox_plugin_location_location",
        )

    def test_event_relationship(self):
        self.assertEqual(self.location.event, self.event)

    def test_reversion_registration(self):
        self.assertTrue(reversion.is_registered(Location))

    def test_location_update(self):
        new_latitude = Decimal("38.774929")
        with reversion.create_revision():
            self.location.latitude = new_latitude
            self.location.save()

        updated_location = Location.objects.get(id=self.location.id)
        self.assertEqual(updated_location.latitude, new_latitude)

    def test_reversion_history(self):
        new_latitude = Decimal("38.774929")
        with reversion.create_revision():
            self.location.latitude = new_latitude
            self.location.save()

        versions = Version.objects.get_for_object(self.location)
        self.assertEqual(versions.count(), 2)  # Original version + 1 update
        self.assertEqual(versions[0].field_dict["latitude"], new_latitude)
        self.assertEqual(
            versions[1].field_dict["latitude"], self.location_data["latitude"]
        )

    def test_event_cascade_delete(self):
        location_id = self.location.id
        self.event.delete()
        with self.assertRaises(Location.DoesNotExist):
            Location.objects.get(id=location_id)

    def test_location_deletion(self):
        location_id = self.location.id
        self.location.delete()
        with self.assertRaises(Location.DoesNotExist):
            Location.objects.get(id=location_id)
