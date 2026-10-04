import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getSupplier, getAssessments } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import WhatIfSimulator from '../components/WhatIfSimulator';
import BlastRadius from '../components/BlastRadius';
import AiAnalysis from '../components/AiAnalysis';

export default function SupplierDetail() {
  const { id } = useParams();
  const [supplier, setSupplier] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [outcomes, setOutcomes] = useState([]);

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
      
      {assessment && (
        <>
          <AiAnalysis assessment={assessment} outcomes={outcomes} />
          <WhatIfSimulator assessment={assessment} supplier={supplier} onSimulate={setOutcomes} />
          <BlastRadius assessmentId={assessment.id} />
        </>
      )}
    </div>
  );
}