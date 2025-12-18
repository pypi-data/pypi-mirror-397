import whitebox


class WhiteboxPluginLocation(whitebox.Plugin):
    name = "Location"

    exposed_component_map = {
        "service-component": {
            "flight-location-sync": "FlightLocationSyncServiceComponent",
        },
        "map-layer": {
            "flight-path": "map_layers/WhiteboxFlightPath",
            "whitebox-player-marker": "map_layers/WhiteboxPlayerMarker",
        },
    }

    plugin_url_map = {
        "location.flight-session-location-data": "whitebox_plugin_location:flight-session-location-data-list",
    }

    def get_plugin_classes_map(self):
        from .services import LocationService

        return {
            "location.LocationService": LocationService,
        }


plugin_class = WhiteboxPluginLocation
