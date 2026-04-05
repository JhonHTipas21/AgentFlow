"""
AgentFlow Database Models
SQLAlchemy ORM models for all database tables.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float,
    ForeignKey, Enum, Boolean, JSON, Table
)
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
import enum
import uuid


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# ═══════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════

class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ═══════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════

class Agent(Base):
    """AI Agent that can execute workflows using tools."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.ACTIVE, index=True)
    model = Column(String(50), default="claude-sonnet-4-20250514")
    system_prompt = Column(Text, nullable=True)
    max_tokens = Column(Integer, default=2000)
    temperature = Column(Float, default=0.7)

    # Relationships
    tools = relationship("Tool", secondary="agent_tools", back_populates="agents")
    workflows = relationship("Workflow", back_populates="agent", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, status={self.status})>"


class Tool(Base):
    """External tool/function that agents can use."""
    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    function_name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)
    input_schema = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    agents = relationship("Agent", secondary="agent_tools", back_populates="tools")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Tool(id={self.id}, name={self.name})>"


class AgentTool(Base):
    """Association table: Agent ↔ Tool (many-to-many)."""
    __tablename__ = "agent_tools"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    tool_id = Column(Integer, ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Workflow(Base):
    """A single execution of an agent's task."""
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)

    input = Column(Text, nullable=False)
    output = Column(Text, nullable=True)

    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING, index=True)
    error_message = Column(Text, nullable=True)

    execution_time = Column(Float, nullable=True)  # seconds
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)

    metadata_json = Column("metadata", JSON, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="workflows")
    logs = relationship("WorkflowLog", back_populates="workflow", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="workflow", cascade="all, delete-orphan")

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Workflow(id={self.id}, agent_id={self.agent_id}, status={self.status})>"


class WorkflowLog(Base):
    """Log entry for a workflow execution step."""
    __tablename__ = "workflow_logs"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)

    level = Column(Enum(LogLevel), default=LogLevel.INFO, index=True)
    message = Column(Text, nullable=False)
    event_type = Column(String(50), nullable=True)

    metadata_json = Column("metadata", JSON, nullable=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="logs")

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<WorkflowLog(id={self.id}, level={self.level})>"


class ToolCall(Base):
    """Record of a tool invocation during a workflow."""
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False, index=True)
    tool_name = Column(String(255), nullable=False)

    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)

    execution_time = Column(Float, nullable=True)

    # Relationships
    workflow = relationship("Workflow", back_populates="tool_calls")

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<ToolCall(id={self.id}, tool={self.tool_name})>"


class AuditLog(Base):
    """Audit trail for all user actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)
    action = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=False)

    changes = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action})>"
