/**
 * AgentFlow — Main Application
 */
import { useEffect } from 'react';
import { useStore } from './store';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import AgentsPage from './components/AgentsPage';
import WorkflowsPage from './components/WorkflowsPage';
import ToolsPage from './components/ToolsPage';
import ExecutePage from './components/ExecutePage';

const PAGES = {
  dashboard: Dashboard,
  agents: AgentsPage,
  workflows: WorkflowsPage,
  tools: ToolsPage,
  execute: ExecutePage,
};

export default function App() {
  const { currentPage, fetchHealth, toasts, removeToast } = useStore();
  const Page = PAGES[currentPage] || Dashboard;

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000); // Check health every 30s
    return () => clearInterval(interval);
  }, []);

  // Auto-remove toasts
  useEffect(() => {
    if (toasts.length > 0) {
      const timer = setTimeout(() => removeToast(toasts[0].id), 4000);
      return () => clearTimeout(timer);
    }
  }, [toasts]);

  return (
    <div className="app-layout">
      <Sidebar />
      <main className="main-content">
        <Page />
      </main>

      {/* Toast Notifications */}
      <div className="toast-container">
        {toasts.map(toast => (
          <div key={toast.id} className="toast" onClick={() => removeToast(toast.id)}>
            {toast.type === 'success' && '✅'}
            {toast.type === 'error' && '❌'}
            {toast.type === 'info' && 'ℹ️'}
            <span>{toast.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
