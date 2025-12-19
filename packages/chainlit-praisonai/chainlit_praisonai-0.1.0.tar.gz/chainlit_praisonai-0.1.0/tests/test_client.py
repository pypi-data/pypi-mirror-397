"""Chainlit PraisonAI Tests - TDD"""

import pytest


class TestPraisonAIClient:
    """Test PraisonAI client."""

    def test_client_class_exists(self):
        from chainlit_praisonai import PraisonAIClient
        assert PraisonAIClient is not None

    def test_client_default_api_url(self):
        from chainlit_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert client.api_url == "http://localhost:8080"

    def test_client_has_run_workflow_method(self):
        from chainlit_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_workflow')

    def test_client_has_run_agent_method(self):
        from chainlit_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_agent')


class TestPraisonAIClientExecution:
    """Test client execution."""

    @pytest.mark.asyncio
    async def test_run_workflow(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Test response"}
        )
        from chainlit_praisonai import PraisonAIClient
        client = PraisonAIClient()
        result = await client.run_workflow("Test query")
        assert result == "Test response"

    @pytest.mark.asyncio
    async def test_run_agent(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        from chainlit_praisonai import PraisonAIClient
        client = PraisonAIClient()
        result = await client.run_agent("Test query", "researcher")
        assert result == "Agent response"
