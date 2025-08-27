from unittest.mock import Mock

import pytest
from app import app, db
from models import User


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def test_user():
    """Create a test user in the database."""
    with app.app_context():
        db.create_all()
        user = User(username="testuser")
        user.set_password("testpassword")
        db.session.add(user)
        db.session.commit()
        yield user


@pytest.fixture
def authenticated_client(client, test_user):
    """Create a client with an authenticated user."""
    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_user.id)
        sess["_fresh"] = True
    yield client


@pytest.fixture
def mock_agent():
    """Create a mock agent for testing."""
    mock = Mock()
    mock.query.return_value = "Mock agent response"
    return mock


@pytest.fixture
def mock_azure_config():
    """Mock Azure OpenAI configuration."""
    return {
        "AZURE_OPENAI_API_KEY": "test_key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com/",
        "AZURE_OPENAI_DEPLOYMENT_NAME": "test_deployment",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview",
    }


@pytest.fixture
def mock_requests_response():
    """Create a mock requests response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"test": "data"}
    return mock
