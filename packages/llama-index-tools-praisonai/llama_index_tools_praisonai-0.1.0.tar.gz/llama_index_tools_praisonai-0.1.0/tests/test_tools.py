"""
Test PraisonAI LlamaIndex Tools - TDD Tests

Phase 1: Tool Definition Tests
- Test PraisonAIToolSpec class exists
- Test tool methods exist
- Test tool metadata

Phase 2: Tool Execution Tests
- Test run_agent method
- Test run_workflow method
- Test list_agents method

Phase 3: FunctionTool Tests
- Test creating FunctionTool from spec
- Test tool execution via FunctionTool
"""

import pytest
import httpx


class TestPraisonAIToolSpecDefinition:
    """Test PraisonAI ToolSpec class definition."""

    def test_toolspec_class_exists(self):
        """Test that PraisonAIToolSpec class can be imported."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        assert PraisonAIToolSpec is not None

    def test_toolspec_has_spec_functions(self):
        """Test toolspec has spec_functions attribute."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert hasattr(spec, 'spec_functions')
        assert len(spec.spec_functions) > 0

    def test_toolspec_default_api_url(self):
        """Test toolspec has default API URL."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert spec.api_url == "http://localhost:8080"

    def test_toolspec_custom_api_url(self):
        """Test toolspec accepts custom API URL."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec(api_url="http://custom:9000")
        assert spec.api_url == "http://custom:9000"

    def test_toolspec_default_timeout(self):
        """Test toolspec has default timeout."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert spec.timeout == 300

    def test_toolspec_custom_timeout(self):
        """Test toolspec accepts custom timeout."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec(timeout=600)
        assert spec.timeout == 600


class TestPraisonAIToolSpecMethods:
    """Test PraisonAI ToolSpec methods exist."""

    def test_has_run_agent_method(self):
        """Test toolspec has run_agent method."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert hasattr(spec, 'run_agent')
        assert callable(spec.run_agent)

    def test_has_run_workflow_method(self):
        """Test toolspec has run_workflow method."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert hasattr(spec, 'run_workflow')
        assert callable(spec.run_workflow)

    def test_has_list_agents_method(self):
        """Test toolspec has list_agents method."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert hasattr(spec, 'list_agents')
        assert callable(spec.list_agents)

    def test_spec_functions_contains_methods(self):
        """Test spec_functions contains all tool methods."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        assert 'run_agent' in spec.spec_functions
        assert 'run_workflow' in spec.spec_functions
        assert 'list_agents' in spec.spec_functions


class TestPraisonAIToolSpecExecution:
    """Test PraisonAI ToolSpec execution."""

    def test_run_agent_with_query(self, httpx_mock):
        """Test run_agent with query."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Research results from PraisonAI"}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = spec.run_agent(query="Research AI trends", agent="researcher")
        
        assert result == "Research results from PraisonAI"

    def test_run_workflow_with_query(self, httpx_mock):
        """Test run_workflow with query."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Workflow completed"}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = spec.run_workflow(query="Complete the content pipeline")
        
        assert result == "Workflow completed"

    def test_list_agents(self, httpx_mock):
        """Test list_agents method."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/list",
            method="GET",
            json={"agents": [
                {"name": "Researcher", "id": "researcher"},
                {"name": "Writer", "id": "writer"}
            ]}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = spec.list_agents()
        
        assert "researcher" in result.lower() or "Researcher" in result

    def test_run_agent_handles_empty_response(self, httpx_mock):
        """Test run_agent handles empty response."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/test",
            method="POST",
            json={}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = spec.run_agent(query="Test", agent="test")
        
        assert result == ""

    def test_run_agent_handles_connection_error(self, httpx_mock):
        """Test run_agent handles connection errors."""
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        
        with pytest.raises(Exception):
            spec.run_agent(query="Test", agent="test")


class TestPraisonAIFunctionTools:
    """Test creating FunctionTools from ToolSpec."""

    def test_to_tool_list_returns_tools(self):
        """Test to_tool_list returns list of tools."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        tools = spec.to_tool_list()
        
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_to_tool_list_tools_are_function_tools(self):
        """Test tools are FunctionTool instances."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        from llama_index.core.tools import FunctionTool
        
        spec = PraisonAIToolSpec()
        tools = spec.to_tool_list()
        
        for tool in tools:
            assert isinstance(tool, FunctionTool)

    def test_tools_have_metadata(self):
        """Test tools have proper metadata."""
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        tools = spec.to_tool_list()
        
        for tool in tools:
            assert tool.metadata.name is not None
            assert tool.metadata.description is not None


class TestPraisonAIAsyncExecution:
    """Test async execution of PraisonAI tools."""

    @pytest.mark.asyncio
    async def test_async_run_agent(self, httpx_mock):
        """Test async run_agent."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Async research results"}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = await spec.arun_agent(query="Research async", agent="researcher")
        
        assert result == "Async research results"

    @pytest.mark.asyncio
    async def test_async_run_workflow(self, httpx_mock):
        """Test async run_workflow."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Async workflow done"}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = await spec.arun_workflow(query="Run async workflow")
        
        assert result == "Async workflow done"

    @pytest.mark.asyncio
    async def test_async_list_agents(self, httpx_mock):
        """Test async list_agents."""
        httpx_mock.add_response(
            url="http://localhost:8080/agents/list",
            method="GET",
            json={"agents": [{"name": "Agent1", "id": "agent1"}]}
        )
        
        from llama_index_tools_praisonai import PraisonAIToolSpec
        spec = PraisonAIToolSpec()
        result = await spec.alist_agents()
        
        assert "agent1" in result.lower() or "Agent1" in result


# httpx_mock fixture is provided by pytest-httpx plugin automatically
