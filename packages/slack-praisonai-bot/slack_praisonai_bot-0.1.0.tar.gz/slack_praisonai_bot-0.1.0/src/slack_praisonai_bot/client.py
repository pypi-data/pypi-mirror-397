"""PraisonAI API client for Slack bot."""

import httpx


class PraisonAIClient:
    """Client for interacting with PraisonAI API."""

    def __init__(self, api_url: str = "http://localhost:8080", timeout: int = 300) -> None:
        self.api_url = api_url
        self.timeout = timeout

    async def run_workflow(self, query: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/agents",
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()
        return response.json().get("response", "")

    async def run_agent(self, query: str, agent: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/agents/{agent}",
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()
        return response.json().get("response", "")

    async def list_agents(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.api_url}/agents/list", timeout=30)
            response.raise_for_status()
        agents = response.json().get("agents", [])
        if not agents:
            return "No agents available."
        return "\n".join([f"• *{a.get('name')}* (`{a.get('id')}`)" for a in agents])
