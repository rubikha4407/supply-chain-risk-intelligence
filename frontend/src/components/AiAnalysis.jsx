import { useState, useEffect } from 'react';
import { getExplanation, explainTradeoffs } from '../api/client';

export default function AiAnalysis({ assessment, outcomes }) {
  const [explanation, setExplanation] = useState(null);
  const [tradeoffs, setTradeoffs] = useState(null);
  const [managerSummary, setManagerSummary] = useState(null);

  useEffect(() => {
    if (assessment) {
      getExplanation(assessment.id).then(res => setExplanation(res.data)).catch(console.error);
    }
  }, [assessment]);

  useEffect(() => {
    if (outcomes && outcomes.length > 0) {
      explainTradeoffs(outcomes).then(res => setTradeoffs(res.data.comparison_explanation)).catch(console.error);
    }
  }, [outcomes]);

  const handleManagerExplain = () => {
    if (!explanation) return;
    const summary = `EXECUTIVE BRIEFING:\n\n` +
      `Risk: ${assessment.event?.title || 'Supply Disruption'}\n` +
      `${explanation.why_it_matters}\n\n` +
      `IMPACT: ${explanation.business_impact}\n\n` +
      (tradeoffs ? `RECOMMENDATION CONSIDERATIONS: ${tradeoffs}` : '');
    setManagerSummary(summary);
  };

  return (
    <div className="card mt-24" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🤖</span> AI Risk & Strategy Analysis
        </h3>
        <button 
          className="btn" 
          onClick={handleManagerExplain}
          style={{ background: 'var(--accent-blue)', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}
        >
          Explain to Manager
        </button>
      </div>

      <div style={{ fontSize: '12px', color: 'var(--text-tertiary)', marginBottom: '16px', fontStyle: 'italic' }}>
        * AI-generated explanation based on calculated system data.
      </div>

      {explanation && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <h4 style={{ color: 'var(--accent-amber)', fontSize: '13px', marginBottom: '8px', textTransform: 'uppercase' }}>
              🧠 Why This Risk Matters
            </h4>
            <p style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-secondary)' }}>
              {explanation.why_it_matters}
            </p>
          </div>

          <div>
            <h4 style={{ color: 'var(--accent-red)', fontSize: '13px', marginBottom: '8px', textTransform: 'uppercase' }}>
              💥 Business Impact
            </h4>
            <div style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
              {explanation.business_impact}
            </div>
          </div>
        </div>
      )}

      {tradeoffs && (
        <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
          <h4 style={{ color: 'var(--accent-purple)', fontSize: '13px', marginBottom: '8px', textTransform: 'uppercase' }}>
            🔄 Recovery Trade-Offs
          </h4>
          <p style={{ fontSize: '14px', lineHeight: '1.6', color: 'var(--text-secondary)' }}>
            {tradeoffs}
          </p>
        </div>
      )}

      {managerSummary && (
        <div className="animate-fade-in" style={{ marginTop: '24px', padding: '16px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', borderLeft: '4px solid var(--accent-blue)' }}>
          <h4 style={{ fontSize: '13px', marginBottom: '8px', color: '#fff' }}>MANAGEMENT SUMMARY</h4>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '13px', lineHeight: '1.6', color: 'var(--text-secondary)', fontFamily: 'inherit' }}>
            {managerSummary}
          </pre>
        </div>
      )}
    </div>
  );
}
