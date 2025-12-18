from django.db import models
from reversion import register


@register()
class Location(models.Model):
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    altitude = models.DecimalField(max_digits=12, decimal_places=7)
    event = models.ForeignKey("event.EventLog", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location({self.latitude}, {self.longitude}, {self.altitude})"
