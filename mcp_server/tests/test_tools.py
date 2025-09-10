"""Tests for individual tool modules"""

import json
from unittest.mock import Mock

import httpx
import pytest
from models import (
    ContactDetailCreate,
    ContractCreate,
    InvoiceCreate,
    InvoiceDetailCreate,
    SerialCreate,
    ServiceCreate,
    ServiceDetailCreate,
)


class MockResponse:
    """Mock HTTP response for testing"""

    def __init__(self, status_code: int, json_data: dict = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self):
        return self._json_data


@pytest.fixture
def mock_mcp():
    """Mock MCP server for testing"""
    mcp = Mock()
    mcp.tool = Mock(
        return_value=lambda func: func
    )  # Decorator that returns the function unchanged
    return mcp


@pytest.fixture
def mock_client():
    """Mock HTTP client for testing"""
    return Mock(spec=httpx.Client)


@pytest.fixture
def handle_api_response():
    """Mock API response handler"""

    def handler(response: httpx.Response, action: str) -> str:
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        elif response.status_code == 404:
            return "Error: Resource not found"
        else:
            return f"Error: API request failed with status {response.status_code}"

    return handler


class TestInvoiceTools:
    """Test invoice tool functions"""

    def test_invoice_tools_registration(
        self, mock_mcp, mock_client, handle_api_response
    ):
        """Test that invoice tools can be registered"""
        from invoice_tools import add_invoice_tools

        # Should not raise an exception
        add_invoice_tools(
            mock_mcp, mock_client, "http://localhost:8000", handle_api_response
        )

        # Verify tool decorator was called
        assert mock_mcp.tool.called

    def test_invoice_model_validation(self):
        """Test invoice model validation"""
        detail = InvoiceDetailCreate(item=1, quantity=2, unit_price=150.00)

        invoice = InvoiceCreate(
            customer=1, invoice_date="2024-01-15", status="pending", details=[detail]
        )

        # Test serialization
        data = invoice.model_dump(exclude_none=True)
        assert data["customer"] == 1
        assert data["invoice_date"] == "2024-01-15"
        assert len(data["details"]) == 1
        assert data["details"][0]["unit_price"] == 150.00


class TestContractTools:
    """Test contract tool functions"""

    def test_contract_tools_registration(
        self, mock_mcp, mock_client, handle_api_response
    ):
        """Test that contract tools can be registered"""
        from contract_tools import add_contract_tools

        # Should not raise an exception
        add_contract_tools(
            mock_mcp, mock_client, "http://localhost:8000", handle_api_response
        )

        # Verify tool decorator was called
        assert mock_mcp.tool.called

    def test_contract_model_validation(self):
        """Test contract model validation"""
        contact = ContactDetailCreate(
            contact_person="John Doe", role="Manager", email="john@example.com"
        )

        contract = ContractCreate(
            customer=1,
            start_date="2024-01-01",
            end_date="2024-12-31",
            contract_type="SLA",
            status="active",
            terms="Standard terms",
            contact_details=[contact],
        )

        data = contract.model_dump(exclude_none=True)
        assert data["customer"] == 1
        assert data["contract_type"] == "SLA"
        assert len(data["contact_details"]) == 1
        assert data["contact_details"][0]["contact_person"] == "John Doe"


class TestSerialTools:
    """Test serial tool functions"""

    def test_serial_tools_registration(
        self, mock_mcp, mock_client, handle_api_response
    ):
        """Test that serial tools can be registered"""
        from serial_tools import add_serial_tools

        # Should not raise an exception
        add_serial_tools(
            mock_mcp, mock_client, "http://localhost:8000", handle_api_response
        )

        # Verify tool decorator was called
        assert mock_mcp.tool.called

    def test_serial_model_validation(self):
        """Test serial model validation"""
        serial = SerialCreate(
            serial_number="SN123456789",
            item=1,
            status="active",
            manufactured_date="2024-01-01",
            warranty_end_date="2026-01-01",
        )

        data = serial.model_dump(exclude_none=True)
        assert data["serial_number"] == "SN123456789"
        assert data["item"] == 1
        assert data["status"] == "active"


class TestServiceTools:
    """Test service tool functions"""

    def test_service_tools_registration(
        self, mock_mcp, mock_client, handle_api_response
    ):
        """Test that service tools can be registered"""
        from service_tools import add_service_tools

        # Should not raise an exception
        add_service_tools(
            mock_mcp, mock_client, "http://localhost:8000", handle_api_response
        )

        # Verify tool decorator was called
        assert mock_mcp.tool.called

    def test_service_model_validation(self):
        """Test service model validation"""
        detail = ServiceDetailCreate(
            serial=1,
            description="Routine maintenance",
            parts_used="Filter, Oil",
            labor_hours=2.5,
            cost=125.00,
        )

        service = ServiceCreate(
            service_name="Printer Maintenance",
            customer=1,
            service_date="2024-01-15",
            technician="Tech Smith",
            status="completed",
            notes="Service completed successfully",
            details=[detail],
        )

        data = service.model_dump(exclude_none=True)
        assert data["service_name"] == "Printer Maintenance"
        assert data["customer"] == 1
        assert data["technician"] == "Tech Smith"
        assert len(data["details"]) == 1
        assert data["details"][0]["labor_hours"] == 2.5


class TestModelIntegration:
    """Test model integration and edge cases"""

    def test_optional_field_handling(self):
        """Test that optional fields are handled correctly"""
        from models import CustomerUpdate, ItemUpdate

        # Customer update with only name
        customer_update = CustomerUpdate(name="Updated Name")
        data = customer_update.model_dump(exclude_none=True)

        assert "name" in data
        assert "email" not in data
        assert "phone" not in data

        # Item update with only price
        item_update = ItemUpdate(price=299.99)
        data = item_update.model_dump(exclude_none=True)

        assert "price" in data
        assert "name" not in data
        assert "brand" not in data

    def test_date_string_conversion(self):
        """Test date handling in models"""
        from datetime import date

        from models import ContractUpdate

        # Create update with date
        contract_update = ContractUpdate(start_date=date(2024, 1, 1))
        data = contract_update.model_dump(exclude_none=True)

        # Date should be present
        assert "start_date" in data
        assert data["start_date"] == date(2024, 1, 1)

    def test_nested_model_validation(self):
        """Test validation of nested models"""
        from models import InvoiceCreate, InvoiceDetailCreate

        # Create invoice with invalid detail (negative quantity)
        detail = InvoiceDetailCreate(
            item=1,
            quantity=-1,  # This should still pass validation since we don't have custom validators
            unit_price=100.0,
        )

        invoice = InvoiceCreate(customer=1, invoice_date="2024-01-15", details=[detail])

        # Should still create the model (Pydantic doesn't validate business logic by default)
        assert invoice.details[0].quantity == -1

        # Test multiple details
        detail2 = InvoiceDetailCreate(item=2, quantity=3, unit_price=50.0)
        invoice_multi = InvoiceCreate(
            customer=1, invoice_date="2024-01-15", details=[detail, detail2]
        )

        assert len(invoice_multi.details) == 2
        assert invoice_multi.details[1].unit_price == 50.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
