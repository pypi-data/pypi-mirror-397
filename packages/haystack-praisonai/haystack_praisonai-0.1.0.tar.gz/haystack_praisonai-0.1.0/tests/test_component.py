"""Haystack PraisonAI Component Tests - TDD"""


class TestPraisonAIComponent:
    """Test PraisonAI Haystack component."""

    def test_component_class_exists(self):
        from haystack_praisonai import PraisonAIComponent
        assert PraisonAIComponent is not None

    def test_component_default_api_url(self):
        from haystack_praisonai import PraisonAIComponent
        component = PraisonAIComponent()
        assert component.api_url == "http://localhost:8080"

    def test_component_custom_api_url(self):
        from haystack_praisonai import PraisonAIComponent
        component = PraisonAIComponent(api_url="http://custom:9000")
        assert component.api_url == "http://custom:9000"

    def test_component_has_run_method(self):
        from haystack_praisonai import PraisonAIComponent
        component = PraisonAIComponent()
        assert hasattr(component, 'run')

    def test_component_is_haystack_component(self):
        from haystack_praisonai import PraisonAIComponent
        # Check if decorated with @component
        assert hasattr(PraisonAIComponent, '__haystack_component__') or hasattr(PraisonAIComponent, 'run')


class TestPraisonAIComponentExecution:
    """Test PraisonAI component execution."""

    def test_run_returns_dict(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Test response"}
        )
        from haystack_praisonai import PraisonAIComponent
        component = PraisonAIComponent()
        result = component.run(query="Test query")
        assert isinstance(result, dict)
        assert "response" in result

    def test_run_with_agent(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents/researcher",
            method="POST",
            json={"response": "Agent response"}
        )
        from haystack_praisonai import PraisonAIComponent
        component = PraisonAIComponent(agent="researcher")
        result = component.run(query="Test query")
        assert result["response"] == "Agent response"

    def test_run_workflow(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8080/agents",
            method="POST",
            json={"response": "Workflow response"}
        )
        from haystack_praisonai import PraisonAIComponent
        component = PraisonAIComponent()
        result = component.run(query="Test query")
        assert result["response"] == "Workflow response"
