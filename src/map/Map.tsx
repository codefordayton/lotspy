import type { LatLngTuple } from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import MarkerClusterGroup from "react-leaflet-cluster";
import { useData } from "./datasette";

import "leaflet/dist/leaflet.css";

const DAYTON: LatLngTuple = [39.7592, -84.1936];

const hsize = 0.8;
const SOUTHEAST: LatLngTuple = [DAYTON[0] - hsize, DAYTON[1] - hsize];
const NORTHWEST: LatLngTuple = [DAYTON[0] + hsize, DAYTON[1] + hsize];

export function Map() {
  const {
    data: noorp,
    error,
    isLoading,
  } = useData<{
    agent_name: string;
    latitude: number;
    longitude: number;
  }>(`
    SELECT noorp.agent_name, parcels.longitude, parcels.latitude
    FROM noorp
    JOIN parcels ON noorp.parcel = parcels.parcel_number
  `);

  return (
    <MapContainer
      center={DAYTON}
      zoom={13}
      minZoom={10}
      style={{
        height: "100vh",
        width: "100vw",
      }}
      maxBounds={[SOUTHEAST, NORTHWEST]}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {noorp && (
        <MarkerClusterGroup chunkedLoading>
          {noorp.map((n, index) => (
            <Marker
              key={index}
              position={[n.latitude, n.longitude]}
              title={n.agent_name}
            >
              <Popup>
                <div>
                  <h2>{n.agent_name}</h2>
                  <p>Parcel:</p>
                </div>
              </Popup>
            </Marker>
          ))}
        </MarkerClusterGroup>
      )}
    </MapContainer>
  );
}
