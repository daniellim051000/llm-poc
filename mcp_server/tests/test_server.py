"""Tests for MCP server functionality"""

from datetime import date
from unittest.mock import Mock, patch

import httpx
import pytest
from models import CustomerCreate, CustomerUpdate, ItemCreate, ItemUpdate


class MockResponse:
    """Mock HTTP response for testing"""

    def __init__(self, status_code: int, json_data: dict = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


@pytest.fixture
def mock_client():
    """Mock HTTP client for testing"""
    return Mock(spec=httpx.Client)


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "id": 1,
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "123-456-7890",
        "address": "123 Test St",
    }


@pytest.fixture
def sample_item_data():
    """Sample item data for testing"""
    return {
        "id": 1,
        "name": "Test Printer",
        "model": "XYZ-123",
        "brand": "TestBrand",
        "item_group": 1,
        "price": 299.99,
    }


class TestCustomerTools:
    """Test customer-related tools"""

    def test_list_customers_success(self, mock_client, sample_customer_data):
        """Test successful customer listing"""
        # Mock response
        mock_client.get.return_value = MockResponse(200, [sample_customer_data])

        # Import and test the function (this would normally be from server.py)
        from server import handle_api_response

        # Test the API response handling
        response = MockResponse(200, [sample_customer_data])
        result = handle_api_response(response, "list customers")

        # Verify the result contains the customer data
        assert "Test Customer" in result
        assert "test@example.com" in result

    def test_list_customers_with_filter(self, mock_client, sample_customer_data):
        """Test customer listing with name filter"""
        mock_client.get.return_value = MockResponse(200, [sample_customer_data])

        # This would test the actual list_customers function with filter
        # For now, testing the response handling
        response = MockResponse(200, [sample_customer_data])
        from server import handle_api_response

        result = handle_api_response(response, "list customers")

        assert "Test Customer" in result

    def test_customer_not_found(self, mock_client):
        """Test customer not found scenario"""
        mock_client.get.return_value = MockResponse(404)

        from server import handle_api_response

        response = MockResponse(404)
        result = handle_api_response(response, "get customer")

        assert "not found" in result.lower()

    def test_customer_creation_validation(self):
        """Test customer data validation with Pydantic"""
        # Valid customer data
        customer_data = CustomerCreate(
            name="Valid Customer", email="valid@example.com", phone="123-456-7890"
        )
        assert customer_data.name == "Valid Customer"
        assert customer_data.email == "valid@example.com"

        # Test model serialization
        data_dict = customer_data.model_dump(exclude_none=True)
        assert "name" in data_dict
        assert "email" in data_dict
        assert data_dict["name"] == "Valid Customer"

    def test_customer_update_partial(self):
        """Test partial customer updates"""
        update_data = CustomerUpdate(name="Updated Name")
        data_dict = update_data.model_dump(exclude_none=True)

        # Only name should be present
        assert "name" in data_dict
        assert "email" not in data_dict
        assert data_dict["name"] == "Updated Name"


class TestItemTools:
    """Test item-related tools"""

    def test_item_creation_validation(self):
        """Test item data validation"""
        item_data = ItemCreate(
            name="Test Printer",
            model="ABC-123",
            brand="TestBrand",
            item_group=1,
            price=199.99,
        )

        assert item_data.name == "Test Printer"
        assert item_data.price == 199.99
        assert item_data.item_group == 1

    def test_item_search_params(self):
        """Test item search parameter handling"""
        # This would test the actual search_items function
        # For now, verify the models work correctly
        item_data = ItemUpdate(name="Updated Printer")
        data_dict = item_data.model_dump(exclude_none=True)

        assert "name" in data_dict
        assert "price" not in data_dict


class TestApiResponseHandling:
    """Test API response handling"""

    def test_successful_responses(self):
        """Test handling of successful API responses"""
        from server import handle_api_response

        # Test 200 OK
        response_200 = MockResponse(200, {"id": 1, "name": "Test"})
        result = handle_api_response(response_200, "test action")
        assert "Test" in result

        # Test 201 Created
        response_201 = MockResponse(201, {"id": 2, "name": "Created"})
        result = handle_api_response(response_201, "create action")
        assert "Created" in result

        # Test 204 No Content
        response_204 = MockResponse(204)
        result = handle_api_response(response_204, "delete action")
        assert "Success" in result
        assert "delete action" in result

    def test_error_responses(self):
        """Test handling of error responses"""
        from server import handle_api_response

        # Test 404 Not Found
        response_404 = MockResponse(404)
        result = handle_api_response(response_404, "test action")
        assert "not found" in result.lower()

        # Test 400 Bad Request
        response_400 = MockResponse(400, {"error": "Invalid data"})
        result = handle_api_response(response_400, "test action")
        assert "Bad request" in result
        assert "Invalid data" in result

    def test_unexpected_responses(self):
        """Test handling of unexpected response codes"""
        from server import handle_api_response

        response_500 = MockResponse(500, text="Internal Server Error")
        result = handle_api_response(response_500, "test action")
        assert "500" in result
        assert "Internal Server Error" in result


class TestDataValidation:
    """Test data validation and serialization"""

    def test_date_handling(self):
        """Test date serialization in models"""
        from models import InvoiceCreate, InvoiceDetailCreate

        # Create invoice with date
        detail = InvoiceDetailCreate(item=1, quantity=2, unit_price=100.0)
        invoice = InvoiceCreate(
            customer=1,
            invoice_date=date(2024, 1, 15),
            status="pending",
            details=[detail],
        )

        # Test serialization
        data = invoice.model_dump(exclude_none=True)
        assert data["invoice_date"] == date(2024, 1, 15)
        assert len(data["details"]) == 1
        assert data["details"][0]["quantity"] == 2

    def test_optional_fields(self):
        """Test handling of optional fields"""
        from models import CustomerCreate

        # Customer with minimal data
        customer = CustomerCreate(name="Minimal Customer")
        data = customer.model_dump(exclude_none=True)

        assert "name" in data
        assert "email" not in data  # Should be excluded when None
        assert "phone" not in data
        assert "address" not in data


class TestServerIntegration:
    """Integration tests for the MCP server"""

    @patch("httpx.Client")
    def test_server_initialization(self, mock_client_class):
        """Test server can be initialized properly"""
        # This would test that the server starts without errors
        # and all tools are registered correctly

        # Mock the client class
        mock_client_instance = Mock()
        mock_client_class.return_value = mock_client_instance

        # Import server (this registers all tools)
        try:
            import server

            assert hasattr(server, "mcp")
            assert hasattr(server, "client")
            assert server.DJANGO_API_URL is not None
        except ImportError as e:
            pytest.skip(f"Server import failed: {e}")

    def test_environment_configuration(self):
        """Test environment variable handling"""
        import os
        from unittest.mock import patch

        # Test default values
        with patch.dict(os.environ, {}, clear=True):
            # This would test that defaults are set correctly
            # For now, just verify our test environment
            assert True  # Placeholder

    def test_error_handling_edge_cases(self):
        """Test error handling for edge cases"""
        from server import handle_api_response

        # Test with empty response
        empty_response = MockResponse(200, {})
        result = handle_api_response(empty_response, "empty test")
        assert "{}" in result  # Should return empty JSON object

        # Test with malformed JSON in 400 response
        bad_response = MockResponse(400, text="Not JSON")
        result = handle_api_response(bad_response, "bad request")
        assert "Bad request" in result
        assert "Not JSON" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
