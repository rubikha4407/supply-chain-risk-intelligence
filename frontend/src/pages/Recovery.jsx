import { useState, useEffect } from 'react';
import { getRecoveryPlans, approveRecoveryAction } from '../api/client';

export default function Recovery() {
  const [plans, setPlans] = useState([]);
  const [actionStatus, setActionStatus] = useState({});

  useEffect(() => {
    getRecoveryPlans().then(res => setPlans(res.data));
  }, []);

  const handleApprove = async (actionId) => {
    try {
      setActionStatus(prev => ({ ...prev, [actionId]: { stage: 'SENT TO n8n', message: 'Sending to orchestrator...' } }));
      const res = await approveRecoveryAction(actionId);
      
      setActionStatus(prev => ({ 
        ...prev, 
        [actionId]: { 
           stage: res.data.status.toUpperCase(), 
           message: res.data.message, 
           executionId: res.data.n8n_execution_id,
           time: new Date().toLocaleTimeString()
        } 
      }));
    } catch (e) {
      setActionStatus(prev => ({ ...prev, [actionId]: { stage: 'FAILED', message: e.response?.data?.detail || e.message } }));
    }
  };

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
               {p.actions.map(a => {
                 const statusInfo = actionStatus[a.id] || { stage: a.status === 'pending' ? null : a.status.toUpperCase() };
                 const isCompleted = statusInfo.stage === 'COMPLETED';
                 const isFailed = statusInfo.stage === 'FAILED';
                 
                 return (
                   <div key={a.id} style={{ display: 'flex', flexDirection: 'column', borderBottom: '1px solid var(--border)', padding: '12px 0' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <strong>{a.action_type.replace('_', ' ').toUpperCase()}</strong>
                          <p style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>{a.description}</p>
                        </div>
                        {statusInfo.stage ? (
                           <span className={`badge ${isCompleted ? 'resolved' : isFailed ? 'critical' : 'monitoring'}`}>
                             {statusInfo.stage}
                           </span>
                        ) : (
                          <button 
                            className="btn" 
                            onClick={() => handleApprove(a.id)}
                            style={{ padding: '6px 12px', fontSize: '12px', background: 'var(--accent-blue)', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                          >
                            Approve & Execute
                          </button>
                        )}
                      </div>
                      
                      {statusInfo.stage && (
                        <div style={{ marginTop: '12px', padding: '8px', background: 'var(--bg-main)', borderRadius: '4px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                           <strong>Automation Activity:</strong>
                           <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px' }}>
                             <span>Time: {statusInfo.time || new Date().toLocaleTimeString()}</span>
                             <span>Status: {statusInfo.stage}</span>
                             <span>Execution ID: {statusInfo.executionId || a.n8n_execution_id || 'N/A'}</span>
                           </div>
                           {statusInfo.message && (
                             <div style={{ marginTop: '4px', color: isFailed ? 'var(--accent-red)' : 'var(--accent-amber)' }}>
                               {statusInfo.message}
                             </div>
                           )}
                        </div>
                      )}
                   </div>
                 );
               })}
             </div>
          </div>
        ))}
      </div>
    </div>
  );
}