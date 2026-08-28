import { useEffect, useMemo, useRef, useState } from "react";
import { GoogleMap, HeatmapLayer, useLoadScript } from "@react-google-maps/api";

const center = { lat: 12.9716, lng: 77.5946 };
const backendUrl = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";
const mapsApiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;
const MAP_LIBRARIES = ["visualization"];
const REQUEST_TIMEOUT_MS = 15000;

function formatUtc(value) {
  if (!value) return "--";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "--";
  return date.toLocaleString();
}

export default function RiskHeatmap() {
  const [rawPoints, setRawPoints] = useState([]);
  const [meta, setMeta] = useState({
    generated_at: null,
    total_points: 0,
    source_points_evaluated: 0,
    threshold: 0.3,
    used_cache: false,
  });
  const [minRisk, setMinRisk] = useState(0.05);
  const [radius, setRadius] = useState(35);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inFlightControllerRef = useRef(null);

  const { isLoaded, loadError } = useLoadScript({
    googleMapsApiKey: mapsApiKey || "",
    libraries: MAP_LIBRARIES,
  });

  const loadHeatmap = async () => {
    if (inFlightControllerRef.current) {
      inFlightControllerRef.current.abort();
    }

    const controller = new AbortController();
    inFlightControllerRef.current = controller;

    const timeoutId = setTimeout(() => {
      controller.abort();
    }, REQUEST_TIMEOUT_MS);

    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${backendUrl}/heatmap`, { signal: controller.signal });
      if (!res.ok) {
        throw new Error(`Backend returned ${res.status}`);
      }

      const data = await res.json();
      if (!Array.isArray(data.points)) {
        throw new Error("Heatmap payload is missing points[]");
      }

      setRawPoints(data.points);
      setMeta({
        generated_at: data.generated_at || null,
        total_points: data.total_points || 0,
        source_points_evaluated: data.source_points_evaluated || 0,
        threshold: data.threshold ?? 0.3,
        used_cache: Boolean(data.used_cache),
      });

      if (data.error) {
        setError(data.error);
      }
    } catch (err) {
      if (err.name === "AbortError") {
        setError("Heatmap request timed out. Please try refresh again.");
      } else {
        setError("Unable to load risk heatmap data.");
      }
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
      if (inFlightControllerRef.current === controller) {
        inFlightControllerRef.current = null;
      }
    }
  };

  useEffect(() => {
    loadHeatmap();
    return () => {
      if (inFlightControllerRef.current) {
        inFlightControllerRef.current.abort();
      }
    };
  }, []);

  const filteredRawPoints = useMemo(
    () => rawPoints.filter((point) => point.risk >= minRisk),
    [rawPoints, minRisk],
  );

  const mapPoints = useMemo(() => {
    if (!isLoaded || !window.google?.maps) {
      return [];
    }

    return filteredRawPoints.map((point) => ({
      location: new window.google.maps.LatLng(point.lat, point.lng),
      weight: Math.max(1, Math.round(point.risk * 100)),
    }));
  }, [isLoaded, filteredRawPoints]);

  const handleRefresh = () => {
    loadHeatmap();
  };

  if (!mapsApiKey) {
    return <div className="status-card">Missing REACT_APP_GOOGLE_MAPS_API_KEY in frontend/.env</div>;
  }

  if (loadError) {
    return <div className="status-card">Google Maps failed to load.</div>;
  }

  return (
    <section className="dashboard">
      <header className="hero-panel">
        <p className="eyebrow">Urban Safety Intelligence</p>
        <h1>Road Accident Risk Heatmap</h1>
        <p className="hero-copy">
          Live model-backed surface showing where severe road incidents are more likely. Designed for
          proactive patrol planning and traffic safety decisions.
        </p>
      </header>

      <div className="stats-grid">
        <article className="stat-card">
          <p>Visible Risk Cells</p>
          <strong>{filteredRawPoints.length}</strong>
        </article>
        <article className="stat-card">
          <p>Evaluated Cells</p>
          <strong>{meta.source_points_evaluated}</strong>
        </article>
        <article className="stat-card">
          <p>Last Generated</p>
          <strong>{formatUtc(meta.generated_at)}</strong>
        </article>
        <article className="stat-card">
          <p>Cache Status</p>
          <strong>{meta.used_cache ? "Warm Cache" : "Fresh Compute"}</strong>
        </article>
      </div>

      <div className="controls-row">
        <label>
          Minimum Risk: <span>{minRisk.toFixed(2)}</span>
          <input
            type="range"
            min="0.05"
            max="0.95"
            step="0.01"
            value={minRisk}
            onChange={(event) => setMinRisk(Number(event.target.value))}
          />
        </label>

        <label>
          Heat Radius: <span>{radius}px</span>
          <input
            type="range"
            min="20"
            max="60"
            step="1"
            value={radius}
            onChange={(event) => setRadius(Number(event.target.value))}
          />
        </label>

        <button type="button" onClick={handleRefresh} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh Risk Surface"}
        </button>
      </div>

      {error ? <div className="status-card warning">{error}</div> : null}
      {!error && filteredRawPoints.length === 0 ? (
        <div className="status-card warning">
          No points match current minimum risk. Reduce the slider to view the full surface.
        </div>
      ) : null}

      <div className="map-panel">
        {!isLoaded ? (
          <div className="status-card">Loading map...</div>
        ) : (
          <GoogleMap
            mapContainerClassName="map-canvas"
            center={center}
            zoom={11}
            options={{
              mapTypeId: "roadmap",
              streetViewControl: false,
              fullscreenControl: true,
              rotateControl: false,
              tilt: 0,
              maxZoom: 16,
              minZoom: 10,
            }}
          >
            <HeatmapLayer
              data={mapPoints}
              options={{
                radius,
                opacity: 0.85,
                maxIntensity: 70,
                dissipating: true,
                gradient: [
                  "rgba(53, 92, 125, 0)",
                  "rgba(83, 184, 143, 1)",
                  "rgba(247, 202, 98, 1)",
                  "rgba(244, 144, 77, 1)",
                  "rgba(214, 69, 80, 1)",
                ],
              }}
            />
          </GoogleMap>
        )}
      </div>

      <footer className="legend-row">
        <span>Threshold: {meta.threshold.toFixed(2)}</span>
        <span>Low Risk</span>
        <span>Moderate</span>
        <span>Elevated</span>
        <span>Critical</span>
      </footer>
    </section>
  );
}
