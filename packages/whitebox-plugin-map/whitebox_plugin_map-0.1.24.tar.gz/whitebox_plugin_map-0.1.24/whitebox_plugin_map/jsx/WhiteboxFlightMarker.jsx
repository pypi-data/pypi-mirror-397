import { useEffect, useRef } from "react";
import { Marker, useMap } from "react-leaflet";
import useMapStore from "./stores/map";

import './utils/leaflet_patch.js';

const { importWhiteboxStateStore, withStateStore } = Whitebox;

const WhiteboxFlightMarkerToWrap = () => {
  const useMissionControlStore = importWhiteboxStateStore("flight.mission-control");
  const mode = useMissionControlStore((state) => state.mode);

  const map = useMap();

  const whiteboxCoordinates = useMapStore((state) => state.whiteboxCoordinates);
  const setWhiteboxMarkerRef = useMapStore((state) => state.setWhiteboxMarkerRef);

  const defaultFollowZoom = useMapStore((state) => state.defaultFollowZoom);
  const followShouldZoomIn = useMapStore((state) => state.followShouldZoomIn);
  const follow = useMapStore((state) => state.follow);
  const setFollow = useMapStore((state) => state.setFollow);

  const markerRef = useRef(null);

  // When the component mounts, we set the marker reference in the store and
  // update it every time the marker reference changes.
  useEffect(() => {
    setWhiteboxMarkerRef(markerRef);
  }, [setWhiteboxMarkerRef, markerRef.current]);

  useEffect(() => {
    if (!whiteboxCoordinates) return;

    // Animate the map
    if (follow) {
      // Undefined as the default value means that the map will not zoom in
      const followZoom = followShouldZoomIn ? defaultFollowZoom : undefined;
      // const followZoom = defaultFollowZoom;
      map.flyTo(whiteboxCoordinates, followZoom);

      // Set the shouldZoomIn to false, so that the choice doesn't persist
      setFollow(follow, false);
    }

    // Move the marker without the full re-render
    if (markerRef.current) {
      markerRef.current.setLatLng(whiteboxCoordinates);
    }
  }, [map, whiteboxCoordinates]);

  // Playback mode is handled with the marker located in the `location` plugin,
  // where this component will be migrated to as well in the future
  if (mode !== "flight") return null;

  // If the marker location does not exist, do not render anything
  if (!whiteboxCoordinates) return null;

  return (
      <Marker
        position={whiteboxCoordinates}
        ref={markerRef}
        eventHandlers={{
          click: () => {
            map.setView(whiteboxCoordinates, defaultFollowZoom);
            setFollow(true);
          },
        }}
      />
  );
};

const WhiteboxFlightMarker = withStateStore(
  WhiteboxFlightMarkerToWrap,
  ["flight.mission-control"],
);

export { WhiteboxFlightMarker };
export default WhiteboxFlightMarker;
