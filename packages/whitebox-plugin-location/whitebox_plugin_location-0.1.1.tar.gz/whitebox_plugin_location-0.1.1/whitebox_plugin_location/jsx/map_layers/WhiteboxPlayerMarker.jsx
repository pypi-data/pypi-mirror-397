import { useEffect, useState } from "react";
import { Marker } from "react-leaflet";
import useLocationDataStore from "../stores/location_data";

const { importWhiteboxStateStore, withStateStore } = Whitebox;

const WhiteboxPlayerMarkerToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const mode = useMissionControlStore((state) => state.mode);
  const onMissionControlEvent = useMissionControlStore((state) => state.on);
  const locationData = useLocationDataStore((state) => state.locationData);

  // In the beginning, we don't have the location for the very exact moment when
  // the flight started, so we're going to use the very first one for the actual
  // starting location from index 0
  const [activePositionIndex, setActivePositionIndex] = useState(0);

  useEffect(() => {
    if (mode !== "playback") return;

    return onMissionControlEvent("playback.time", (time, unixTime) => {
      // Same here as for the initialization, in case we can't ascertain from
      // the timestamp, we go for index 0 by default, ensuring that we always
      // have a location, even when seeking to beginning
      let latest = 0;

      for (let i = 0; i < locationData.length; i++) {
        const timestamp = new Date(locationData[i].timestamp);
        if (timestamp <= unixTime) {
          latest = i;
        }
      }

      setActivePositionIndex(latest);
    });
  }, [mode, locationData, onMissionControlEvent]);

  // Only render in playback mode
  if (mode !== "playback") return null;

  // When we don't have location data ready yet, just don't render anything
  if (locationData.length === 0) return null;

  const currentPosition = locationData[activePositionIndex];
  const coordinates = [currentPosition.latitude, currentPosition.longitude];

  return (
      <Marker position={coordinates} />
  );
};

const WhiteboxPlayerMarker = withStateStore(
  WhiteboxPlayerMarkerToWrap,
  ["flight.mission-control"],
)

export { WhiteboxPlayerMarker };
export default WhiteboxPlayerMarker;
