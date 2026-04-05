/**
 * Tools Page — Browse available tools
 */
import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { Wrench, Mail, FileText, MessageSquare, Search, BarChart3 } from 'lucide-react';
import { useStore } from '../store';

const TOOL_ICONS = {
  email: Mail,
  project_management: FileText,
  communication: MessageSquare,
  research: Search,
  analysis: BarChart3,
};

const TOOL_COLORS = {
  email: '#e74c3c',
  project_management: '#3498db',
  communication: '#9b59b6',
  research: '#2ecc71',
  analysis: '#f39c12',
};

export default function ToolsPage() {
  const { tools, fetchTools } = useStore();

  useEffect(() => { fetchTools(); }, []);

  return (
    <div>
      <div className="page-header">
        <h2>Tool Registry</h2>
        <p>Available tools that agents can use during workflow execution</p>
      </div>

      <div className="page-content">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
          {tools.map((tool, i) => {
            const Icon = TOOL_ICONS[tool.category] || Wrench;
            const color = TOOL_COLORS[tool.category] || '#6c5ce7';

            return (
              <motion.div
                key={tool.name}
                className="card"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="flex items-center gap-3" style={{ marginBottom: 14 }}>
                  <div
                    className="stat-icon"
                    style={{
                      background: `${color}15`,
                      color: color,
                      width: 42,
                      height: 42,
                    }}
                  >
                    <Icon size={20} />
                  </div>
                  <div>
                    <h4 style={{ fontSize: 14, fontWeight: 600 }}>{tool.name}</h4>
                    {tool.category && (
                      <span className="text-xs text-muted">{tool.category}</span>
                    )}
                  </div>
                </div>
                <p className="text-sm text-muted">{tool.description}</p>
              </motion.div>
            );
          })}
        </div>

        {tools.length === 0 && (
          <div className="empty-state">
            <div className="icon">🔧</div>
            <h3>No tools available</h3>
            <p>Tools are registered in the backend tool registry.</p>
          </div>
        )}
      </div>
    </div>
  );
}
