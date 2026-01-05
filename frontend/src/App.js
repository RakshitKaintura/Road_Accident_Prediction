import React, { useState } from "react";
import axios from "axios";
import { GoogleMap, LoadScript, Marker, InfoWindow } from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "100vh",
};

const center = {
  lat: 40.7128,
  lng: -74.0060, // NYC
};

function riskColor(level) {
  if (level === 2) return "🔴 Fatal Risk";
  if (level === 1) return "🟠 Injury Risk";
  return "🟢 Low Risk";
}

function App() {
  const [marker, setMarker] = useState(null);
  const [risk, setRisk] = useState(null);

  const handleClick = async (e) => {
    const lat = e.latLng.lat();
    const lon = e.latLng.lng();

    setMarker({ lat, lng: lon });
    setRisk(null);

    try {
      const res = await axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/predict`,
        { params: { lat, lon } }
      );
      setRisk(res.data);
    } catch (err) {
      alert("Backend not reachable");
    }
  };

  return (
    <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={center}
        zoom={11}
        onClick={handleClick}
      >
        {marker && (
          <Marker position={marker}>
            {risk && (
              <InfoWindow>
                <div>
                  <h3>{riskColor(risk.risk_level)}</h3>
                  <p>No Injury: {risk.probabilities.no_injury}</p>
                  <p>Injury: {risk.probabilities.injury}</p>
                  <p>Fatal: {risk.probabilities.fatal}</p>
                </div>
              </InfoWindow>
            )}
          </Marker>
        )}
      </GoogleMap>
    </LoadScript>
  );
}

export default App;
