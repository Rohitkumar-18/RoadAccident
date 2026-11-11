import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { getDashboard, getAccidents, getHotspots, uploadCsv, runAnalysis } from "./api";

function StatCard({ label, value, hint }) {
  return <div className="stat-card"><span>{label}</span><strong>{value ?? "—"}</strong><small>{hint}</small></div>;
}

export default function App() {
  const [dashboard, setDashboard] = useState(null);
  const [accidents, setAccidents] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function refresh() {
    try {
      const [d, a, h] = await Promise.all([getDashboard(), getAccidents(), getHotspots()]);
      setDashboard(d.data); setAccidents(a.data); setHotspots(h.data);
      setError("");
    } catch (e) {
      setError(e.response?.data?.error || "Cannot connect to Django API. Start the backend and check MySQL settings.");
    }
  }
  useEffect(() => { refresh(); }, []);

  async function handleUpload() {
    if (!file) { setError("Choose a CSV file first."); return; }
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await uploadCsv(file);
      setMessage(`Upload complete: ${result.data.created} new rows, ${result.data.skipped_duplicates} duplicates skipped.`);
      if (result.data.errors?.length) setMessage((m) => `${m} First issue: ${result.data.errors[0]}`);
      await refresh();
    } catch (e) { setError(e.response?.data?.error || "CSV upload failed."); }
    finally { setBusy(false); }
  }

  async function handleAnalysis() {
    setBusy(true); setError(""); setMessage("");
    try {
      const result = await runAnalysis();
      setMessage(`${result.data.message} Processed ${result.data.records_processed} records and found ${result.data.hotspots_found} clusters.`);
      await refresh();
    } catch (e) { setError(e.response?.data?.error || "Analysis failed."); }
    finally { setBusy(false); }
  }

  const chartData = dashboard?.by_severity?.map((x) => ({ severity: x.severity || "Unknown", accidents: x.count })) || [];
  const mapCenter = hotspots.length
    ? [hotspots[0].center_latitude, hotspots[0].center_longitude]
    : accidents.length ? [accidents[0].latitude, accidents[0].longitude] : [12.9716, 77.5946];

  return (
    <div className="app-shell">
      <header className="topbar">
        <div><div className="eyebrow">ROAD SAFETY ANALYTICS</div><h1>Accident Hotspot Predictor</h1><p>Explore historical accident patterns and identify geographic clusters.</p></div>
        <div className="header-chip">Django · React · MySQL · DBSCAN</div>
      </header>

      <main>
        {error && <div className="alert error">{error}</div>}
        {message && <div className="alert success">{message}</div>}

        <section className="stats-grid">
          <StatCard label="Total accident records" value={dashboard?.total_accidents ?? 0} hint="Records in database" />
          <StatCard label="Serious / fatal" value={dashboard?.serious_or_fatal ?? 0} hint="Based on severity field" />
          <StatCard label="Detected hotspots" value={dashboard?.hotspot_count ?? 0} hint="Latest DBSCAN analysis" />
          <StatCard label="Records displayed" value={accidents.length} hint="Latest 500 records" />
        </section>

        <section className="panel upload-panel">
          <div><h2>Dataset management</h2><p>Upload a CSV with accident dates, times and GPS coordinates.</p></div>
          <div className="upload-actions">
            <input type="file" accept=".csv,text/csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            <button onClick={handleUpload} disabled={busy}>{busy ? "Working…" : "Upload CSV"}</button>
            <button className="primary" onClick={handleAnalysis} disabled={busy}>Run hotspot analysis</button>
          </div>
          <small>Required columns: accident_id, date, time, latitude, longitude. Sample CSV is in the project's sample_data folder.</small>
        </section>

        <div className="content-grid">
          <section className="panel map-panel">
            <div className="panel-heading"><div><h2>Hotspot map</h2><p>Circle size reflects the number of accidents in each cluster.</p></div><span className="legend"><i /> Detected cluster</span></div>
            <MapContainer center={mapCenter} zoom={12} scrollWheelZoom className="map">
              <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {hotspots.map((h) => (
                <CircleMarker key={h.id} center={[h.center_latitude, h.center_longitude]}
                  radius={Math.max(8, Math.min(24, h.accident_count * 3))}
                  pathOptions={{ color: h.risk_level === "High" ? "#dc5757" : h.risk_level === "Medium" ? "#d89b36" : "#269b78", fillOpacity: 0.45 }}>
                  <Popup><b>Hotspot #{h.cluster_id + 1}</b><br />Accidents: {h.accident_count}<br />Risk: {h.risk_level}<br />Score: {h.risk_score}</Popup>
                </CircleMarker>
              ))}
            </MapContainer>
            <small className="map-note">Map uses OpenStreetMap tiles. No hotspot markers appear until analysis has been run.</small>
          </section>

          <section className="panel chart-panel">
            <h2>Accidents by severity</h2><p>Distribution of uploaded records.</p>
            {chartData.length ? <div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={chartData}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="severity" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="accidents" fill="#397c9b" radius={[5,5,0,0]} /></BarChart></ResponsiveContainer></div> : <div className="empty">Upload accident records to view analytics.</div>}
            <h2 className="subheading">Latest detected hotspots</h2>
            {hotspots.length ? <div className="hotspot-list">{hotspots.map(h => <div className="hotspot-row" key={h.id}><div><b>Cluster {h.cluster_id + 1}</b><small>{h.accident_count} accidents · {h.serious_count} serious/fatal</small></div><span className={`risk ${h.risk_level.toLowerCase()}`}>{h.risk_level}</span></div>)}</div> : <div className="empty compact">No analysis results yet.</div>}
          </section>
        </div>

        <section className="panel table-panel">
          <div className="panel-heading"><div><h2>Accident records</h2><p>Most recent records stored in the database.</p></div><span className="count">{accidents.length} shown</span></div>
          <div className="table-wrap"><table><thead><tr><th>ID</th><th>Date</th><th>Time</th><th>Latitude</th><th>Longitude</th><th>Severity</th><th>Road type</th></tr></thead>
            <tbody>{accidents.map(a => <tr key={a.id}><td>{a.accident_id}</td><td>{a.date}</td><td>{a.time}</td><td>{Number(a.latitude).toFixed(4)}</td><td>{Number(a.longitude).toFixed(4)}</td><td>{a.severity}</td><td>{a.road_type || "—"}</td></tr>)}
            {!accidents.length && <tr><td colSpan="7" className="empty-cell">No accident records yet. Upload the sample CSV to get started.</td></tr>}</tbody>
          </table></div>
        </section>
        <footer>Academic prototype · Historical pattern analysis only · Verify all data before real-world use.</footer>
      </main>
    </div>
  );
}
