/**
 * Workflow Executor — Run workflows against agents in real-time
 */
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Play, Bot, Clock, Zap, CheckCircle, XCircle, Send, RotateCcw } from 'lucide-react';
import { useStore } from '../store';

export default function ExecutePage() {
  const { agents, fetchAgents, executeWorkflow, executing, executionResult } = useStore();
  const [selectedAgentId, setSelectedAgentId] = useState('');
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);

  useEffect(() => { fetchAgents(); }, []);

  const handleExecute = async () => {
    if (!selectedAgentId || !input.trim()) return;

    try {
      const result = await executeWorkflow(Number(selectedAgentId), input.trim());
      setHistory(prev => [result, ...prev]);
      setInput('');
    } catch (err) {
      setHistory(prev => [{
        error: err.response?.data?.detail || 'Execution failed',
        input: input.trim(),
        status: 'failed',
        created_at: new Date().toISOString(),
      }, ...prev]);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h2>Execute Workflow</h2>
        <p>Send prompts to your agents and see results in real-time</p>
      </div>

      <div className="page-content">
        <div className="grid-2" style={{ gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* Left: Input Panel */}
          <div>
            <motion.div
              className="card"
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>
                <Zap size={16} style={{ verticalAlign: -2 }} /> Workflow Input
              </h3>

              <div className="form-group">
                <label className="form-label">Select Agent</label>
                <select
                  className="form-select"
                  value={selectedAgentId}
                  onChange={e => setSelectedAgentId(e.target.value)}
                >
                  <option value="">Choose an agent...</option>
                  {agents.map(a => (
                    <option key={a.id} value={a.id}>
                      {a.name} ({a.model})
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Input Prompt</label>
                <textarea
                  className="form-textarea"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  placeholder="e.g., Check my emails and create tasks for urgent items"
                  rows={6}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && e.metaKey) handleExecute();
                  }}
                />
                <span className="text-xs text-muted">⌘+Enter to execute</span>
              </div>

              <button
                className="btn btn-primary"
                style={{ width: '100%' }}
                onClick={handleExecute}
                disabled={executing || !selectedAgentId || !input.trim()}
              >
                {executing ? (
                  <><span className="spinner" /> Executing...</>
                ) : (
                  <><Send size={16} /> Execute Workflow</>
                )}
              </button>

              {/* Quick prompts */}
              <div style={{ marginTop: 16 }}>
                <span className="text-xs text-muted" style={{ marginBottom: 8, display: 'block' }}>Quick prompts:</span>
                <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                  {[
                    'Check emails and summarize urgent items',
                    'Create a task for the budget review',
                    'Send a team status update to Slack',
                    'Search for latest AI trends and generate report',
                  ].map(prompt => (
                    <button
                      key={prompt}
                      className="tag"
                      style={{ cursor: 'pointer', fontSize: 11 }}
                      onClick={() => setInput(prompt)}
                    >
                      {prompt.slice(0, 40)}...
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right: Results Panel */}
          <div>
            <motion.div
              className="card"
              initial={{ opacity: 0, x: 12 }}
              animate={{ opacity: 1, x: 0 }}
              style={{ minHeight: 400 }}
            >
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>
                <Play size={16} style={{ verticalAlign: -2 }} /> Execution Results
              </h3>

              {history.length === 0 && !executing ? (
                <div className="empty-state">
                  <div className="icon">⚡</div>
                  <h3>Ready to execute</h3>
                  <p>Select an agent, write a prompt, and hit Execute.</p>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  {executing && (
                    <div className="card-glass" style={{ padding: 16, textAlign: 'center' }}>
                      <div className="spinner" style={{ margin: '0 auto 12px' }} />
                      <p className="text-sm text-muted">Processing workflow...</p>
                    </div>
                  )}

                  {history.map((result, i) => (
                    <motion.div
                      key={i}
                      className="card-glass"
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      style={{ padding: 16 }}
                    >
                      {/* Header */}
                      <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
                        <div className="flex items-center gap-2">
                          {result.status === 'success' ? (
                            <CheckCircle size={16} style={{ color: 'var(--success)' }} />
                          ) : (
                            <XCircle size={16} style={{ color: 'var(--error)' }} />
                          )}
                          <span className={`badge badge-${result.status}`}>
                            <span className="badge-dot" />
                            {result.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-muted">
                          {result.execution_time && (
                            <span><Clock size={12} /> {result.execution_time.toFixed(3)}s</span>
                          )}
                          {result.tokens_used > 0 && (
                            <span>{result.tokens_used} tokens</span>
                          )}
                          {result.cost_usd > 0 && (
                            <span>${result.cost_usd.toFixed(4)}</span>
                          )}
                        </div>
                      </div>

                      {/* Input */}
                      <div style={{ background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', padding: '10px 12px', marginBottom: 10 }}>
                        <span className="text-xs text-muted">Input:</span>
                        <p className="text-sm" style={{ marginTop: 4 }}>{result.input}</p>
                      </div>

                      {/* Output */}
                      {result.output ? (
                        <div style={{ background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                          <span className="text-xs text-muted">Output:</span>
                          <pre className="text-sm" style={{
                            marginTop: 4,
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            fontFamily: "'SF Mono', 'Fira Code', monospace",
                            fontSize: 12.5,
                            lineHeight: 1.6,
                            color: 'var(--text-primary)',
                          }}>
                            {result.output}
                          </pre>
                        </div>
                      ) : result.error && (
                        <div style={{ background: 'var(--error-soft)', borderRadius: 'var(--radius-sm)', padding: '10px 12px', color: 'var(--error)', fontSize: 13 }}>
                          {result.error}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
}
