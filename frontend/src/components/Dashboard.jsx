/**
 * Dashboard Page — Overview with stats, recent activity, and charts
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Bot, Workflow, Zap, Clock, CheckCircle, XCircle, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { useStore } from '../store';

export default function Dashboard() {
  const { agents, workflows, tools, fetchAgents, fetchWorkflows, fetchTools, fetchHealth } = useStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchAgents(), fetchWorkflows(), fetchTools(), fetchHealth()])
      .finally(() => setLoading(false));
  }, []);

  const successCount = workflows.filter(w => w.status === 'success').length;
  const failedCount = workflows.filter(w => w.status === 'failed').length;
  const avgTime = workflows.length > 0
    ? (workflows.reduce((sum, w) => sum + (w.execution_time || 0), 0) / workflows.length).toFixed(2)
    : '0.00';

  // Chart data — aggregate by hour (mock for now)
  const chartData = Array.from({ length: 7 }, (_, i) => ({
    name: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
    workflows: Math.floor(Math.random() * 20) + 5 + workflows.length,
    success: Math.floor(Math.random() * 15) + 5 + successCount,
  }));

  const fadeIn = {
    initial: { opacity: 0, y: 12 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4 },
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-header-actions">
          <div>
            <h2>Dashboard</h2>
            <p>System overview and real-time metrics</p>
          </div>
          <div className="flex gap-2">
            <button className="btn btn-secondary btn-sm" onClick={() => { fetchAgents(); fetchWorkflows(); }}>
              ↻ Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="page-content">
        {/* Stats Grid */}
        <div className="stats-grid">
          <motion.div className="card stat-card" {...fadeIn} transition={{ delay: 0 }}>
            <div className="stat-header">
              <div className="stat-icon purple"><Bot size={18} /></div>
              <span className="stat-change positive">Active</span>
            </div>
            <span className="stat-label">Total Agents</span>
            <span className="stat-value">{agents.length}</span>
          </motion.div>

          <motion.div className="card stat-card" {...fadeIn} transition={{ delay: 0.05 }}>
            <div className="stat-header">
              <div className="stat-icon blue"><Workflow size={18} /></div>
              <span className="stat-change positive">+{workflows.length}</span>
            </div>
            <span className="stat-label">Total Workflows</span>
            <span className="stat-value">{workflows.length}</span>
          </motion.div>

          <motion.div className="card stat-card" {...fadeIn} transition={{ delay: 0.1 }}>
            <div className="stat-header">
              <div className="stat-icon green"><CheckCircle size={18} /></div>
              <span className="stat-change positive">{workflows.length > 0 ? Math.round(successCount / workflows.length * 100) : 0}%</span>
            </div>
            <span className="stat-label">Success Rate</span>
            <span className="stat-value">{successCount}</span>
          </motion.div>

          <motion.div className="card stat-card" {...fadeIn} transition={{ delay: 0.15 }}>
            <div className="stat-header">
              <div className="stat-icon orange"><Clock size={18} /></div>
            </div>
            <span className="stat-label">Avg. Latency</span>
            <span className="stat-value">{avgTime}s</span>
          </motion.div>
        </div>

        {/* Charts Row */}
        <div className="grid-2" style={{ marginBottom: 28 }}>
          <motion.div className="card" {...fadeIn} transition={{ delay: 0.2 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 20 }}>Workflow Activity</h3>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorWf" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6c5ce7" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6c5ce7" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" tick={{ fill: '#5a5a72', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#5a5a72', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: '#1e1e2a',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 10,
                    color: '#f0f0f5',
                    fontSize: 12,
                  }}
                />
                <Area type="monotone" dataKey="workflows" stroke="#6c5ce7" fill="url(#colorWf)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div className="card" {...fadeIn} transition={{ delay: 0.25 }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 20 }}>Success vs Total</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData} barGap={4}>
                <XAxis dataKey="name" tick={{ fill: '#5a5a72', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: '#5a5a72', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: '#1e1e2a',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: 10,
                    color: '#f0f0f5',
                    fontSize: 12,
                  }}
                />
                <Bar dataKey="workflows" fill="rgba(108, 92, 231, 0.3)" radius={[4, 4, 0, 0]} />
                <Bar dataKey="success" fill="#6c5ce7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Recent Workflows */}
        <motion.div className="card" {...fadeIn} transition={{ delay: 0.3 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Recent Workflows</h3>
          {workflows.length === 0 ? (
            <div className="empty-state">
              <div className="icon">📭</div>
              <h3>No workflows yet</h3>
              <p>Execute a workflow from the Agents page to see activity here.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Agent</th>
                    <th>Status</th>
                    <th>Input</th>
                    <th>Time</th>
                    <th>Tokens</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {workflows.slice(0, 10).map(wf => (
                    <tr key={wf.id}>
                      <td className="font-mono text-xs">#{wf.id}</td>
                      <td>Agent #{wf.agent_id}</td>
                      <td>
                        <span className={`badge badge-${wf.status}`}>
                          <span className="badge-dot" />
                          {wf.status}
                        </span>
                      </td>
                      <td className="truncate" style={{ maxWidth: 200 }}>{wf.input}</td>
                      <td className="text-muted">{wf.execution_time?.toFixed(2)}s</td>
                      <td className="text-muted">{wf.tokens_used || '—'}</td>
                      <td className="text-muted text-xs">{new Date(wf.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>

        {/* Available Tools */}
        <motion.div className="card" style={{ marginTop: 16 }} {...fadeIn} transition={{ delay: 0.35 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Available Tools ({tools.length})</h3>
          <div className="tags-list">
            {tools.map(tool => (
              <span key={tool.name} className="tag">
                <Zap size={10} /> {tool.name}
              </span>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
