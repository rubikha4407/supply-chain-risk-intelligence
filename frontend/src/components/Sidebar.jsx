import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Factory,
  Zap,
  Shield,
  FlaskConical,
  Webhook,
  Heart,
} from 'lucide-react';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <h1>Supply Chain Risk Intelligence</h1>
        <div className="subtitle">Recovery Orchestrator</div>
      </div>

      <nav className="sidebar-nav">
        {/* Overview */}
        <div className="nav-section">
          <div className="nav-section-title">Overview</div>
          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <LayoutDashboard />
            Dashboard
          </NavLink>
        </div>

        {/* Supply Chain */}
        <div className="nav-section">
          <div className="nav-section-title">Supply Chain</div>
          <NavLink
            to="/suppliers"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Factory />
            Suppliers
          </NavLink>
          <NavLink
            to="/events"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Zap />
            Events
          </NavLink>
        </div>

        {/* Intelligence */}
        <div className="nav-section">
          <div className="nav-section-title">Intelligence</div>
          <NavLink
            to="/recovery"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Shield />
            Recovery Plans
          </NavLink>
          <NavLink
            to="/simulate"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <FlaskConical />
            Simulate
          </NavLink>
        </div>

        {/* System */}
        <div className="nav-section">
          <div className="nav-section-title">System</div>
          <NavLink
            to="/n8n"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Webhook />
            n8n Status
          </NavLink>
        </div>
      </nav>

      <div style={{ padding: '16px 20px', borderTop: '1px solid var(--glass-border)' }}>
        <div className="flex-center" style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          <Heart size={12} />
          Hackathon MVP v0.1
        </div>
      </div>
    </aside>
  );
}
