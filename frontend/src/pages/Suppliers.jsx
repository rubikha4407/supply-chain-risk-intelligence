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