/**
 * Workflows Page — View execution history
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Workflow, Clock, CheckCircle, XCircle, FileText, ChevronDown, ChevronUp } from 'lucide-react';
import { useStore } from '../store';
import { workflowsApi } from '../api';

export default function WorkflowsPage() {
  const { workflows, fetchWorkflows, workflowsLoading } = useStore();
  const [expandedId, setExpandedId] = useState(null);
  const [logs, setLogs] = useState({});

  useEffect(() => { fetchWorkflows(); }, []);

  const toggleExpand = async (id) => {
    if (expandedId === id) {
      setExpandedId(null);
      return;
    }
    setExpandedId(id);
    if (!logs[id]) {
      try {
        const { data } = await workflowsApi.logs(id);
        setLogs(prev => ({ ...prev, [id]: data }));
      } catch (err) {
        console.error('Failed to fetch logs:', err);
      }
    }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-header-actions">
          <div>
            <h2>Workflows</h2>
            <p>View execution history and detailed logs</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={fetchWorkflows}>
            ↻ Refresh
          </button>
        </div>
      </div>

      <div className="page-content">
        {workflowsLoading ? (
          <div className="empty-state">
            <div className="spinner" style={{ margin: '0 auto' }} />
          </div>
        ) : workflows.length === 0 ? (
          <div className="empty-state">
            <div className="icon">📋</div>
            <h3>No workflows recorded</h3>
            <p>Execute a workflow to see its history here.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {workflows.map((wf, i) => (
              <motion.div
                key={wf.id}
                className="card"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                style={{ padding: 0, overflow: 'hidden' }}
              >
                {/* Row */}
                <div
                  className="flex items-center justify-between"
                  style={{ padding: '14px 20px', cursor: 'pointer' }}
                  onClick={() => toggleExpand(wf.id)}
                >
                  <div className="flex items-center gap-3">
                    {wf.status === 'success' ? (
                      <CheckCircle size={18} style={{ color: 'var(--success)' }} />
                    ) : wf.status === 'failed' ? (
                      <XCircle size={18} style={{ color: 'var(--error)' }} />
                    ) : (
                      <Clock size={18} style={{ color: 'var(--info)' }} />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs" style={{ color: 'var(--text-tertiary)' }}>
                          #{wf.id}
                        </span>
                        <span className={`badge badge-${wf.status}`}>
                          <span className="badge-dot" /> {wf.status}
                        </span>
                        <span className="text-xs text-muted">Agent #{wf.agent_id}</span>
                      </div>
                      <p className="text-sm truncate" style={{ maxWidth: 500, marginTop: 2 }}>
                        {wf.input}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-xs text-muted flex items-center gap-2">
                      <Clock size={12} /> {wf.execution_time?.toFixed(3)}s
                    </div>
                    <div className="text-xs text-muted">
                      {new Date(wf.created_at).toLocaleString()}
                    </div>
                    {expandedId === wf.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </div>
                </div>

                {/* Expanded Detail */}
                {expandedId === wf.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    style={{ borderTop: '1px solid var(--border-subtle)', padding: 20, background: 'var(--bg-secondary)' }}
                  >
                    <div className="grid-2" style={{ gap: 20 }}>
                      <div>
                        <h4 className="text-xs text-muted" style={{ marginBottom: 8 }}>INPUT</h4>
                        <div style={{ background: 'var(--bg-input)', padding: 12, borderRadius: 'var(--radius-sm)', fontSize: 13 }}>
                          {wf.input}
                        </div>
                      </div>
                      <div>
                        <h4 className="text-xs text-muted" style={{ marginBottom: 8 }}>OUTPUT</h4>
                        <pre style={{
                          background: 'var(--bg-input)',
                          padding: 12,
                          borderRadius: 'var(--radius-sm)',
                          fontSize: 12,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          fontFamily: "'SF Mono', monospace",
                          maxHeight: 300,
                          overflow: 'auto',
                        }}>
                          {wf.output || '(no output)'}
                        </pre>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="flex gap-4 mt-4">
                      <div className="tag">Tokens: {wf.tokens_used || 0}</div>
                      <div className="tag">Cost: ${(wf.cost_usd || 0).toFixed(4)}</div>
                      <div className="tag">Time: {wf.execution_time?.toFixed(3)}s</div>
                      {wf.error_message && <div className="tag" style={{ color: 'var(--error)' }}>Error: {wf.error_message}</div>}
                    </div>

                    {/* Logs */}
                    {logs[wf.id] && logs[wf.id].length > 0 && (
                      <div style={{ marginTop: 16 }}>
                        <h4 className="text-xs text-muted" style={{ marginBottom: 8 }}>
                          <FileText size={12} style={{ verticalAlign: -2 }} /> EXECUTION LOGS
                        </h4>
                        {logs[wf.id].map(log => (
                          <div
                            key={log.id}
                            className="flex items-center gap-3"
                            style={{
                              padding: '6px 0',
                              borderBottom: '1px solid var(--border-subtle)',
                              fontSize: 12,
                            }}
                          >
                            <span className={`badge badge-${log.level === 'error' ? 'error' : 'active'}`} style={{ minWidth: 50, justifyContent: 'center' }}>
                              {log.level}
                            </span>
                            <span>{log.message}</span>
                            <span className="text-muted" style={{ marginLeft: 'auto', fontSize: 11 }}>
                              {new Date(log.created_at).toLocaleTimeString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </motion.div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
