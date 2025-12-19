"""PraisonAI Tools for LangChain."""

from typing import Optional, Type
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun


class PraisonAIInput(BaseModel):
    """Input schema for PraisonAI tool."""

    query: str = Field(description="The query or task to send to PraisonAI agents")
    agent: Optional[str] = Field(
        default=None,
        description="Optional specific agent name to run. If not provided, runs the default workflow.",
    )


class PraisonAITool(BaseTool):
    """Tool for running PraisonAI multi-agent workflows.

    This tool allows LangChain agents to leverage PraisonAI's multi-agent
    capabilities for complex tasks like research, content creation, and more.

    Example:
        ```python
        from langchain_praisonai import PraisonAITool

        tool = PraisonAITool(api_url="http://localhost:8080")
        result = tool.run({"query": "Research AI trends", "agent": "researcher"})
        ```
    """

    name: str = "praisonai"
    description: str = (
        "Run a PraisonAI multi-agent workflow. Use this tool when you need to "
        "leverage multiple AI agents working together to complete complex tasks "
        "like research, content creation, analysis, or any multi-step workflow. "
        "PraisonAI orchestrates specialized agents to produce high-quality results."
    )
    args_schema: Type[BaseModel] = PraisonAIInput
    api_url: str = "http://localhost:8080"
    timeout: int = 300

    def _run(
        self,
        query: str,
        agent: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run the PraisonAI tool synchronously.

        Args:
            query: The query or task to send to PraisonAI.
            agent: Optional specific agent to run.
            run_manager: Optional callback manager.

        Returns:
            The response from PraisonAI agents.
        """
        endpoint = f"{self.api_url}/agents/{agent}" if agent else f"{self.api_url}/agents"

        response = httpx.post(
            endpoint,
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    async def _arun(
        self,
        query: str,
        agent: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run the PraisonAI tool asynchronously.

        Args:
            query: The query or task to send to PraisonAI.
            agent: Optional specific agent to run.
            run_manager: Optional callback manager.

        Returns:
            The response from PraisonAI agents.
        """
        endpoint = f"{self.api_url}/agents/{agent}" if agent else f"{self.api_url}/agents"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("response", "")


class PraisonAIAgentInput(BaseModel):
    """Input schema for PraisonAI agent-specific tool."""

    query: str = Field(description="The query or task to send to the agent")


class PraisonAIAgentTool(BaseTool):
    """Tool for running a specific PraisonAI agent.

    This tool is pre-configured to run a specific agent, making it easier
    to use in agent chains where you want dedicated tools for each agent type.

    Example:
        ```python
        from langchain_praisonai import PraisonAIAgentTool

        researcher = PraisonAIAgentTool(agent_name="researcher")
        writer = PraisonAIAgentTool(agent_name="writer")

        # Use in an agent
        tools = [researcher, writer]
        ```
    """

    name: str = "praisonai_agent"
    description: str = "Run a specific PraisonAI agent"
    args_schema: Type[BaseModel] = PraisonAIAgentInput
    api_url: str = "http://localhost:8080"
    timeout: int = 300
    agent_name: str = ""

    def __init__(self, agent_name: str, **kwargs):
        """Initialize the agent tool.

        Args:
            agent_name: The name of the PraisonAI agent to run.
            **kwargs: Additional arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        self.agent_name = agent_name
        self.name = f"praisonai_{agent_name}"
        self.description = (
            f"Run the PraisonAI {agent_name} agent. Use this tool when you need "
            f"the specialized capabilities of the {agent_name} agent."
        )

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Run the specific PraisonAI agent synchronously."""
        endpoint = f"{self.api_url}/agents/{self.agent_name}"

        response = httpx.post(
            endpoint,
            json={"query": query},
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    async def _arun(
        self,
        query: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Run the specific PraisonAI agent asynchronously."""
        endpoint = f"{self.api_url}/agents/{self.agent_name}"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                json={"query": query},
                timeout=self.timeout,
            )
            response.raise_for_status()

        data = response.json()
        return data.get("response", "")


class PraisonAIListAgentsTool(BaseTool):
    """Tool for listing available PraisonAI agents.

    This tool retrieves the list of available agents from a PraisonAI server,
    which can be useful for dynamic agent selection.

    Example:
        ```python
        from langchain_praisonai import PraisonAIListAgentsTool

        list_tool = PraisonAIListAgentsTool()
        agents = list_tool.run({})
        ```
    """

    name: str = "praisonai_list_agents"
    description: str = (
        "List all available PraisonAI agents. Use this to discover what "
        "specialized agents are available for different tasks."
    )
    api_url: str = "http://localhost:8080"
    timeout: int = 30

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """List available agents synchronously."""
        endpoint = f"{self.api_url}/agents/list"

        response = httpx.get(endpoint, timeout=self.timeout)
        response.raise_for_status()

        data = response.json()
        agents = data.get("agents", [])

        if not agents:
            return "No agents available."

        agent_list = "\n".join(
            [f"- {agent.get('name', 'Unknown')} (id: {agent.get('id', 'unknown')})" for agent in agents]
        )
        return f"Available PraisonAI agents:\n{agent_list}"

    async def _arun(
        self,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """List available agents asynchronously."""
        endpoint = f"{self.api_url}/agents/list"

        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint, timeout=self.timeout)
            response.raise_for_status()

        data = response.json()
        agents = data.get("agents", [])

        if not agents:
            return "No agents available."

        agent_list = "\n".join(
            [f"- {agent.get('name', 'Unknown')} (id: {agent.get('id', 'unknown')})" for agent in agents]
        )
        return f"Available PraisonAI agents:\n{agent_list}"
