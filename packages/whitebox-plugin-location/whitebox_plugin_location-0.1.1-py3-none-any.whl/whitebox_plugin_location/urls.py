from rest_framework.routers import SimpleRouter

from .views import (
    FlightSessionLocationDataViewSet,
)


app_name = "whitebox_plugin_location"


router = SimpleRouter()


router.register(
    r"flight-session-location-data",
    FlightSessionLocationDataViewSet,
    basename="flight-session-location-data",
)

urlpatterns = router.urls
