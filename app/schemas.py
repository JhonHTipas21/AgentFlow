"""
AgentFlow Pydantic Schemas
Request/response validation models for the API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ═══════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════

class AgentStatusSchema(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class WorkflowStatusSchema(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ═══════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════

class ToolCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=5)
    function_name: str
    category: Optional[str] = None
    input_schema: Optional[Dict[str, Any]] = None


class ToolResponse(BaseModel):
    id: int
    name: str
    description: str
    function_name: str
    category: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ToolInfo(BaseModel):
    """Lightweight tool info for listing available tools."""
    name: str
    description: str
    category: Optional[str] = None


# ═══════════════════════════════════════════════════════
# AGENTS
# ═══════════════════════════════════════════════════════

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255, examples=["email_processor"])
    description: Optional[str] = Field(None, examples=["Processes emails and creates tasks"])
    tools: List[str] = Field(default=[], description="List of tool names to assign")
    model: str = Field("claude-sonnet-4-20250514", description="LLM model to use")
    system_prompt: Optional[str] = None
    max_tokens: int = Field(2000, ge=100, le=8000)
    temperature: float = Field(0.7, ge=0.0, le=1.0)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    status: Optional[AgentStatusSchema] = None
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)


class AgentResponse(BaseModel):
    id: int
    uuid: str
    name: str
    description: Optional[str] = None
    status: AgentStatusSchema
    model: str
    max_tokens: int
    temperature: float
    tools: List[ToolResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgentListResponse(BaseModel):
    id: int
    uuid: str
    name: str
    description: Optional[str] = None
    status: AgentStatusSchema
    model: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════
# WORKFLOWS
# ═══════════════════════════════════════════════════════

class WorkflowExecuteRequest(BaseModel):
    input: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        examples=["Check emails and create tasks for urgent items"]
    )
    metadata: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    id: int
    uuid: str
    agent_id: int
    input: str
    output: Optional[str] = None
    status: WorkflowStatusSchema
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None
    cost_usd: Optional[float] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WorkflowLogResponse(BaseModel):
    id: int
    workflow_id: int
    level: str
    message: str
    event_type: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    sub: Optional[str] = None


# ═══════════════════════════════════════════════════════
# GENERIC RESPONSES
# ═══════════════════════════════════════════════════════

class MessageResponse(BaseModel):
    detail: str


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    skip: int
    limit: int
