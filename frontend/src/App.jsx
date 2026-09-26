import { useEffect, useState } from "react";
import { CircleMarker, MapContainer, Polyline, Popup, TileLayer } from "react-leaflet";

const DEFAULT_ANALYSIS = { radius_miles: 25, minimum_overlap_days: 7 };

async function getJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`Request failed: ${response.status}`);
  return response.json();
}

function priorityClass(priority) {
  return `priority priority-${priority.toLowerCase()}`;
}

function App() {
  const [projects, setProjects] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [settings, setSettings] = useState(DEFAULT_ANALYSIS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadProjects() {
    setProjects(await getJson("/api/projects"));
  }

  async function analyze() {
    setLoading(true);
    setError("");
    try {
      const result = await getJson("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      setAnalysis(result);
      setSelectedOpportunity(result.opportunities[0] ?? null);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProjects().catch((requestError) => setError(requestError.message));
    analyze();
  }, []);

  const projectById = Object.fromEntries(projects.map((project) => [project.id, project]));

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">GRID OPERATIONS / 2027 PLANNING</p>
          <h1>Grid<span>Sync</span></h1>
        </div>
        <div className="status"><i /> DEMO DATA ACTIVE</div>
      </header>

      <section className="control-strip">
        <div><strong>Coordination scan</strong><span>Compare public construction plans across utility boundaries.</span></div>
        <label>Radius
          <select value={settings.radius_miles} onChange={(event) => setSettings({ ...settings, radius_miles: Number(event.target.value) })}>
            <option value="5">5 miles</option><option value="10">10 miles</option><option value="25">25 miles</option>
          </select>
        </label>
        <label>Minimum overlap
          <select value={settings.minimum_overlap_days} onChange={(event) => setSettings({ ...settings, minimum_overlap_days: Number(event.target.value) })}>
            <option value="7">7 days</option><option value="14">14 days</option><option value="30">30 days</option>
          </select>
        </label>
        <button className="analyze-button" onClick={analyze} disabled={loading}>{loading ? "Scanning..." : "Analyze Projects"}</button>
      </section>

      {error && <div className="error-banner">Backend connection unavailable: {error}</div>}

      <section className="stats-grid">
        <Stat label="Projects analyzed" value={analysis?.projects_analyzed ?? "—"} />
        <Stat label="Utilities compared" value={analysis?.utilities_compared ?? "—"} />
        <Stat label="Opportunities found" value={analysis?.opportunities_found ?? "—"} />
        <Stat label="High priority" value={analysis?.high_priority_opportunities ?? "—"} accent />
      </section>

      <section className="workspace-grid">
        <div className="map-panel panel">
          <div className="panel-heading"><div><p className="eyebrow">LIVE PROJECT MAP</p><h2>Construction proximity</h2></div><span className="legend"><b className="north-dot" /> North <b className="south-dot" /> South</span></div>
          <MapContainer center={[26.2, -80.14]} zoom={10} scrollWheelZoom className="map">
            <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {projects.map((project) => <CircleMarker key={project.id} center={[project.latitude, project.longitude]} radius={8} pathOptions={{ color: project.utility.includes("North") ? "#29b6a6" : "#ffb454", fillOpacity: 0.9 }}><Popup><strong>{project.project_name}</strong><br />{project.utility}<br />{project.start_date} to {project.end_date}</Popup></CircleMarker>)}
            {analysis?.opportunities.map((opportunity) => { const a = projectById[opportunity.project_a_id]; const b = projectById[opportunity.project_b_id]; return a && b ? <Polyline key={`${a.id}-${b.id}`} positions={[[a.latitude, a.longitude], [b.latitude, b.longitude]]} pathOptions={{ color: opportunity.priority === "HIGH" ? "#ff6b5f" : "#ffd166", weight: opportunity.priority === "HIGH" ? 4 : 2, dashArray: "6 8" }} /> : null; })}
          </MapContainer>
        </div>

        <aside className="opportunity-panel panel">
          <div className="panel-heading"><div><p className="eyebrow">SIGNAL REVIEW</p><h2>Top opportunities</h2></div><span className="count">{analysis?.opportunities.length ?? 0}</span></div>
          <div className="opportunity-list">{analysis?.opportunities.map((opportunity) => <button className={`opportunity-row ${selectedOpportunity === opportunity ? "selected" : ""}`} key={`${opportunity.project_a_id}-${opportunity.project_b_id}`} onClick={() => setSelectedOpportunity(opportunity)}><div><span className={priorityClass(opportunity.priority)}>{opportunity.priority}</span><strong>{projectById[opportunity.project_a_id]?.project_name}</strong><small>vs {projectById[opportunity.project_b_id]?.project_name}</small></div><div className="row-metric">{opportunity.distance_miles} mi<small>{opportunity.overlap_days} overlap days</small></div></button>)}</div>
          {selectedOpportunity && <OpportunityDetail opportunity={selectedOpportunity} projectById={projectById} />}
        </aside>
      </section>

      <Timeline projects={projects} />
    </main>
  );
}

function Stat({ label, value, accent }) { return <div className={`stat ${accent ? "stat-accent" : ""}`}><span>{label}</span><strong>{value}</strong></div>; }

function OpportunityDetail({ opportunity, projectById }) {
  const projectA = projectById[opportunity.project_a_id];
  const projectB = projectById[opportunity.project_b_id];
  return <div className="detail"><div className="detail-title"><span>SELECTED SIGNAL</span><b className={priorityClass(opportunity.priority)}>{opportunity.priority}</b></div><h3>{projectA?.project_name}</h3><p className="versus">vs {projectB?.project_name}</p><div className="detail-metrics"><div><strong>{opportunity.distance_miles}</strong><span>miles apart</span></div><div><strong>{opportunity.overlap_days}</strong><span>overlap days</span></div></div><p className="why">Why it was flagged</p><p className="explanation">These sites are {opportunity.distance_miles} miles apart and their schedules {opportunity.overlap_days ? `overlap for ${opportunity.overlap_days} days` : "begin within the configured window"}. {opportunity.compatible ? "The work types may share staging, equipment, or access planning." : "The work types may still benefit from shared access planning."}</p><div className="actions"><span>Potential coordination</span><b>Shared staging</b><b>Equipment scheduling</b><b>Access planning</b></div><div className="sources"><span>PUBLIC SOURCES</span><a href={projectA?.source_url} target="_blank" rel="noreferrer">View {projectA?.utility} source ↗</a><a href={projectB?.source_url} target="_blank" rel="noreferrer">View {projectB?.utility} source ↗</a></div></div>;
}

function Timeline({ projects }) {
  if (!projects.length) return null;
  const rangeStart = new Date("2027-01-01").getTime();
  const rangeEnd = new Date("2028-03-01").getTime();
  return <section className="timeline-panel panel"><div className="panel-heading"><div><p className="eyebrow">FIELD SCHEDULE / 14 MONTH WINDOW</p><h2>Project timeline</h2></div><span className="legend">Overlapping bars reveal coordination windows</span></div><div className="timeline"><div className="month-labels"><span>JAN 2027</span><span>APR</span><span>JUL</span><span>OCT</span><span>JAN 2028</span></div>{projects.map((project) => { const start = Math.max(0, (new Date(project.start_date).getTime() - rangeStart) / (rangeEnd - rangeStart) * 100); const end = Math.min(100, (new Date(project.end_date).getTime() - rangeStart) / (rangeEnd - rangeStart) * 100); return <div className="timeline-row" key={project.id}><div className="timeline-name"><b>{project.utility.includes("North") ? "N" : "S"}</b><span>{project.project_name}</span></div><div className="timeline-track"><div className={`timeline-bar ${project.utility.includes("North") ? "bar-north" : "bar-south"}`} style={{ left: `${start}%`, width: `${Math.max(2, end - start)}%` }}><span>{project.project_type}</span></div></div></div>; })}</div></section>;
}

export default App;