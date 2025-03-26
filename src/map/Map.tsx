import type { LatLngTuple } from "leaflet";
import { MapContainer, TileLayer } from "react-leaflet";

import "leaflet/dist/leaflet.css";

const DAYTON: LatLngTuple = [39.7592, -84.1936];

const hsize = 0.2
const SOUTHEAST: LatLngTuple = [DAYTON[0] - hsize, DAYTON[1] - hsize];
const NORTHWEST: LatLngTuple = [DAYTON[0] + hsize, DAYTON[1] + hsize];

export function Map() {
  return (
    <MapContainer
      center={DAYTON}
      zoom={13}
      minZoom={10}
      style={{
        height: "100vh",
        width: "100vw",
      }}
      maxBounds={[
        SOUTHEAST,
        NORTHWEST,
      ]}
      ref={(ref) => {
        console.log(ref)
      }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    </MapContainer>
  );
}
