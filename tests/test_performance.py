"""
AgentFlow Performance Tests
Benchmarks for API response time, throughput, and concurrency.
"""
import pytest
import time
from concurrent.futures import ThreadPoolExecutor


class TestPerformance:
    """Performance benchmarks for AgentFlow."""

    def test_health_endpoint_latency(self, client):
        """Health check responds under 100ms."""
        start = time.time()
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200
        elapsed = time.time() - start
        avg_ms = (elapsed / 10) * 1000
        assert avg_ms < 100, f"Avg latency {avg_ms:.1f}ms exceeds 100ms"

    def test_agent_crud_latency(self, client):
        """Agent create + read cycle under 200ms."""
        start = time.time()
        response = client.post("/agents/", json={"name": "perf_agent"})
        assert response.status_code == 201
        agent_id = response.json()["id"]

        response = client.get(f"/agents/{agent_id}")
        assert response.status_code == 200
        elapsed = (time.time() - start) * 1000
        assert elapsed < 200, f"CRUD cycle took {elapsed:.1f}ms"

    def test_list_agents_scalability(self, client):
        """Listing agents scales with count."""
        # Create 20 agents
        for i in range(20):
            client.post("/agents/", json={"name": f"scale_agent_{i}"})

        start = time.time()
        response = client.get("/agents/?limit=20")
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert len(response.json()) == 20
        assert elapsed < 300, f"List 20 agents took {elapsed:.1f}ms"

    def test_workflow_execution_throughput(self, client, created_agent):
        """Execute 5 workflows sequentially under 5s."""
        agent_id = created_agent["id"]
        start = time.time()

        for i in range(5):
            response = client.post(f"/agents/{agent_id}/execute", json={
                "input": f"Throughput test #{i}",
            })
            assert response.status_code == 200

        elapsed = time.time() - start
        throughput = 5 / elapsed
        assert throughput > 1.0, f"Throughput {throughput:.2f}/s too low"

    def test_concurrent_health_checks(self, client):
        """Handle 10 concurrent health checks."""
        def health_check(_):
            response = client.get("/health")
            return response.status_code

        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(health_check, range(10)))

        assert all(r == 200 for r in results)

    def test_tools_listing_latency(self, client):
        """Tools list responds under 50ms."""
        start = time.time()
        response = client.get("/tools/")
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 50, f"Tools list took {elapsed:.1f}ms"

    def test_api_response_size(self, client, created_agent):
        """API responses are compact (under 4KB for single agent)."""
        agent_id = created_agent["id"]
        response = client.get(f"/agents/{agent_id}")
        size_bytes = len(response.content)
        assert size_bytes < 4096, f"Response {size_bytes}B exceeds 4KB"
