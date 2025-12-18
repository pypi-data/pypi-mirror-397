import { useEffect } from "react";
import useLocationDataStore from "./stores/location_data";

const {
  importWhiteboxStateStore,
  withStateStore,
} = Whitebox;

const FlightLocationSyncServiceComponentToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const onMissionControlEvent = useMissionControlStore((state) => state.on);

  const fetchLocationDataForFlightSession = useLocationDataStore(
      (state) => state.fetchLocationDataForFlightSession
  );
  const addPosition = useLocationDataStore((state) => state.addPosition);
  const clearData = useLocationDataStore((state) => state.clear);

  useEffect(() => {
    return onMissionControlEvent("mode", (mode, flightSession) => {
      // When moving into flight mode without an active flight session, clear
      // data so nothing is displayed or kept in RAM
      if (!flightSession) {
        clearData();
        return;
      }

      fetchLocationDataForFlightSession(flightSession);
    });
  }, []);

  useEffect(() => {
    return Whitebox.sockets.addEventListener("flight", "message", (event) => {
      // Only take actual location data is flight is in progress. State checked
      // directly without subscription
      const {
        mode,
        activeFlightSession,
      } = useMissionControlStore.getState();

      if (mode !== "flight" || !activeFlightSession)
        return;

      const data = JSON.parse(event.data);

      if (data.type !== "location.update")
        return;

      const location = data.location;
      const positionData = {
        latitude: location.latitude,
        longitude: location.longitude,
      };
      addPosition(positionData);
    })
  });

  return null;
}

const FlightLocationSyncServiceComponent = withStateStore(
  FlightLocationSyncServiceComponentToWrap,
  ["flight.mission-control"],
)

export { FlightLocationSyncServiceComponent };
export default FlightLocationSyncServiceComponent;
