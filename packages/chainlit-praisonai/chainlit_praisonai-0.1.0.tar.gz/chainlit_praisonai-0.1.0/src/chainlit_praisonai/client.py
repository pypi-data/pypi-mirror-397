"""PraisonAI API client for Chainlit."""

from typing import List, Dict
import httpx


class PraisonAIClient:
    """Async client for interacting with PraisonAI API."""

    def __init__(self, api_url: str = "http://localhost:8080", timeout: int = 300) -> None:
        self.api_url = api_url
        self.timeout = timeout

    async def run_workflow(self, query: str) -> str:
        """Run the full PraisonAI workflow."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/agents",
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()
        return response.json().get("response", "")

    async def run_agent(self, query: str, agent: str) -> str:
        """Run a specific agent."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/agents/{agent}",
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()
        return response.json().get("response", "")

    async def list_agents(self) -> List[Dict]:
        """List available agents."""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/agents/list", timeout=30)
            response.raise_for_status()
        return response.json().get("agents", [])
