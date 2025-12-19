"""PraisonAI API client for Telegram bot."""

import httpx


class PraisonAIClient:
    """Client for interacting with PraisonAI API."""

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        timeout: int = 300,
    ) -> None:
        self.api_url = api_url
        self.timeout = timeout

    async def run_workflow(self, query: str) -> str:
        """Run the full PraisonAI multi-agent workflow."""
        endpoint = f"{self.api_url}/agents"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    async def run_agent(self, query: str, agent: str) -> str:
        """Run a specific PraisonAI agent."""
        endpoint = f"{self.api_url}/agents/{agent}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    async def list_agents(self) -> str:
        """List all available PraisonAI agents."""
        endpoint = f"{self.api_url}/agents/list"

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, timeout=30)
            response.raise_for_status()

        data = response.json()
        agents = data.get("agents", [])

        if not agents:
            return "No agents available."

        agent_list = "\n".join(
            [f"• *{agent.get('name', 'Unknown')}* (id: `{agent.get('id', 'unknown')}`)" for agent in agents]
        )
        return f"*Available PraisonAI Agents:*\n{agent_list}"
