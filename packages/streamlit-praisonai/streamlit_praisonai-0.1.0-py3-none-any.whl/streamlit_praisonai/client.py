"""PraisonAI API client for Streamlit."""

from typing import List, Dict
import httpx


class PraisonAIClient:
    """Client for interacting with PraisonAI API."""

    def __init__(self, api_url: str = "http://localhost:8080", timeout: int = 300) -> None:
        self.api_url = api_url
        self.timeout = timeout

    def run_workflow(self, query: str) -> str:
        """Run the full PraisonAI workflow."""
        response = httpx.post(
            f"{self.api_url}/agents",
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def run_agent(self, query: str, agent: str) -> str:
        """Run a specific agent."""
        response = httpx.post(
            f"{self.api_url}/agents/{agent}",
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def list_agents(self) -> List[Dict]:
        """List available agents."""
        response = httpx.get(f"{self.api_url}/agents/list", timeout=30)
        response.raise_for_status()
        return response.json().get("agents", [])
