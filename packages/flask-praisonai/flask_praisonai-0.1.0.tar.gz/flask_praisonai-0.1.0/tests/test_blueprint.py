"""Flask PraisonAI Blueprint Tests - TDD"""


class TestPraisonAIClient:
    """Test PraisonAI client."""

    def test_client_class_exists(self):
        from flask_praisonai import PraisonAIClient
        assert PraisonAIClient is not None

    def test_client_default_api_url(self):
        from flask_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert client.api_url == "http://localhost:8080"

    def test_client_has_run_workflow_method(self):
        from flask_praisonai import PraisonAIClient
        client = PraisonAIClient()
        assert hasattr(client, 'run_workflow')


class TestPraisonAIBlueprint:
    """Test PraisonAI blueprint."""

    def test_create_blueprint_function_exists(self):
        from flask_praisonai import create_blueprint
        assert create_blueprint is not None
        assert callable(create_blueprint)

    def test_create_blueprint_returns_blueprint(self):
        from flask_praisonai import create_blueprint
        from flask import Blueprint
        bp = create_blueprint()
        assert isinstance(bp, Blueprint)


class TestPraisonAIClientExecution:
    """Test client execution."""

    def test_run_workflow(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Test response"}
        )
        from flask_praisonai import PraisonAIClient
        client = PraisonAIClient()
        result = client.run_workflow("Test query")
        assert result == "Test response"

    def test_run_agent(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        from flask_praisonai import PraisonAIClient
        client = PraisonAIClient()
        result = client.run_agent("Test query", "researcher")
        assert result == "Agent response"
