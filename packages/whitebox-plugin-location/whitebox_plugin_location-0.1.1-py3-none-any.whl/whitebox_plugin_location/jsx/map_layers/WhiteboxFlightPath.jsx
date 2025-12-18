import { Polyline } from "react-leaflet";
import useLocationDataStore from "../stores/location_data";

const { importWhiteboxStateStore, withStateStore } = Whitebox;

const WhiteboxFlightPathToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const mode = useMissionControlStore((state) => state.mode);
  const flightSession = useMissionControlStore((state) => state.getFlightSession());
  const locationData = useLocationDataStore((state) => state.locationData);

  if (mode !== "flight" || !flightSession || flightSession.ended_at)
    return null;

  if (locationData.length === 0) {
    return null;
  }

  const preparedData = locationData.map(
      (entry) => [entry.latitude, entry.longitude]
  );

  return <Polyline positions={preparedData}
                   pathOptions={{ color: "orange" }} />;
}

const WhiteboxFlightPath = withStateStore(
    WhiteboxFlightPathToWrap,
    ["flight.mission-control"],
)

export { WhiteboxFlightPath };
export default WhiteboxFlightPath;
