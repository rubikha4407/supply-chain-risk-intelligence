import { useState } from 'react';
import { compareRecovery } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function WhatIfSimulator({ assessment, supplier, onSimulate }) {
  const [loading, setLoading] = useState(false);
  const [outcomes, setOutcomes] = useState([]);

  const handleCompare = async () => {
    setLoading(true);
    try {
      const res = await compareRecovery(assessment.id);
      setOutcomes(res.data);
      if (onSimulate) onSimulate(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  // The 'DO NOTHING' baseline
  const baseline = outcomes.find(o => o.strategy === 'do_nothing');
  
  // Format for the chart
  const chartData = outcomes.map(o => ({
    name: o.strategy.replace('_', ' ').toUpperCase(),
    'Recovery (Days)': o.recovery_time_days,
    'Rev Risk ($K)': Math.round(o.revenue_at_risk / 1000),
    'Add. Cost ($K)': Math.round(o.additional_cost / 1000)
  }));

  const revRisk = assessment.impact_analyses?.reduce((sum, ia) => sum + ia.revenue_at_risk, 0) || 0;

  return (
    <div className="card mt-24">
      <h3>What-If Simulator</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>Simulate recovery decisions before taking action.</p>

      <div style={{ padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', marginBottom: '24px' }}>
        <h4 style={{ color: 'var(--accent-amber)' }}>CURRENT SITUATION</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginTop: '12px' }}>
          <div><strong>Supplier:</strong> {supplier.name}</div>
          <div><strong>Inventory:</strong> {assessment.inventory_runway_days || 0} days</div>
          <div><strong>Expected Disruption:</strong> {assessment.estimated_disruption_days || 0} days</div>
          <div><strong>Revenue at Risk:</strong> ${revRisk.toLocaleString()}</div>
        </div>
      </div>

      {!outcomes.length ? (
        <button className="btn" onClick={handleCompare} disabled={loading} style={{ padding: '10px 20px', background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          {loading ? 'Running Simulations...' : 'Run What-If Comparison'}
        </button>
      ) : (
        <div className="animate-fade-in">
          <h4>Strategy Comparison</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginTop: '16px' }}>
            {outcomes.map(o => (
              <div key={o.strategy} style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '8px', background: 'var(--bg-card-hover)' }}>
                 <h5 style={{ marginBottom: '12px', fontSize: '14px', borderBottom: '1px solid var(--border)', paddingBottom: '8px' }}>
                   {o.strategy.replace('_', ' ').toUpperCase()}
                 </h5>
                 <p style={{ fontSize: '12px', color: 'var(--text-secondary)', minHeight: '36px' }}>{o.description}</p>
                 <ul style={{ marginTop: '12px', fontSize: '13px', lineHeight: '1.6', color: 'var(--text-primary)', listStyle: 'none', padding: 0 }}>
                   <li><strong>Recovery:</strong> {o.recovery_time_days} days</li>
                   <li><strong>Rev Risk:</strong> ${o.revenue_at_risk.toLocaleString()}</li>
                   <li><strong>Stockout:</strong> {o.stockout_status}</li>
                 </ul>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '32px' }}>
             <h4>Outcomes Matrix</h4>
             <table className="data-table" style={{ marginTop: '16px' }}>
               <thead>
                 <tr>
                   <th>Strategy</th>
                   <th>Additional Cost</th>
                   <th>Recovery Time</th>
                   <th>Revenue at Risk</th>
                   <th>Stockout</th>
                   <th>Prod. Impact</th>
                 </tr>
               </thead>
               <tbody>
                 {outcomes.map(o => (
                   <tr key={o.strategy}>
                     <td>{o.strategy.replace('_', ' ').toUpperCase()}</td>
                     <td>${o.additional_cost.toLocaleString()}</td>
                     <td>{o.recovery_time_days} days</td>
                     <td>${o.revenue_at_risk.toLocaleString()}</td>
                     <td><span className={`badge ${o.stockout_status === 'YES' ? 'critical' : 'monitoring'}`}>{o.stockout_status}</span></td>
                     <td>{o.production_impact_pct}%</td>
                   </tr>
                 ))}
               </tbody>
             </table>
          </div>

          <div style={{ marginTop: '32px', height: '350px' }}>
             <h4>Visual Comparison</h4>
             <ResponsiveContainer width="100%" height="100%" style={{ marginTop: '16px' }}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }} />
                  <Legend />
                  <Bar dataKey="Recovery (Days)" fill="#3b82f6" />
                  <Bar dataKey="Rev Risk ($K)" fill="#ef4444" />
                  <Bar dataKey="Add. Cost ($K)" fill="#f59e0b" />
                </BarChart>
             </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
