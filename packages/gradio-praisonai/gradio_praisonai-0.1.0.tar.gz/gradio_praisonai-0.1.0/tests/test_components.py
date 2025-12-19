"""Gradio PraisonAI Components Tests - TDD"""


class TestPraisonAIClient:
    """Test PraisonAI client."""

    def test_client_class_exists(self):
        from gradio_praisonai import PraisonAIClient
        assert PraisonAIClient is not None

    def test_client_default_api_url(self):
        from gradio_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert client.api_url == "http://localhost:8080"

    def test_client_has_run_workflow_method(self):
        from gradio_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_workflow')

    def test_client_has_run_agent_method(self):
        from gradio_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_agent')


class TestPraisonAIChatInterface:
    """Test PraisonAI chat interface."""

    def test_create_interface_function_exists(self):
        from gradio_praisonai import create_chat_interface
        assert create_chat_interface is not None
        assert callable(create_chat_interface)


class TestPraisonAIClientExecution:
    """Test client execution."""

    def test_run_workflow(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Test response"}
        )
        from gradio_praisonai import PraisonAIClient
        client = PraisonAIClient()
        result = client.run_workflow("Test query")
        assert result == "Test response"

    def test_run_agent(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        from gradio_praisonai import PraisonAIClient
        client = PraisonAIClient()
        result = client.run_agent("Test query", "researcher")
        assert result == "Agent response"
