import { useState, useEffect } from 'react';
import { Webhook, CheckCircle, XCircle } from 'lucide-react';
import { getN8nStatus } from '../api/client';

export default function N8nStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getN8nStatus()
      .then((res) => setStatus(res.data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Checking n8n status...</p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <h2>n8n Integration</h2>
        <p>Workflow automation engine connectivity and execution status</p>
      </div>

      <div className="card" style={{ textAlign: 'center', padding: 48 }}>
        {status?.connected ? (
          <CheckCircle size={48} color="var(--accent-emerald)" />
        ) : (
          <XCircle size={48} color="var(--text-muted)" />
        )}
        <h3 style={{ marginTop: 16, fontSize: 18, fontWeight: 600 }}>
          {status?.connected ? 'Connected' : 'Not Connected'}
        </h3>
        <p style={{ marginTop: 8, fontSize: 13, color: 'var(--text-secondary)' }}>
          {status?.message}
        </p>
        <div
          style={{
            marginTop: 24,
            padding: '12px 20px',
            background: 'var(--glass)',
            borderRadius: 'var(--radius-sm)',
            display: 'inline-block',
            fontSize: 12,
            color: 'var(--text-tertiary)',
          }}
        >
          <Webhook size={14} style={{ verticalAlign: 'middle', marginRight: 6 }} />
          n8n webhook integration will be configured in Phase 4
        </div>
      </div>
    </div>
  );
}
