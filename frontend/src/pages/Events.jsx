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