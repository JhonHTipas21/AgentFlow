"""
Pytest fixtures for AgentFlow tests.
Provides a test database and test client.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base


# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    # Clear in-memory state store between tests
    from app.state import StateManager
    StateManager._memory_store.clear()


@pytest.fixture
def db():
    """Provide a test database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Provide a test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_agent_data():
    """Sample agent creation payload."""
    return {
        "name": "test_agent",
        "description": "A test agent for unit tests",
        "tools": ["read_email", "search_web"],
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "temperature": 0.5,
    }


@pytest.fixture
def created_agent(client, sample_agent_data):
    """Create and return a test agent."""
    response = client.post("/agents/", json=sample_agent_data)
    assert response.status_code == 201
    return response.json()
