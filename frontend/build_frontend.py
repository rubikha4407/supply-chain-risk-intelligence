import os

# --- Dashboard.jsx ---
dashboard_jsx = """
import { useState, useEffect } from 'react';
import {
  Factory,
  AlertTriangle,
  Zap,
  ShieldAlert,
  Package,
  FileCheck,
  MapPin,
  Clock,
  ArrowRight
} from 'lucide-react';
import { getDashboard, getAssessments } from '../api/client';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [dashRes, assRes] = await Promise.all([
          getDashboard(),
          getAssessments(),
        ]);
        setKpis(dashRes.data);
        setAssessments(assRes.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Loading intelligence data...</p>
      </div>
    );
  }

  // Get suppliers from assessments to map them
  const activeAlerts = assessments.filter(a => ['critical', 'warning'].includes(a.status));

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h2>Supply Chain Risk Intelligence</h2>
        <p>Real-time global monitoring and disruption prevention</p>
      </div>

      <div className="kpi-grid stagger-children">
        <KPICard icon={<Factory size={20} />} value={kpis.total_suppliers} label="Total Suppliers" color="blue" />
        <KPICard icon={<AlertTriangle size={20} />} value={kpis.at_risk_suppliers} label="Suppliers At Risk" color="amber" />
        <KPICard icon={<ShieldAlert size={20} />} value={kpis.critical_alerts} label="Critical Risks" color="red" />
        <KPICard icon={<Package size={20} />} value={`${kpis.units_at_risk || 0}`} label="Inventory At Risk" color="purple" />
        <KPICard icon={<Zap size={20} />} value={`$${(kpis.revenue_at_risk || 0).toLocaleString()}`} label="Revenue At Risk" color="red" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '20px', marginTop: '24px' }}>
        <div className="card">
          <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Global Supply Chain Risk Map</h3>
          <div style={{ height: '400px', borderRadius: '8px', overflow: 'hidden' }}>
            <MapContainer center={[20, 0]} zoom={2} style={{ height: '100%', width: '100%', background: '#0a0a0a' }}>
              <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                attribution="&copy; OpenStreetMap contributors"
              />
              {assessments.map(a => {
                const color = a.status === 'critical' ? '#ef4444' : a.status === 'warning' ? '#f59e0b' : '#10b981';
                return (
                   <CircleMarker key={a.id} center={[a.supplier.latitude, a.supplier.longitude]} radius={8} pathOptions={{ color, fillColor: color, fillOpacity: 0.7 }}>
                     <Popup>
                       <div style={{ color: '#333' }}>
                         <strong>{a.supplier.name}</strong><br/>
                         Risk: {a.status.toUpperCase()}<br/>
                         Score: {a.risk_score}
                       </div>
                     </Popup>
                   </CircleMarker>
                )
              })}
            </MapContainer>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Active Risk Alerts</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '400px', overflowY: 'auto' }}>
            {activeAlerts.length === 0 ? (
              <p style={{ color: 'var(--text-tertiary)' }}>No active alerts.</p>
            ) : activeAlerts.map(a => (
              <Link key={a.id} to={`/suppliers/${a.supplier_id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                <div style={{ padding: '12px', background: 'var(--bg-card-hover)', borderRadius: '6px', border: '1px solid var(--border)' }}>
                  <div className="flex-between mb-4">
                    <span style={{ fontSize: '13px', fontWeight: 'bold' }}>{a.event.title}</span>
                    <span className={`badge ${a.status}`}>{a.status.toUpperCase()}</span>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                    {a.supplier.name}
                  </div>
                  <div className="flex-between" style={{ fontSize: '11px', color: 'var(--text-tertiary)' }}>
                    <span>Score: {a.risk_score}</span>
                    <span>Inv: {a.inventory_runway_days}d</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      <div className="card mt-24">
        <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Supply Chain Risk Overview</h3>
        <table className="data-table">
          <thead>
            <tr>
              <th>Risk Level</th>
              <th>Suppliers</th>
              <th>Avg Inventory (Days)</th>
              <th>Avg Score</th>
            </tr>
          </thead>
          <tbody>
            {['critical', 'warning', 'monitoring', 'resolved'].map(level => {
              const group = assessments.filter(a => a.status === level);
              if (group.length === 0) return null;
              const avgInv = group.reduce((sum, a) => sum + (a.inventory_runway_days || 0), 0) / group.length;
              const avgScore = group.reduce((sum, a) => sum + a.risk_score, 0) / group.length;
              return (
                <tr key={level}>
                  <td><span className={`badge ${level}`}>{level.toUpperCase()}</span></td>
                  <td>{group.length}</td>
                  <td>{avgInv.toFixed(1)}</td>
                  <td>{avgScore.toFixed(2)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KPICard({ icon, value, label, color }) {
  return (
    <div className={`kpi-card ${color}`}>
      <div className="kpi-icon">{icon}</div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
    </div>
  );
}
"""

# --- Suppliers.jsx ---
suppliers_jsx = """
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Factory, Search } from 'lucide-react';
import { getSuppliers, getAssessments } from '../api/client';

export default function Suppliers() {
  const [suppliers, setSuppliers] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [search, setSearch] = useState('');
  
  useEffect(() => {
    Promise.all([getSuppliers(), getAssessments()]).then(([suppRes, assRes]) => {
      setSuppliers(suppRes.data);
      setAssessments(assRes.data);
    });
  }, []);

  const filtered = suppliers.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.country.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="animate-fade-in">
      <div className="page-header flex-between">
        <div>
          <h2>Suppliers</h2>
          <p>Global supplier network with risk monitoring</p>
        </div>
        <div style={{ position: 'relative' }}>
          <Search size={16} style={{ position: 'absolute', left: 12, top: 10, color: '#666' }} />
          <input 
            type="text" 
            placeholder="Search suppliers..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ padding: '8px 12px 8px 36px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--bg-card)', color: '#fff' }}
          />
        </div>
      </div>

      <table className="data-table mt-24">
        <thead>
          <tr>
            <th>Supplier</th>
            <th>Country</th>
            <th>Reliability</th>
            <th>Current Risk</th>
            <th>Inventory Days</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(s => {
            const assessment = assessments.find(a => a.supplier_id === s.id);
            const riskLevel = assessment ? assessment.status : 'monitoring';
            const invDays = assessment ? assessment.inventory_runway_days : '-';
            return (
              <tr key={s.id}>
                <td>
                  <Link to={`/suppliers/${s.id}`} style={{ color: '#fff', textDecoration: 'none', fontWeight: 'bold' }}>
                    {s.name}
                  </Link>
                </td>
                <td>{s.country}</td>
                <td>{(s.reliability_score * 100).toFixed(0)}%</td>
                <td><span className={`badge ${riskLevel}`}>{riskLevel.toUpperCase()}</span></td>
                <td>{invDays}</td>
                <td><span className={`badge ${s.is_active ? 'monitoring' : 'critical'}`}>{s.is_active ? 'NORMAL' : 'INACTIVE'}</span></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
"""

# --- SupplierDetail.jsx ---
supplier_detail_jsx = """
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getSupplier, getAssessments } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function SupplierDetail() {
  const { id } = useParams();
  const [supplier, setSupplier] = useState(null);
  const [assessment, setAssessment] = useState(null);

  useEffect(() => {
    Promise.all([getSupplier(id), getAssessments()]).then(([supRes, assRes]) => {
      setSupplier(supRes.data);
      setAssessment(assRes.data.find(a => a.supplier_id === parseInt(id)));
    });
  }, [id]);

  if (!supplier) return <div>Loading...</div>;

  // Mock burndown data for the chart based on inventory days
  const inventoryDays = assessment?.inventory_runway_days || 30;
  const data = [];
  let stock = inventoryDays * 100; // arbitrary consumption 100/day
  for(let i=0; i <= inventoryDays + 5; i++) {
    data.push({ day: `Day ${i}`, stock: Math.max(0, stock) });
    stock -= 100;
  }

  return (
    <div className="animate-fade-in">
      <h2>{supplier.name}</h2>
      <p>{supplier.country} • Tier {supplier.tier} • {(supplier.reliability_score * 100).toFixed(0)}% Reliability</p>

      {assessment && (
        <div className="card mt-24" style={{ borderLeft: `4px solid ${assessment.status === 'critical' ? 'red' : 'orange'}` }}>
          <h3>Active Disruption Alert</h3>
          <p><strong>Event:</strong> {assessment.event?.title}</p>
          <p><strong>Risk Score:</strong> {assessment.risk_score}</p>
          <p><strong>Status:</strong> <span className={`badge ${assessment.status}`}>{assessment.status.toUpperCase()}</span></p>
          <div style={{ marginTop: '12px', padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
            <p><strong>AI Explanation:</strong></p>
            <p>{assessment.ai_risk_explanation}</p>
          </div>
        </div>
      )}

      <div className="card mt-24">
        <h3>Inventory Burndown Projection</h3>
        <div style={{ height: '300px', marginTop: '20px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="day" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: 'none' }} />
              <ReferenceLine x={`Day ${inventoryDays}`} stroke="red" label="STOCKOUT" />
              <Line type="monotone" dataKey="stock" stroke="#3b82f6" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {assessment && (
        <div className="card mt-24">
          <h3>Impact Visualization</h3>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginTop: '20px', overflowX: 'auto', paddingBottom: '10px' }}>
             <div className="kpi-card blue">Event<br/><small>{assessment.event?.event_type}</small></div>
             <span>→</span>
             <div className="kpi-card amber">Supplier<br/><small>{supplier.name}</small></div>
             <span>→</span>
             <div className="kpi-card purple">Inventory<br/><small>{inventoryDays} Days</small></div>
             <span>→</span>
             <div className="kpi-card red">Revenue Risk<br/><small>Calculated internally</small></div>
          </div>
        </div>
      )}
    </div>
  );
}
"""

# --- Events.jsx ---
events_jsx = """
import { useState, useEffect } from 'react';
import { getEvents } from '../api/client';

export default function Events() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    getEvents().then(res => setEvents(res.data));
  }, []);

  return (
    <div className="animate-fade-in">
      <h2>External Events</h2>
      <p>Global events monitored by AI</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '24px' }}>
        {events.map(e => (
          <div key={e.id} className="card">
            <div className="flex-between">
              <h3 style={{ fontSize: '18px' }}>{e.event_type === 'weather' ? '🌪️' : e.event_type === 'transport' ? '🚢' : '🏭'} {e.title}</h3>
              <span className={`badge ${e.severity === 'critical' ? 'critical' : e.severity === 'high' ? 'warning' : 'monitoring'}`}>{e.severity.toUpperCase()}</span>
            </div>
            <p style={{ marginTop: '8px', color: 'var(--text-secondary)' }}>{e.description}</p>
            <div style={{ marginTop: '16px', fontSize: '12px', color: 'var(--text-tertiary)', display: 'flex', gap: '16px' }}>
              <span><strong>Location:</strong> {e.affected_country || 'Global'}</span>
              <span><strong>Radius:</strong> {e.radius_km} km</span>
              <span><strong>Date:</strong> {new Date(e.detected_at).toLocaleString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

# --- Recovery.jsx ---
recovery_jsx = """
import { useState, useEffect } from 'react';
import { getRecoveryPlans } from '../api/client';

export default function Recovery() {
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    getRecoveryPlans().then(res => setPlans(res.data));
  }, []);

  return (
    <div className="animate-fade-in">
      <h2>Recovery Plans</h2>
      <p>AI-generated mitigation strategies for active disruptions</p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '16px', marginTop: '24px' }}>
        {plans.map(p => (
          <div key={p.id} className="card" style={{ borderLeft: '4px solid var(--accent-blue)' }}>
             <div className="flex-between">
                <h3>{p.plan_name}</h3>
                <span className="badge monitoring">{p.status.toUpperCase()}</span>
             </div>
             <p style={{ marginTop: '12px', color: 'var(--text-secondary)' }}>{p.ai_summary}</p>
             
             <div style={{ marginTop: '16px', background: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '8px' }}>
               <h4 style={{ marginBottom: '8px' }}>Recommended Actions</h4>
               {p.actions.map(a => (
                 <div key={a.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border)', padding: '8px 0' }}>
                    <div>
                      <strong>{a.action_type.replace('_', ' ').toUpperCase()}</strong>
                      <p style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>{a.description}</p>
                    </div>
                    <button className="btn" style={{ padding: '6px 12px', fontSize: '12px', background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
                      Approve Action
                    </button>
                 </div>
               ))}
             </div>
          </div>
        ))}
      </div>
    </div>
  );
}
"""

# --- Simulate.jsx ---
simulate_jsx = """
import { useState, useEffect } from 'react';
import { getScenarios, runScenario, simulateEvent } from '../api/client';

export default function Simulate() {
  const [scenarios, setScenarios] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    getScenarios().then(res => setScenarios(res.data));
  }, []);

  const handleRun = async (id) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await runScenario(id);
      setResult(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <h2>Disruption Simulator</h2>
      <p>Test the intelligence engine against pre-built global scenarios.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '24px' }}>
        {scenarios.map(s => (
          <div key={s.id} className="card">
            <h3>{s.name}</h3>
            <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px', marginBottom: '16px' }}>{s.description}</p>
            <button className="btn" onClick={() => handleRun(s.id)} disabled={loading} style={{ padding: '8px 16px', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
          </div>
        ))}
      </div>

      {loading && (
         <div className="card mt-24" style={{ textAlign: 'center', padding: '40px' }}>
           <div className="spinner" style={{ margin: '0 auto 16px' }} />
           <p>Analyzing event impact, traversing BOM, and generating recovery plans...</p>
         </div>
      )}

      {result && !loading && (
        <div className="card mt-24 animate-fade-in" style={{ border: '1px solid var(--accent-blue)' }}>
           <h2>Simulation Results: {result.title}</h2>
           
           <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginTop: '20px' }}>
              <div>
                <h4>AI Event Understanding</h4>
                <ul style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px' }}>
                  <li>Type: {result.ai_understanding.event_type}</li>
                  <li>Severity: {result.ai_understanding.severity}</li>
                  <li>Location: {result.ai_understanding.affected_country}</li>
                </ul>
              </div>
              
              <div>
                <h4>Assessments ({result.assessments_count})</h4>
                {result.assessments.map(a => (
                   <div key={a.id} style={{ background: 'rgba(255,255,255,0.05)', padding: '12px', borderRadius: '4px', marginTop: '8px' }}>
                      <p><strong>Supplier ID:</strong> {a.supplier_id}</p>
                      <p><strong>Risk Score:</strong> {a.risk_score} (<span className={`badge ${a.status}`}>{a.status.toUpperCase()}</span>)</p>
                      <p><strong>Inventory Impact:</strong> {a.inventory_impact}</p>
                      <p><strong>Financial Impact:</strong> ${a.financial_impact}</p>
                      <p style={{ marginTop: '8px', fontSize: '12px' }}><strong>Explanation:</strong> {a.explanation}</p>
                      {a.recovery_recommendation && (
                        <p style={{ marginTop: '8px', fontSize: '12px', color: '#3b82f6' }}><strong>Recovery:</strong> {a.recovery_recommendation}</p>
                      )}
                   </div>
                ))}
              </div>
           </div>
        </div>
      )}
    </div>
  );
}
"""

with open('src/pages/Dashboard.jsx', 'w') as f:
    f.write(dashboard_jsx.strip())

with open('src/pages/Suppliers.jsx', 'w') as f:
    f.write(suppliers_jsx.strip())

with open('src/pages/SupplierDetail.jsx', 'w') as f:
    f.write(supplier_detail_jsx.strip())

with open('src/pages/Events.jsx', 'w') as f:
    f.write(events_jsx.strip())

with open('src/pages/Recovery.jsx', 'w') as f:
    f.write(recovery_jsx.strip())

with open('src/pages/Simulate.jsx', 'w') as f:
    f.write(simulate_jsx.strip())

print("Successfully generated all Phase 3 frontend files.")
