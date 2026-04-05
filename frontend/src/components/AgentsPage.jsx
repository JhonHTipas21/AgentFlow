/**
 * Agents Page — List, create, and manage agents
 */
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Plus, Trash2, Play, ChevronRight, Settings, X, Wrench } from 'lucide-react';
import { useStore } from '../store';

export default function AgentsPage() {
  const { agents, fetchAgents, createAgent, deleteAgent, agentsLoading, tools, fetchTools, setPage } = useStore();
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    fetchAgents();
    fetchTools();
  }, []);

  return (
    <div>
      <div className="page-header">
        <div className="page-header-actions">
          <div>
            <h2>Agents</h2>
            <p>Create and manage your AI agents</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
            <Plus size={16} /> New Agent
          </button>
        </div>
      </div>

      <div className="page-content">
        {agentsLoading ? (
          <div className="empty-state">
            <div className="spinner" style={{ margin: '0 auto' }} />
            <p className="mt-4">Loading agents...</p>
          </div>
        ) : agents.length === 0 ? (
          <div className="empty-state">
            <div className="icon">🤖</div>
            <h3>No agents yet</h3>
            <p>Create your first AI agent to start automating workflows.</p>
            <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
              <Plus size={16} /> Create Agent
            </button>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 16 }}>
            {agents.map((agent, i) => (
              <AgentCard key={agent.id} agent={agent} index={i} onDelete={deleteAgent} onExecute={() => setPage('execute')} />
            ))}
          </div>
        )}
      </div>

      <AnimatePresence>
        {showCreate && (
          <CreateAgentModal
            tools={tools}
            onClose={() => setShowCreate(false)}
            onCreate={async (data) => {
              await createAgent(data);
              setShowCreate(false);
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}


function AgentCard({ agent, index, onDelete, onExecute }) {
  const [confirmDelete, setConfirmDelete] = useState(false);

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      style={{ cursor: 'default' }}
    >
      <div className="flex items-center justify-between" style={{ marginBottom: 14 }}>
        <div className="flex items-center gap-3">
          <div className="stat-icon purple" style={{ width: 36, height: 36 }}>
            <Bot size={18} />
          </div>
          <div>
            <h4 style={{ fontSize: 14, fontWeight: 600 }}>{agent.name}</h4>
            <span className="text-xs text-muted font-mono">{agent.uuid?.slice(0, 8)}</span>
          </div>
        </div>
        <span className={`badge badge-${agent.status}`}>
          <span className="badge-dot" />
          {agent.status}
        </span>
      </div>

      {agent.description && (
        <p className="text-sm text-muted" style={{ marginBottom: 12 }}>
          {agent.description}
        </p>
      )}

      <div className="flex items-center gap-2" style={{ marginBottom: 14 }}>
        <Settings size={12} className="text-muted" />
        <span className="text-xs text-muted">{agent.model}</span>
        <span className="text-xs text-muted">•</span>
        <span className="text-xs text-muted">T={agent.temperature}</span>
        <span className="text-xs text-muted">•</span>
        <span className="text-xs text-muted">{agent.max_tokens} tokens</span>
      </div>

      {agent.tools?.length > 0 && (
        <div className="tags-list" style={{ marginBottom: 14 }}>
          {agent.tools.map(tool => (
            <span key={tool.id || tool.name} className="tag">
              <Wrench size={10} /> {tool.name}
            </span>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <button className="btn btn-primary btn-sm" style={{ flex: 1 }} onClick={onExecute}>
          <Play size={14} /> Execute
        </button>
        {confirmDelete ? (
          <>
            <button className="btn btn-danger btn-sm" onClick={() => { onDelete(agent.id); setConfirmDelete(false); }}>
              Confirm
            </button>
            <button className="btn btn-ghost btn-sm" onClick={() => setConfirmDelete(false)}>Cancel</button>
          </>
        ) : (
          <button className="btn btn-ghost btn-sm" onClick={() => setConfirmDelete(true)}>
            <Trash2 size={14} />
          </button>
        )}
      </div>
    </motion.div>
  );
}


function CreateAgentModal({ tools, onClose, onCreate }) {
  const [form, setForm] = useState({
    name: '',
    description: '',
    tools: [],
    model: 'claude-sonnet-4-20250514',
    max_tokens: 2000,
    temperature: 0.7,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setError('Agent name is required');
      return;
    }
    setSubmitting(true);
    setError('');
    try {
      await onCreate(form);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create agent');
      setSubmitting(false);
    }
  };

  const toggleTool = (toolName) => {
    setForm(prev => ({
      ...prev,
      tools: prev.tools.includes(toolName)
        ? prev.tools.filter(t => t !== toolName)
        : [...prev.tools, toolName],
    }));
  };

  return (
    <motion.div
      className="modal-overlay"
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className="modal"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        onClick={e => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>Create New Agent</h3>
          <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={16} /></button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div style={{ background: 'var(--error-soft)', color: 'var(--error)', padding: '10px 14px', borderRadius: 'var(--radius-md)', marginBottom: 16, fontSize: 13 }}>
                {error}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Name *</label>
              <input
                className="form-input"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
                placeholder="e.g. email_processor"
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-textarea"
                value={form.description}
                onChange={e => setForm({ ...form, description: e.target.value })}
                placeholder="What does this agent do?"
                rows={3}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Model</label>
              <select
                className="form-select"
                value={form.model}
                onChange={e => setForm({ ...form, model: e.target.value })}
              >
                <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
                <option value="claude-3-opus-20240229">Claude 3 Opus</option>
              </select>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Max Tokens</label>
                <input
                  className="form-input"
                  type="number"
                  value={form.max_tokens}
                  onChange={e => setForm({ ...form, max_tokens: Number(e.target.value) })}
                  min={100} max={8000}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Temperature ({form.temperature})</label>
                <input
                  type="range"
                  min="0" max="1" step="0.1"
                  value={form.temperature}
                  onChange={e => setForm({ ...form, temperature: Number(e.target.value) })}
                  style={{ width: '100%', marginTop: 8 }}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Assign Tools</label>
              <div className="flex gap-2" style={{ flexWrap: 'wrap' }}>
                {tools.map(tool => (
                  <button
                    key={tool.name}
                    type="button"
                    className={`tag ${form.tools.includes(tool.name) ? '' : ''}`}
                    style={{
                      cursor: 'pointer',
                      background: form.tools.includes(tool.name) ? 'var(--accent-soft)' : undefined,
                      color: form.tools.includes(tool.name) ? 'var(--accent)' : undefined,
                      borderColor: form.tools.includes(tool.name) ? 'var(--accent)' : undefined,
                    }}
                    onClick={() => toggleTool(tool.name)}
                  >
                    <Wrench size={10} /> {tool.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? <><span className="spinner" /> Creating...</> : <><Plus size={14} /> Create Agent</>}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
}
