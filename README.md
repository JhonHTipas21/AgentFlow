# 🤖 AgentFlow

> **Production-Ready Multi-Agent System with Claude API**
>
> Automatiza flujos de trabajo empresariales complejos mediante un sistema de agentes autónomos inteligentes. AgentFlow orquesta múltiples agentes especializados que colaboran usando Claude para resolver tareas end-to-end sin intervención humana.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Claude API](https://img.shields.io/badge/claude-sonnet-purple.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Key Features

### 🎯 Multi-Agent Orchestration
- Specialized agents that work collaboratively
- Intelligent orchestration powered by Claude
- Automatic dependency handling between agents
- Auto-retry and fallback on errors

### 🛠️ Extensible Tool System
- **Email**: Gmail reading, content analysis
- **Task Management**: Jira task creation
- **Communication**: Slack notifications
- **Research**: Web search and data analysis
- **Reports**: Automated report generation
- **Easy to extend**: Create your own tools in minutes

### ⚡ Async-First Architecture
- Celery workers for parallel processing
- Redis for cache and state management
- WebSocket support for real-time updates
- Background task execution

### 📊 Enterprise-Ready
- ✅ JWT Authentication
- ✅ Complete audit logging
- ✅ Structured JSON logging
- ✅ Prometheus metrics endpoint
- ✅ Docker + Docker Compose
- ✅ Health & readiness checks

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- (Optional) Docker & Docker Compose
- (Optional) PostgreSQL 15+ and Redis 7+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/JhonHTipas21/agentflow.git
cd agentflow
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment**
```bash
cp .env.example .env
# Edit .env with your API keys (ANTHROPIC_API_KEY for Claude)
```

5. **Run the API**
```bash
uvicorn app.main:app --reload
```

6. **Verify**
```bash
curl http://localhost:8000/health
# Response: {"status": "ok", "app": "AgentFlow", "version": "1.0.0"}
```

7. **Explore the API**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### With Docker (Production)
```bash
docker-compose up -d
# API: http://localhost:8000
# Swagger: http://localhost:8000/docs
```

---

## 📖 Usage Examples

### Create an Agent

```bash
curl -X POST http://localhost:8000/agents/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "email_processor",
    "description": "Processes incoming emails and creates tasks",
    "tools": ["read_email", "create_jira_task", "send_slack_message"]
  }'
```

### Execute a Workflow

```bash
curl -X POST http://localhost:8000/agents/1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Check emails and create tasks for urgent items"
  }'

# Response:
# {
#   "workflow_id": 1,
#   "agent_id": 1,
#   "output": "Created 3 tasks from emails...",
#   "status": "success",
#   "execution_time": 1.23
# }
```

### View Workflow Logs

```bash
curl http://localhost:8000/workflows/1/logs
```

### List Available Tools

```bash
curl http://localhost:8000/tools/
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  User / External System                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │   FastAPI Gateway   │
         │  (JWT Auth, CORS)   │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┐
    ▼               ▼               ▼
┌─────────┐  ┌────────────┐  ┌──────────────┐
│ Agent   │  │ Workflow   │  │ Tool         │
│ Service │  │ Service    │  │ Registry     │
└────┬────┘  └─────┬──────┘  └──────┬───────┘
     │             │                │
     │             ▼                │
     │      ┌────────────────┐     │
     │      │ Agent          │     │
     └─────▶│ Orchestrator   │◀────┘
            │ (Claude API)   │
            └────────┬───────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │ Gmail  │  │ Jira   │  │ Slack  │
    │ API    │  │ API    │  │ API    │
    └────────┘  └────────┘  └────────┘
```

---

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.11+ |
| **Web Framework** | FastAPI | 0.115+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Database** | SQLite / PostgreSQL | — |
| **Cache** | Redis | 7+ |
| **Task Queue** | Celery | 5.4+ |
| **AI/LLM** | Claude API (Anthropic) | Latest |
| **Container** | Docker | 24+ |
| **Testing** | Pytest | 8.3+ |

---

## 📁 Project Structure

```
agentflow/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py             # Settings management
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── database.py           # DB connection
│   ├── agents.py             # Agent orchestrator
│   ├── tools.py              # Tool system
│   ├── celery_app.py         # Async task queue
│   ├── logging_config.py     # Structured logging
│   ├── routers/
│   │   ├── agents.py         # /agents endpoints
│   │   ├── workflows.py      # /workflows endpoints
│   │   └── tools.py          # /tools endpoints
│   ├── services/
│   │   ├── agent_service.py  # Agent CRUD logic
│   │   └── workflow_service.py
│   ├── integrations/
│   │   ├── gmail.py          # Gmail API
│   │   ├── jira.py           # Jira API
│   │   └── slack.py          # Slack API
│   └── middleware/
│       └── auth.py           # JWT authentication
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   └── test_api.py           # API tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── LICENSE
└── README.md
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test class
pytest tests/test_api.py::TestAgentCRUD -v
```

---

## 🔐 Security

- ✅ JWT authentication on endpoints
- ✅ CORS properly configured
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ API key management via environment variables
- ✅ Audit logging of all actions
- ✅ Non-root Docker user
- ✅ Secrets never in git (use .env)

---

## 🗂️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/ready` | Readiness check (DB) |
| `GET` | `/info` | App information |
| `POST` | `/token` | Get JWT token |
| `POST` | `/agents/` | Create agent |
| `GET` | `/agents/` | List agents |
| `GET` | `/agents/{id}` | Get agent |
| `PUT` | `/agents/{id}` | Update agent |
| `DELETE` | `/agents/{id}` | Delete agent |
| `POST` | `/agents/{id}/execute` | Execute workflow |
| `POST` | `/agents/{id}/execute-async` | Async execution |
| `GET` | `/workflows/` | List workflows |
| `GET` | `/workflows/{id}` | Get workflow |
| `GET` | `/workflows/{id}/logs` | Get workflow logs |
| `GET` | `/tools/` | List tools |
| `GET` | `/tools/{name}` | Get tool details |

---

## 🗺️ Roadmap

- [ ] v1.1 — Agent memory persistence (long-term context)
- [ ] v1.2 — Multi-model support (Claude + GPT-4 + Gemini)
- [ ] v1.3 — Visual workflow builder (React frontend)
- [ ] v1.4 — Agent marketplace (share agents)
- [ ] v1.5 — Advanced RAG (knowledge bases)
- [ ] v2.0 — Self-improving agents

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 📧 Contact

- **GitHub**: [@JhonHTipas21](https://github.com/JhonHTipas21)
- **Email**: jhonharveytipas@gmail.com
- **LinkedIn**: [Jhon Harvey Tipas Solis](https://linkedin.com/in/jhon-harvey-tipas-solis-b45135259/)

---

**Made with ❤️ by [Jhon Harvey Tipas Solis](https://github.com/JhonHTipas21)**

⭐ If AgentFlow helps you, please star it on GitHub!
