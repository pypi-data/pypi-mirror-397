from rest_framework import serializers

from .models import Location


class FlightSessionLocationDataSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source="event.timestamp")

    class Meta:
        model = Location
        fields = [
            "latitude",
            "longitude",
            "altitude",
            "timestamp",
        ]
