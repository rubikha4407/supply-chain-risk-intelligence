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