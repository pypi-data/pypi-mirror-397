"""
Test PraisonAI LangChain Tools - TDD Tests

Phase 1: Tool Definition Tests
- Test PraisonAITool class exists and has correct attributes
- Test tool name and description
- Test input schema validation

Phase 2: Tool Execution Tests  
- Test synchronous tool execution
- Test async tool execution
- Test error handling

Phase 3: Integration Tests
- Test with mock PraisonAI server
- Test agent parameter handling
- Test timeout configuration
"""

import pytest
import httpx


class TestPraisonAIToolDefinition:
    """Test PraisonAI Tool class definition."""

    def test_tool_class_exists(self):
        """Test that PraisonAITool class can be imported."""
        from langchain_praisonai import PraisonAITool
        assert PraisonAITool is not None

    def test_tool_has_correct_name(self):
        """Test tool has correct name attribute."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        assert tool.name == "praisonai"

    def test_tool_has_description(self):
        """Test tool has a description."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        assert tool.description is not None
        assert len(tool.description) > 0
        assert "PraisonAI" in tool.description

    def test_tool_default_api_url(self):
        """Test tool has default API URL."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        assert tool.api_url == "http://localhost:8080"

    def test_tool_custom_api_url(self):
        """Test tool accepts custom API URL."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool(api_url="http://custom:9000")
        assert tool.api_url == "http://custom:9000"

    def test_tool_default_timeout(self):
        """Test tool has default timeout."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        assert tool.timeout == 300

    def test_tool_custom_timeout(self):
        """Test tool accepts custom timeout."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool(timeout=600)
        assert tool.timeout == 600


class TestPraisonAIToolInputSchema:
    """Test PraisonAI Tool input schema."""

    def test_tool_has_args_schema(self):
        """Test tool has args_schema defined."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        assert tool.args_schema is not None

    def test_args_schema_has_query_field(self):
        """Test args schema has query field."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        schema = tool.args_schema.model_json_schema()
        assert "query" in schema["properties"]

    def test_args_schema_has_agent_field(self):
        """Test args schema has optional agent field."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        schema = tool.args_schema.model_json_schema()
        assert "agent" in schema["properties"]

    def test_query_is_required(self):
        """Test query field is required."""
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        schema = tool.args_schema.model_json_schema()
        assert "query" in schema.get("required", [])


class TestPraisonAIToolExecution:
    """Test PraisonAI Tool execution."""

    def test_run_with_query_only(self, httpx_mock):
        """Test running tool with query only."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Test response from PraisonAI"}
        )
        
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        result = tool._run(query="What is AI?")
        
        assert result == "Test response from PraisonAI"

    def test_run_with_specific_agent(self, httpx_mock):
        """Test running tool with specific agent."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Research results"}
        )
        
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        result = tool._run(query="Research AI trends", agent="researcher")
        
        assert result == "Research results"

    def test_run_handles_empty_response(self, httpx_mock):
        """Test tool handles empty response gracefully."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={}
        )
        
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        result = tool._run(query="Test query")
        
        assert result == ""

    def test_run_handles_connection_error(self, httpx_mock):
        """Test tool handles connection errors."""
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
        
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        
        with pytest.raises(Exception):
            tool._run(query="Test query")


class TestPraisonAIToolAsync:
    """Test PraisonAI Tool async execution."""

    @pytest.mark.asyncio
    async def test_arun_with_query(self, httpx_mock):
        """Test async running tool with query."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Async response"}
        )
        
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        result = await tool._arun(query="Async test")
        
        assert result == "Async response"

    @pytest.mark.asyncio
    async def test_arun_with_agent(self, httpx_mock):
        """Test async running tool with specific agent."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/writer",
            method="POST",
            json={"response": "Written content"}
        )
        
        from langchain_praisonai import PraisonAITool
        tool = PraisonAITool()
        result = await tool._arun(query="Write an article", agent="writer")
        
        assert result == "Written content"


class TestPraisonAIAgentTool:
    """Test PraisonAI Agent-specific Tool."""

    def test_agent_tool_class_exists(self):
        """Test PraisonAIAgentTool class exists."""
        from langchain_praisonai import PraisonAIAgentTool
        assert PraisonAIAgentTool is not None

    def test_agent_tool_requires_agent_name(self):
        """Test agent tool requires agent name."""
        from langchain_praisonai import PraisonAIAgentTool
        tool = PraisonAIAgentTool(agent_name="researcher")
        assert tool.agent_name == "researcher"

    def test_agent_tool_name_includes_agent(self):
        """Test agent tool name includes agent name."""
        from langchain_praisonai import PraisonAIAgentTool
        tool = PraisonAIAgentTool(agent_name="researcher")
        assert "researcher" in tool.name

    def test_agent_tool_run(self, httpx_mock):
        """Test agent tool execution."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        
        from langchain_praisonai import PraisonAIAgentTool
        tool = PraisonAIAgentTool(agent_name="researcher")
        result = tool._run(query="Research something")
        
        assert result == "Agent response"


class TestPraisonAIListAgentsTool:
    """Test PraisonAI List Agents Tool."""

    def test_list_agents_tool_exists(self):
        """Test PraisonAIListAgentsTool class exists."""
        from langchain_praisonai import PraisonAIListAgentsTool
        assert PraisonAIListAgentsTool is not None

    def test_list_agents_tool_name(self):
        """Test list agents tool has correct name."""
        from langchain_praisonai import PraisonAIListAgentsTool
        tool = PraisonAIListAgentsTool()
        assert tool.name == "praisonai_list_agents"

    def test_list_agents_run(self, httpx_mock):
        """Test list agents tool execution."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/list",
            method="GET",
            json={"agents": [
                {"name": "Researcher", "id": "researcher"},
                {"name": "Writer", "id": "writer"}
            ]}
        )
        
        from langchain_praisonai import PraisonAIListAgentsTool
        tool = PraisonAIListAgentsTool()
        result = tool._run()
        
        assert "researcher" in result.lower() or "Researcher" in result


# httpx_mock fixture is provided by pytest-httpx plugin automatically
