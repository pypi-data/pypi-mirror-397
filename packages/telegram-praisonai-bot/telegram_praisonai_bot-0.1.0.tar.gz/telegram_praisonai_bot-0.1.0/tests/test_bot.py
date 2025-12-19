"""
Telegram PraisonAI Bot Tests - TDD
"""

import pytest
import httpx


class TestPraisonAIClient:
    """Test PraisonAI API client."""

    def test_client_class_exists(self):
        """Test PraisonAIClient class exists."""
        from telegram_praisonai_bot import PraisonAIClient
        assert PraisonAIClient is not None

    def test_client_default_api_url(self):
        """Test client has default API URL."""
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        assert client.api_url == "http://localhost:8080"

    def test_client_custom_api_url(self):
        """Test client accepts custom API URL."""
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient(api_url="http://custom:9000")
        assert client.api_url == "http://custom:9000"

    def test_client_has_run_agent_method(self):
        """Test client has run_agent method."""
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_agent')
        assert callable(client.run_agent)

    def test_client_has_run_workflow_method(self):
        """Test client has run_workflow method."""
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_workflow')
        assert callable(client.run_workflow)

    def test_client_has_list_agents_method(self):
        """Test client has list_agents method."""
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'list_agents')
        assert callable(client.list_agents)


class TestPraisonAIClientExecution:
    """Test PraisonAI client execution."""

    @pytest.mark.asyncio
    async def test_run_workflow(self, httpx_mock):
        """Test run_workflow method."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Workflow response"}
        )
        
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        result = await client.run_workflow("Test query")
        
        assert result == "Workflow response"

    @pytest.mark.asyncio
    async def test_run_agent(self, httpx_mock):
        """Test run_agent method."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        result = await client.run_agent("Test query", "researcher")
        
        assert result == "Agent response"

    @pytest.mark.asyncio
    async def test_list_agents(self, httpx_mock):
        """Test list_agents method."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/list",
            method="GET",
            json={"agents": [
                {"name": "Researcher", "id": "researcher"},
                {"name": "Writer", "id": "writer"}
            ]}
        )
        
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        result = await client.list_agents()
        
        assert "researcher" in result.lower() or "Researcher" in result

    @pytest.mark.asyncio
    async def test_run_workflow_handles_error(self, httpx_mock):
        """Test run_workflow handles connection errors."""
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
        
        from telegram_praisonai_bot import PraisonAIClient
        client = PraisonAIClient()
        
        with pytest.raises(Exception):
            await client.run_workflow("Test query")


# httpx_mock fixture is provided by pytest-httpx plugin automatically
