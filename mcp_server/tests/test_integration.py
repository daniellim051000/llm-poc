"""Integration tests for MCP server"""

import os
from datetime import date
from unittest.mock import Mock, patch

import pytest


# Test data fixtures
@pytest.fixture
def sample_customer():
    return {
        "id": 1,
        "name": "Acme Corporation",
        "email": "contact@acme.com",
        "phone": "555-0123",
        "address": "123 Business St",
        "created_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def sample_invoice():
    return {
        "id": 1,
        "invoice_number": "INV-001",
        "customer": 1,
        "customer_name": "Acme Corporation",
        "invoice_date": "2024-01-15",
        "total_amount": 299.99,
        "status": "paid",
        "details": [
            {
                "id": 1,
                "item": 1,
                "item_name": "Laser Printer",
                "quantity": 1,
                "unit_price": 299.99,
                "total_price": 299.99,
            }
        ],
    }


class TestMCPServerIntegration:
    """Integration tests for the complete MCP server"""

    @patch.dict(
        os.environ, {"DJANGO_API_URL": "http://localhost:8000", "LOG_LEVEL": "INFO"}
    )
    def test_server_configuration(self):
        """Test server configuration from environment"""
        # Clear any existing imports
        import sys

        if "server" in sys.modules:
            del sys.modules["server"]

        # Import with mocked environment
        import server

        assert server.DJANGO_API_URL == "http://localhost:8000"
        assert server.LOG_LEVEL == "INFO"
        assert server.MCP_SERVER_NAME == "ricoh-mcp"

    def test_api_response_handler_comprehensive(self):
        """Test API response handler with various scenarios"""
        from server import handle_api_response

        class MockResponse:
            def __init__(self, status_code, json_data=None, text=""):
                self.status_code = status_code
                self._json_data = json_data or {}
                self.text = text

            def json(self):
                if self.status_code == 400 and not self._json_data:
                    raise ValueError("No JSON data")
                return self._json_data

        # Test success scenarios
        response_200 = MockResponse(200, {"message": "success", "data": []})
        result = handle_api_response(response_200, "test operation")
        assert "success" in result
        assert "data" in result

        response_201 = MockResponse(201, {"id": 1, "created": True})
        result = handle_api_response(response_201, "create operation")
        assert "created" in result.lower()

        response_204 = MockResponse(204)
        result = handle_api_response(response_204, "delete operation")
        assert "Success" in result
        assert "delete operation" in result

        # Test error scenarios
        response_404 = MockResponse(404)
        result = handle_api_response(response_404, "get operation")
        assert "not found" in result.lower()

        response_400_json = MockResponse(400, {"field": ["This field is required."]})
        result = handle_api_response(response_400_json, "validation")
        assert "Bad request" in result
        assert "required" in result

        response_400_text = MockResponse(400, text="Invalid input")
        result = handle_api_response(response_400_text, "validation")
        assert "Bad request" in result
        assert "Invalid input" in result

        response_500 = MockResponse(500, text="Internal Server Error")
        result = handle_api_response(response_500, "server error")
        assert "500" in result
        assert "Internal Server Error" in result


class TestDataFlowIntegration:
    """Test complete data flow from models to API calls"""

    def test_customer_workflow(self, sample_customer):
        """Test complete customer CRUD workflow"""
        from models import CustomerCreate, CustomerUpdate

        # Test creation flow
        create_data = CustomerCreate(
            name="New Customer", email="new@example.com", phone="555-9999"
        )

        create_dict = create_data.model_dump(exclude_none=True)
        assert create_dict["name"] == "New Customer"
        assert create_dict["email"] == "new@example.com"
        assert "address" not in create_dict  # Should be excluded when None

        # Test update flow
        update_data = CustomerUpdate(phone="555-1111")
        update_dict = update_data.model_dump(exclude_none=True)
        assert update_dict == {"phone": "555-1111"}  # Only updated field

    def test_invoice_workflow(self, sample_invoice):
        """Test complete invoice workflow with calculations"""
        from models import InvoiceCreate, InvoiceDetailCreate

        # Create invoice with multiple line items
        details = [
            InvoiceDetailCreate(item=1, quantity=2, unit_price=150.00),
            InvoiceDetailCreate(item=2, quantity=1, unit_price=75.00),
        ]

        invoice_data = InvoiceCreate(
            customer=1,
            invoice_date=date(2024, 1, 15),
            status="pending",
            details=details,
        )

        invoice_dict = invoice_data.model_dump(exclude_none=True)

        # Verify structure
        assert invoice_dict["customer"] == 1
        assert invoice_dict["invoice_date"] == date(2024, 1, 15)
        assert len(invoice_dict["details"]) == 2

        # Simulate total calculation (as would be done in the server)
        total = sum(
            detail.quantity * detail.unit_price for detail in invoice_data.details
        )
        assert total == 375.00  # (2*150) + (1*75)

    def test_date_serialization_workflow(self):
        """Test date handling throughout the system"""
        from models import ContractCreate

        # Test contract with dates
        contract = ContractCreate(
            customer=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            contract_type="Maintenance",
            status="active",
        )

        contract_dict = contract.model_dump(exclude_none=True)

        # Simulate date string conversion for API
        api_data = contract_dict.copy()
        api_data["start_date"] = str(api_data["start_date"])
        api_data["end_date"] = str(api_data["end_date"])

        assert api_data["start_date"] == "2024-01-01"
        assert api_data["end_date"] == "2024-12-31"


class TestErrorHandlingIntegration:
    """Test error handling across the system"""

    @patch("httpx.Client.get")
    def test_network_error_handling(self, mock_get):
        """Test handling of network errors"""
        import httpx
        from server import handle_api_response

        # Simulate network timeout
        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        # This would be tested in actual tool functions
        # For now, verify our error response structure
        class MockResponse:
            status_code = 408
            text = "Request timeout"

        result = handle_api_response(MockResponse(), "timeout test")
        assert "408" in result
        assert "timeout" in result.lower()

    def test_invalid_model_data(self):
        """Test validation of invalid model data"""
        import pytest
        from models import CustomerCreate
        from pydantic import ValidationError

        # Test missing required field
        with pytest.raises(ValidationError):
            CustomerCreate()  # Missing required 'name' field

        # Test valid minimal data
        customer = CustomerCreate(name="Valid Customer")
        assert customer.name == "Valid Customer"
        assert customer.email is None


class TestToolRegistration:
    """Test that all tools are properly registered"""

    def test_all_tool_modules_importable(self):
        """Test that all tool modules can be imported"""
        try:
            import contract_tools
            import invoice_tools
            import models
            import serial_tools
            import server
            import service_tools
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")

    @patch("httpx.Client")
    def test_tool_registration_process(self, mock_client_class):
        """Test the tool registration process"""
        from fastmcp import FastMCP

        # Create a test MCP instance
        test_mcp = FastMCP("test")
        mock_client = Mock()

        def mock_handle_response(response, action):
            return f"Mock response for {action}"

        # Test that tool registration functions work
        try:
            from contract_tools import add_contract_tools
            from invoice_tools import add_invoice_tools
            from serial_tools import add_serial_tools
            from service_tools import add_service_tools

            # These should not raise exceptions
            add_invoice_tools(
                test_mcp, mock_client, "http://test", mock_handle_response
            )
            add_contract_tools(
                test_mcp, mock_client, "http://test", mock_handle_response
            )
            add_serial_tools(test_mcp, mock_client, "http://test", mock_handle_response)
            add_service_tools(
                test_mcp, mock_client, "http://test", mock_handle_response
            )

        except Exception as e:
            pytest.fail(f"Tool registration failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
