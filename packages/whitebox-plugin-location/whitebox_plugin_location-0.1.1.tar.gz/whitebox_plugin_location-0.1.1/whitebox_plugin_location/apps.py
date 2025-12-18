from django.apps import AppConfig

from whitebox.events import event_registry
from plugin.registry import model_registry


class WhiteboxPluginLocationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "whitebox_plugin_location"
    verbose_name = "Whitebox Plugin Location"

    def ready(self):
        from .handlers import LocationUpdateHandler
        from .models import Location

        event_registry.register_event("location.update", LocationUpdateHandler)
        model_registry.register("location.Location", Location)
