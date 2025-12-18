from django.utils.functional import cached_property
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.exceptions import NotFound

from whitebox import import_whitebox_model
from .models import Location
from .serializers import FlightSessionLocationDataSerializer


FlightSession = import_whitebox_model("flight.FlightSession")


class FlightSessionLocationDataViewSet(GenericViewSet, ListModelMixin):
    serializer_class = FlightSessionLocationDataSerializer

    @cached_property
    def flight_session(self):
        flight_session_id = self.request.query_params.get("flight_session_id")
        if not flight_session_id:
            raise NotFound("Flight session ID not provided")

        session = FlightSession.objects.filter(pk=flight_session_id).first()
        if not session:
            raise NotFound("Flight session not found")

        return session

    def get_queryset(self):
        flight_session = self.flight_session

        qs = Location.objects.filter(event__timestamp__gte=flight_session.started_at)
        if not flight_session.is_active:
            qs = qs.filter(event__timestamp__lte=flight_session.ended_at)

        return qs
