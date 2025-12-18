import { useEffect } from "react";

const { importWhiteboxStateStore, withStateStore } = Whitebox;

const SetMapIconServiceComponentToWrap = () => {
  const useMapStore = importWhiteboxStateStore("map");
  const setWhiteboxMarkerIcon = useMapStore(
    (state) => state.setWhiteboxMarkerIcon
  );

  useEffect(() => {
    setWhiteboxMarkerIcon({
      iconURL: Whitebox.api.getStaticUrl(
        "whitebox_plugin_map_icons/assets/plane.svg"
      ),
      isRotating: true,
      initialRotation: 90,
    });
  }, [setWhiteboxMarkerIcon]);

  return null;
};

const SetMapIconServiceComponent = withStateStore(
  SetMapIconServiceComponentToWrap,
  ["map"]
);

export { SetMapIconServiceComponent };
export default SetMapIconServiceComponent;
