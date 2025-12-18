from django.test import TestCase
from django.apps import apps

from whitebox_plugin_location.apps import WhiteboxPluginLocationConfig


class TestLocationConfig(TestCase):
    def test_app_name(self):
        self.assertEqual(
            WhiteboxPluginLocationConfig.name,
            "whitebox_plugin_location",
        )

    def test_default_auto_field(self):
        self.assertEqual(
            WhiteboxPluginLocationConfig.default_auto_field,
            "django.db.models.BigAutoField",
        )

    def test_app_config_type(self):
        app_config = apps.get_app_config("whitebox_plugin_location")
        self.assertIsInstance(app_config, WhiteboxPluginLocationConfig)

    def test_app_config_label(self):
        app_config = apps.get_app_config("whitebox_plugin_location")
        self.assertEqual(app_config.label, "whitebox_plugin_location")

    def test_app_config_models_module(self):
        app_config = apps.get_app_config("whitebox_plugin_location")
        self.assertIsNotNone(app_config.models_module)
