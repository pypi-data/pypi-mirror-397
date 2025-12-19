"""PraisonAI API client for Discord bot."""

import httpx


class PraisonAIClient:
    """Client for interacting with PraisonAI API.

    Example:
        ```python
        client = PraisonAIClient(api_url="http://localhost:8080")
        result = await client.run_workflow("Research AI trends")
        ```
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        timeout: int = 300,
    ) -> None:
        """Initialize the PraisonAI client.

        Args:
            api_url: The URL of the PraisonAI API server.
            timeout: Request timeout in seconds.
        """
        self.api_url = api_url
        self.timeout = timeout

    async def run_workflow(self, query: str) -> str:
        """Run the full PraisonAI multi-agent workflow.

        Args:
            query: The query or task to send to the workflow.

        Returns:
            The response from PraisonAI.
        """
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
        """Run a specific PraisonAI agent.

        Args:
            query: The query or task to send to the agent.
            agent: The name/id of the agent to run.

        Returns:
            The response from the agent.
        """
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
        """List all available PraisonAI agents.

        Returns:
            A formatted string listing available agents.
        """
        endpoint = f"{self.api_url}/agents/list"

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, timeout=30)
            response.raise_for_status()

        data = response.json()
        agents = data.get("agents", [])

        if not agents:
            return "No agents available."

        agent_list = "\n".join(
            [f"• **{agent.get('name', 'Unknown')}** (id: `{agent.get('id', 'unknown')}`)" for agent in agents]
        )
        return f"**Available PraisonAI Agents:**\n{agent_list}"
