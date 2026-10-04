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
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
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