"""FastAPI PraisonAI Router Tests - TDD"""


class TestPraisonAIClient:
    """Test PraisonAI client."""

    def test_client_class_exists(self):
        from fastapi_praisonai import PraisonAIClient
        assert PraisonAIClient is not None

    def test_client_default_api_url(self):
        from fastapi_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert client.api_url == "http://localhost:8080"

    def test_client_has_run_workflow_method(self):
        from fastapi_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_workflow')


class TestPraisonAIRouter:
    """Test PraisonAI router."""

    def test_create_router_function_exists(self):
        from fastapi_praisonai import create_router
        assert create_router is not None
        assert callable(create_router)

    def test_create_router_returns_router(self):
        from fastapi_praisonai import create_router
        from fastapi import APIRouter
        router = create_router()
        assert isinstance(router, APIRouter)


class TestPraisonAIClientExecution:
    """Test client execution."""

    def test_run_workflow(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Test response"}
        )
        from fastapi_praisonai import PraisonAIClient
        import asyncio
        client = PraisonAIClient()
        result = asyncio.run(client.run_workflow("Test query"))
        assert result == "Test response"

    def test_run_agent(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        from fastapi_praisonai import PraisonAIClient
        import asyncio
        client = PraisonAIClient()
        result = asyncio.run(client.run_agent("Test query", "researcher"))
        assert result == "Agent response"
