/**
 * Sidebar Navigation Component
 */
import { Bot, LayoutDashboard, Workflow, Wrench, Settings, Activity, ChevronRight, Zap } from 'lucide-react';
import { useStore } from '../store';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'agents', label: 'Agents', icon: Bot },
  { id: 'workflows', label: 'Workflows', icon: Workflow },
  { id: 'tools', label: 'Tools', icon: Wrench },
  { id: 'execute', label: 'Execute', icon: Zap },
];

export default function Sidebar() {
  const { currentPage, setPage, systemHealth } = useStore();

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon"><Bot size={22} /></div>
          <div>
            <h1>AgentFlow</h1>
            <span>v1.0.0</span>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section-title">Navigation</div>
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`nav-link ${currentPage === id ? 'active' : ''}`}
            onClick={() => setPage(id)}
          >
            <Icon className="icon" size={18} />
            {label}
            {currentPage === id && (
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.4 }} />
            )}
          </button>
        ))}

        <div className="nav-section-title" style={{ marginTop: 24 }}>System</div>
        <button className="nav-link" onClick={() => setPage('settings')}>
          <Settings className="icon" size={18} />
          Settings
        </button>
      </nav>

      <div className="sidebar-footer">
        <div className="flex items-center gap-2" style={{ padding: '0 8px' }}>
          <Activity size={14} style={{ color: systemHealth?.status === 'ok' ? 'var(--success)' : 'var(--error)' }} />
          <span className="text-xs text-muted">
            API {systemHealth?.status === 'ok' ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </aside>
  );
}
