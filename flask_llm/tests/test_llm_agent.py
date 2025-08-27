from unittest.mock import Mock, patch

import pytest
from llm_agent import BusinessDataAgent, create_agent


class TestBusinessDataAgent:
    def setup_method(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.azure_endpoint = "https://test.openai.azure.com/"
        self.deployment_name = "test_deployment"
        self.api_version = "2024-02-15-preview"

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_agent_initialization(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test BusinessDataAgent initialization."""
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        mock_executor = Mock()
        mock_agent_executor.return_value = mock_executor

        agent = BusinessDataAgent(
            self.api_key, self.azure_endpoint, self.deployment_name, self.api_version
        )

        # Verify AzureChatOpenAI was initialized correctly
        mock_azure_openai.assert_called_once_with(
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            deployment_name=self.deployment_name,
            temperature=0,
        )

        # Verify tools are set up
        assert len(agent.tools) == 10  # Should have 10 tools based on imports

        # Check that all expected tools are present
        tool_names = [tool.name for tool in agent.tools]
        expected_tools = [
            "customer_search",
            "customer_invoices",
            "customer_contracts",
            "customer_services",
            "item_search",
            "invoice_search",
            "active_contracts",
            "serial_lookup",
            "service_history",
            "web_search",
        ]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        # Verify prompt template was created
        assert agent.prompt is not None

        # Verify agent was created with correct parameters
        mock_create_agent.assert_called_once_with(mock_llm, agent.tools, agent.prompt)

        # Verify agent executor was created
        mock_agent_executor.assert_called_once_with(
            agent=mock_agent,
            tools=agent.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_query_success(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test successful query execution."""
        mock_executor = Mock()
        mock_agent_executor.return_value = mock_executor
        mock_executor.invoke.return_value = {"output": "Test response"}

        agent = BusinessDataAgent(
            self.api_key, self.azure_endpoint, self.deployment_name
        )

        result = agent.query("What are the active contracts?")

        assert result == "Test response"
        mock_executor.invoke.assert_called_once_with(
            {"input": "What are the active contracts?"}
        )

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_query_error_handling(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test query error handling."""
        mock_executor = Mock()
        mock_agent_executor.return_value = mock_executor
        mock_executor.invoke.side_effect = Exception("LLM error")

        agent = BusinessDataAgent(
            self.api_key, self.azure_endpoint, self.deployment_name
        )

        result = agent.query("Test question")

        assert "Error processing query: LLM error" in result

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_default_api_version(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test default API version is used when not specified."""
        agent = BusinessDataAgent(
            self.api_key, self.azure_endpoint, self.deployment_name
        )

        # Check that default API version was used
        call_args = mock_azure_openai.call_args
        assert call_args[1]["api_version"] == "2024-02-15-preview"

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_prompt_template_content(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test that prompt template contains expected content."""
        agent = BusinessDataAgent(
            self.api_key, self.azure_endpoint, self.deployment_name
        )

        # Check that prompt contains expected instructions
        prompt_messages = agent.prompt.messages
        system_message_template = prompt_messages[0]
        # Extract the content from the SystemMessagePromptTemplate
        system_message = system_message_template.prompt.template

        assert "business data assistant" in system_message
        assert "tools that can retrieve data" in system_message
        assert "web_search tool" in system_message
        assert "search_type='scrape'" in system_message
        assert "search_type='search'" in system_message

    def test_agent_tools_are_callable(self):
        """Test that all tools in the agent are callable."""
        with patch("llm_agent.AzureChatOpenAI"), patch(
            "llm_agent.create_openai_tools_agent"
        ), patch("llm_agent.AgentExecutor"):
            agent = BusinessDataAgent(
                self.api_key, self.azure_endpoint, self.deployment_name
            )

            for tool in agent.tools:
                assert hasattr(tool, "_run"), (
                    f"Tool {tool.name} should have _run method"
                )
                assert hasattr(tool, "name"), (
                    f"Tool {tool.name} should have name attribute"
                )
                assert hasattr(tool, "description"), (
                    f"Tool {tool.name} should have description"
                )


class TestCreateAgentFunction:
    """Test the create_agent factory function."""

    @patch("llm_agent.BusinessDataAgent")
    def test_create_agent_default_version(self, mock_business_agent):
        """Test create_agent with default API version."""
        mock_instance = Mock()
        mock_business_agent.return_value = mock_instance

        result = create_agent("key", "endpoint", "deployment")

        mock_business_agent.assert_called_once_with(
            "key", "endpoint", "deployment", "2024-02-15-preview"
        )
        assert result == mock_instance

    @patch("llm_agent.BusinessDataAgent")
    def test_create_agent_custom_version(self, mock_business_agent):
        """Test create_agent with custom API version."""
        mock_instance = Mock()
        mock_business_agent.return_value = mock_instance

        result = create_agent("key", "endpoint", "deployment", "2024-05-01-preview")

        mock_business_agent.assert_called_once_with(
            "key", "endpoint", "deployment", "2024-05-01-preview"
        )
        assert result == mock_instance


class TestAgentIntegration:
    """Integration tests for the agent with mocked external dependencies."""

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_agent_full_workflow(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test full workflow from initialization to query execution."""
        # Set up mocks
        mock_llm = Mock()
        mock_azure_openai.return_value = mock_llm
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent
        mock_executor = Mock()
        mock_agent_executor.return_value = mock_executor
        mock_executor.invoke.return_value = {
            "output": "Customer data retrieved successfully"
        }

        # Create agent and run query
        agent = BusinessDataAgent("key", "endpoint", "deployment")
        result = agent.query("Find all active contracts for Company A")

        # Verify the full chain was executed
        assert result == "Customer data retrieved successfully"
        mock_azure_openai.assert_called_once()
        mock_create_agent.assert_called_once()
        mock_agent_executor.assert_called_once()
        mock_executor.invoke.assert_called_once_with(
            {"input": "Find all active contracts for Company A"}
        )

    @patch("llm_agent.AzureChatOpenAI")
    @patch("llm_agent.create_openai_tools_agent")
    @patch("llm_agent.AgentExecutor")
    def test_multiple_queries_same_agent(
        self, mock_agent_executor, mock_create_agent, mock_azure_openai
    ):
        """Test that the same agent can handle multiple queries."""
        mock_executor = Mock()
        mock_agent_executor.return_value = mock_executor
        mock_executor.invoke.side_effect = [
            {"output": "First response"},
            {"output": "Second response"},
        ]

        agent = BusinessDataAgent("key", "endpoint", "deployment")

        result1 = agent.query("First query")
        result2 = agent.query("Second query")

        assert result1 == "First response"
        assert result2 == "Second response"
        assert mock_executor.invoke.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__])
