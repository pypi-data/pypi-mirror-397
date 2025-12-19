"""PraisonAI ToolSpec for LlamaIndex."""

import httpx
from llama_index.core.tools.tool_spec.base import BaseToolSpec


class PraisonAIToolSpec(BaseToolSpec):
    """Tool specification for PraisonAI multi-agent framework.

    This ToolSpec provides tools to interact with PraisonAI's multi-agent
    system, allowing LlamaIndex agents to leverage specialized AI agents
    for complex tasks.

    Example:
        ```python
        from llama_index_tools_praisonai import PraisonAIToolSpec
        from llama_index.agent.openai import OpenAIAgent

        spec = PraisonAIToolSpec(api_url="http://localhost:8080")
        tools = spec.to_tool_list()

        agent = OpenAIAgent.from_tools(tools)
        response = agent.chat("Research the latest AI trends")
        ```
    """

    spec_functions = ["run_agent", "run_workflow", "list_agents"]

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        timeout: int = 300,
    ) -> None:
        """Initialize the PraisonAI ToolSpec.

        Args:
            api_url: The URL of the PraisonAI API server.
            timeout: Request timeout in seconds.
        """
        self.api_url = api_url
        self.timeout = timeout

    def run_agent(self, query: str, agent: str) -> str:
        """Run a specific PraisonAI agent with a query.

        Use this tool when you need to run a specific specialized agent
        like a researcher, writer, or editor.

        Args:
            query: The query or task to send to the agent.
            agent: The name/id of the agent to run (e.g., 'researcher', 'writer').

        Returns:
            The response from the PraisonAI agent.
        """
        endpoint = f"{self.api_url}/agents/{agent}"

        response = httpx.post(
            endpoint,
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    def run_workflow(self, query: str) -> str:
        """Run the full PraisonAI multi-agent workflow.

        Use this tool when you need multiple agents to collaborate on a
        complex task. The workflow will automatically orchestrate the
        appropriate agents.

        Args:
            query: The query or task to send to the workflow.

        Returns:
            The final response from the multi-agent workflow.
        """
        endpoint = f"{self.api_url}/agents"

        response = httpx.post(
            endpoint,
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    def list_agents(self) -> str:
        """List all available PraisonAI agents.

        Use this tool to discover what specialized agents are available
        for different tasks.

        Returns:
            A formatted string listing available agents.
        """
        endpoint = f"{self.api_url}/agents/list"

        response = httpx.get(endpoint, timeout=30)
        response.raise_for_status()

        data = response.json()
        agents = data.get("agents", [])

        if not agents:
            return "No agents available."

        agent_list = "\n".join(
            [f"- {agent.get('name', 'Unknown')} (id: {agent.get('id', 'unknown')})" for agent in agents]
        )
        return f"Available PraisonAI agents:\n{agent_list}"

    async def arun_agent(self, query: str, agent: str) -> str:
        """Async version of run_agent.

        Args:
            query: The query or task to send to the agent.
            agent: The name/id of the agent to run.

        Returns:
            The response from the PraisonAI agent.
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

    async def arun_workflow(self, query: str) -> str:
        """Async version of run_workflow.

        Args:
            query: The query or task to send to the workflow.

        Returns:
            The final response from the multi-agent workflow.
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

    async def alist_agents(self) -> str:
        """Async version of list_agents.

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
            [f"- {agent.get('name', 'Unknown')} (id: {agent.get('id', 'unknown')})" for agent in agents]
        )
        return f"Available PraisonAI agents:\n{agent_list}"
