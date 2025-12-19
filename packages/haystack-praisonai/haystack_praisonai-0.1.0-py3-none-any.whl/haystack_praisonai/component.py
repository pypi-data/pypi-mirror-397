"""PraisonAI component for Haystack pipelines."""

from typing import Optional
import httpx
from haystack import component


@component
class PraisonAIComponent:
    """Haystack component for running PraisonAI multi-agent workflows.

    Example:
        ```python
        from haystack import Pipeline
        from haystack_praisonai import PraisonAIComponent

        pipeline = Pipeline()
        pipeline.add_component("praisonai", PraisonAIComponent())
        result = pipeline.run({"praisonai": {"query": "Research AI trends"}})
        ```
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        agent: Optional[str] = None,
        timeout: int = 300,
    ) -> None:
        """Initialize the PraisonAI component.

        Args:
            api_url: The URL of the PraisonAI API server.
            agent: Optional specific agent to run.
            timeout: Request timeout in seconds.
        """
        self.api_url = api_url
        self.agent = agent
        self.timeout = timeout

    @component.output_types(response=str)
    def run(self, query: str) -> dict:
        """Run the PraisonAI workflow or agent.

        Args:
            query: The query or task to send to PraisonAI.

        Returns:
            Dictionary with 'response' key containing the result.
        """
        if self.agent:
            endpoint = f"{self.api_url}/agents/{self.agent}"
        else:
            endpoint = f"{self.api_url}/agents"

        response = httpx.post(
            endpoint,
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return {"response": data.get("response", "")}
