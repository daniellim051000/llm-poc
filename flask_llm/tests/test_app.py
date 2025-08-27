import json
import os
from unittest.mock import Mock, patch

import pytest
from app import app, get_agent
from models import User, db


class TestFlaskApp:
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app."""
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["LOGIN_DISABLED"] = True  # Disable login requirement for testing
        app.config["SECRET_KEY"] = "test-secret-key"

        with app.test_client() as client:
            with app.app_context():
                db.create_all()
                yield client
                db.session.remove()
                db.drop_all()

    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        with app.app_context():
            db.create_all()
            # Check if user already exists
            existing_user = User.query.filter_by(username="testuser").first()
            if existing_user:
                return existing_user
            user = User(username="testuser", email="test@example.com")
            user.set_password("testpassword")
            db.session.add(user)
            db.session.commit()
            return user

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "healthy"
        assert data["message"] == "LLM Business Data API is running"
        assert "/query" in data["endpoints"]

    def test_examples_endpoint(self, client):
        """Test the examples endpoint."""
        response = client.get("/examples")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert "sample_queries" in data
        assert isinstance(data["sample_queries"], list)
        assert len(data["sample_queries"]) > 0
        assert any("Company A" in query for query in data["sample_queries"])

    def test_index_requires_login(self, client):
        """Test that index page requires authentication."""
        response = client.get("/")
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.location

    @patch("app.get_agent")
    def test_query_endpoint_missing_question(self, mock_get_agent, client):
        """Test query endpoint with missing question parameter."""
        response = client.post(
            "/query", data=json.dumps({}), content_type="application/json"
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "error" in data
        assert "Missing 'question'" in data["error"]

    @patch("app.get_agent")
    def test_query_endpoint_success(self, mock_get_agent, client):
        """Test successful query endpoint."""
        # Mock the agent
        mock_agent = Mock()
        mock_agent.query.return_value = "Test response"
        mock_get_agent.return_value = mock_agent

        # Disable login requirement for this test
        app.config["LOGIN_DISABLED"] = True

        response = client.post(
            "/query",
            data=json.dumps({"question": "Test question"}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["question"] == "Test question"
        assert data["answer"] == "Test response"
        mock_agent.query.assert_called_once_with("Test question")

    @patch("app.get_agent")
    def test_query_endpoint_agent_error(self, mock_get_agent, client):
        """Test query endpoint when agent throws an error."""
        # Mock the agent to raise an exception
        mock_agent = Mock()
        mock_agent.query.side_effect = Exception("Agent error")
        mock_get_agent.return_value = mock_agent

        app.config["LOGIN_DISABLED"] = True

        response = client.post(
            "/query",
            data=json.dumps({"question": "Test question"}),
            content_type="application/json",
        )

        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "Agent error" in data["error"]

    def test_login_page_get(self, client):
        """Test GET request to login page."""
        response = client.get("/login")
        assert response.status_code == 200
        # Check that login template is rendered (contains form elements)
        assert b"username" in response.data
        assert b"password" in response.data

    def test_login_missing_credentials(self, client, test_user):
        """Test login with missing credentials."""
        with client.session_transaction() as session:
            session["_flashes"] = []

        response = client.post("/login", data={})
        assert response.status_code == 200
        # Should stay on login page - check that we're still on login page
        assert b"Sign in to access the system" in response.data

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials."""
        response = client.post(
            "/login", data={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 200
        # Should stay on login page
        assert b"Sign in to access the system" in response.data

    def test_login_successful(self, client, test_user):
        """Test successful login."""
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "testpassword"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        # Should redirect to index page after successful login

    def test_logout_requires_login(self, client):
        """Test that logout requires authentication."""
        response = client.get("/logout")
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.location


class TestGetAgent:
    """Test the get_agent function."""

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
            "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
        },
    )
    @patch("app.create_agent")
    def test_get_agent_success(self, mock_create_agent):
        """Test successful agent creation."""
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        # Reset the global agent variable
        import app

        app.agent = None

        agent = get_agent()
        assert agent == mock_agent
        mock_create_agent.assert_called_once_with(
            "test_key",
            "https://test.openai.azure.com/",
            "test_deployment",
            "2024-02-15-preview",
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_get_agent_missing_config(self):
        """Test agent creation with missing configuration."""
        # Reset the global agent variable
        import app

        app.agent = None

        with pytest.raises(ValueError) as exc_info:
            get_agent()

        assert "Missing required Azure OpenAI configuration" in str(exc_info.value)

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
        },
    )
    @patch("app.create_agent")
    def test_get_agent_default_api_version(self, mock_create_agent):
        """Test agent creation with default API version."""
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        # Reset the global agent variable
        import app

        app.agent = None

        agent = get_agent()
        # Check that create_agent was called with the correct parameters
        call_args = mock_create_agent.call_args[0]
        assert call_args[0] == "test_key"
        assert call_args[1] == "https://test.openai.azure.com/"
        assert call_args[2] == "test_deployment"
        # The API version should be the default from the environment or code
        assert call_args[3] in ["2024-02-15-preview", "2024-12-01-preview"]

    @patch.dict(
        os.environ,
        {
            "AZURE_OPENAI_API_KEY": "test_key",
            "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
        },
    )
    @patch("app.create_agent")
    def test_get_agent_singleton(self, mock_create_agent):
        """Test that get_agent returns the same instance on subsequent calls."""
        mock_agent = Mock()
        mock_create_agent.return_value = mock_agent

        # Reset the global agent variable
        import app

        app.agent = None

        agent1 = get_agent()
        agent2 = get_agent()

        assert agent1 == agent2
        # create_agent should only be called once
        mock_create_agent.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
