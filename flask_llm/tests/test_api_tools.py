from unittest.mock import Mock, patch

import pytest
import requests
from api_tools import (
    ActiveContractsTool,
    CustomerInvoicesTool,
    CustomerSearchTool,
    InvoiceSearchTool,
    ItemSearchTool,
    SerialLookupTool,
    ServiceHistoryTool,
    WebSearchTool,
)


class TestCustomerSearchTool:
    def setup_method(self):
        self.tool = CustomerSearchTool()

    @patch("api_tools.requests.get")
    def test_customer_search_all(self, mock_get):
        """Test searching for all customers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Company A", "email": "a@company.com"},
            {"id": 2, "name": "Company B", "email": "b@company.com"},
        ]
        mock_get.return_value = mock_response

        result = self.tool._run()

        assert "Company A" in result
        assert "Company B" in result
        mock_get.assert_called_once()

    @patch("api_tools.requests.get")
    def test_customer_search_filtered(self, mock_get):
        """Test searching for customers with filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Company A", "email": "a@company.com"},
            {"id": 2, "name": "Another Company", "email": "b@company.com"},
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(customer_name="Company A")

        assert "Company A" in result
        assert "Another Company" not in result

    @patch("api_tools.requests.get")
    def test_customer_search_api_error(self, mock_get):
        """Test handling API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = self.tool._run()
        assert "Error: 500" in result

    @patch("api_tools.requests.get")
    def test_customer_search_connection_error(self, mock_get):
        """Test handling connection errors."""
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        result = self.tool._run()
        assert "Error connecting to API" in result


class TestCustomerInvoicesTool:
    def setup_method(self):
        self.tool = CustomerInvoicesTool()

    @patch("api_tools.requests.get")
    def test_customer_invoices_success(self, mock_get):
        """Test successful invoice retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"invoice_number": "INV-001", "total_amount": "1000.00"}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(customer_id=1)

        assert "INV-001" in result
        mock_get.assert_called_once()

    @patch("api_tools.requests.get")
    def test_customer_invoices_not_found(self, mock_get):
        """Test customer invoices not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.tool._run(customer_id=999)
        assert "Error: 404" in result


class TestItemSearchTool:
    def setup_method(self):
        self.tool = ItemSearchTool()

    @patch("api_tools.requests.get")
    def test_item_search_by_query(self, mock_get):
        """Test item search by query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Color Printer", "brand": "Ricoh", "model": "P3000"}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(query="printer")

        assert "Color Printer" in result
        mock_get.assert_called_once()
        # Check that query parameter was passed
        call_args = mock_get.call_args
        assert call_args[1]["params"]["q"] == "printer"

    @patch("api_tools.requests.get")
    def test_item_search_by_brand(self, mock_get):
        """Test item search by brand."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Color Printer", "brand": "Ricoh", "model": "P3000"}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(brand="Ricoh")

        assert "Ricoh" in result
        call_args = mock_get.call_args
        assert call_args[1]["params"]["brand"] == "Ricoh"

    @patch("api_tools.requests.get")
    def test_item_search_both_params(self, mock_get):
        """Test item search with both query and brand."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        self.tool._run(query="printer", brand="Canon")

        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["q"] == "printer"
        assert params["brand"] == "Canon"


class TestInvoiceSearchTool:
    def setup_method(self):
        self.tool = InvoiceSearchTool()

    @patch("api_tools.requests.get")
    def test_invoice_search_all(self, mock_get):
        """Test searching all invoices."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"invoice_number": "INV-001", "customer": {"name": "Company A"}}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run()

        assert "INV-001" in result
        # Should call the general invoices endpoint
        mock_get.assert_called_once()
        assert "by_customer" not in mock_get.call_args[0][0]

    @patch("api_tools.requests.get")
    def test_invoice_search_by_customer(self, mock_get):
        """Test searching invoices by customer."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"invoice_number": "INV-001", "customer": {"name": "Company A"}}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(customer_name="Company A")

        assert "INV-001" in result
        # Should call the by_customer endpoint
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        assert "by_customer" in called_url
        assert "Company A" in called_url


class TestActiveContractsTool:
    def setup_method(self):
        self.tool = ActiveContractsTool()

    @patch("api_tools.requests.get")
    def test_active_contracts_success(self, mock_get):
        """Test successful active contracts retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "contract_number": "CON-001",
                "status": "active",
                "customer": {"name": "Company A"},
            }
        ]
        mock_get.return_value = mock_response

        result = self.tool._run()

        assert "CON-001" in result
        assert "active" in result
        mock_get.assert_called_once()


class TestSerialLookupTool:
    def setup_method(self):
        self.tool = SerialLookupTool()

    @patch("api_tools.requests.get")
    def test_serial_lookup_all(self, mock_get):
        """Test looking up all serials."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"serial_number": "SN123456789", "item": {"name": "Printer"}}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run()

        assert "SN123456789" in result
        mock_get.assert_called_once()
        # Should not have item_id parameter
        call_args = mock_get.call_args
        assert call_args[1]["params"] == {}

    @patch("api_tools.requests.get")
    def test_serial_lookup_by_item(self, mock_get):
        """Test looking up serials by item ID."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"serial_number": "SN123456789", "item": {"name": "Printer"}}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(item_id=1)

        assert "SN123456789" in result
        call_args = mock_get.call_args
        assert call_args[1]["params"]["item_id"] == 1


class TestServiceHistoryTool:
    def setup_method(self):
        self.tool = ServiceHistoryTool()

    @patch("api_tools.requests.get")
    def test_service_history_all(self, mock_get):
        """Test getting all service history."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"service_name": "Maintenance", "customer": {"name": "Company A"}}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run()

        assert "Maintenance" in result
        mock_get.assert_called_once()
        # Should not use date_range endpoint
        assert "by_date_range" not in mock_get.call_args[0][0]

    @patch("api_tools.requests.get")
    def test_service_history_date_range(self, mock_get):
        """Test getting service history with date range."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"service_name": "Maintenance", "service_date": "2024-01-15"}
        ]
        mock_get.return_value = mock_response

        result = self.tool._run(start_date="2024-01-01", end_date="2024-01-31")

        assert "Maintenance" in result
        mock_get.assert_called_once()
        # Should use date_range endpoint
        assert "by_date_range" in mock_get.call_args[0][0]
        call_args = mock_get.call_args
        params = call_args[1]["params"]
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-01-31"


class TestWebSearchTool:
    def setup_method(self):
        self.tool = WebSearchTool()

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_search_success(self, mock_firecrawl_app):
        """Test successful web search."""
        mock_firecrawl = Mock()
        mock_firecrawl_app.return_value = mock_firecrawl

        # Mock search response with new format
        mock_result = Mock()
        mock_result.web = [
            Mock(
                title="Test Result",
                url="https://example.com",
                description="Test description",
            )
        ]
        mock_firecrawl.search.return_value = mock_result

        result = self.tool._run(query="test query", search_type="search")

        assert "Test Result" in result
        assert "https://example.com" in result
        mock_firecrawl.search.assert_called_once_with(query="test query", limit=5)

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_search_old_format(self, mock_firecrawl_app):
        """Test web search with old response format."""
        mock_firecrawl = Mock()
        mock_firecrawl_app.return_value = mock_firecrawl

        # Mock search response with old format
        mock_firecrawl.search.return_value = {
            "success": True,
            "data": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "description": "Test description",
                }
            ],
        }

        result = self.tool._run(query="test query")

        assert "Test Result" in result
        assert "https://example.com" in result

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_scrape_success(self, mock_firecrawl_app):
        """Test successful web scraping."""
        mock_firecrawl = Mock()
        mock_firecrawl_app.return_value = mock_firecrawl

        # Mock scrape response with new format
        mock_result = Mock()
        mock_result.markdown = "# Test Page Content\nThis is test content"
        mock_firecrawl.scrape.return_value = mock_result

        result = self.tool._run(query="https://example.com", search_type="scrape")

        assert "Test Page Content" in result
        mock_firecrawl.scrape.assert_called_once()

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_scrape_old_format(self, mock_firecrawl_app):
        """Test web scraping with old response format."""
        mock_firecrawl = Mock()
        mock_firecrawl_app.return_value = mock_firecrawl

        # Mock scrape response with old format
        mock_firecrawl.scrape.return_value = {
            "success": True,
            "data": {"markdown": "# Test Page Content\nThis is test content"},
        }

        result = self.tool._run(query="https://example.com", search_type="scrape")

        assert "Test Page Content" in result

    def test_web_search_no_api_key(self):
        """Test web search without API key."""
        with patch("api_tools.settings.FIRECRAWL_API_KEY", None):
            result = self.tool._run(query="test query")
            assert "Firecrawl API key not configured" in result

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_scrape_invalid_url(self, mock_firecrawl_app):
        """Test scraping with invalid URL."""
        result = self.tool._run(query="not a url", search_type="scrape")
        assert "no valid URL found" in result

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_search_exception(self, mock_firecrawl_app):
        """Test web search with exception."""
        mock_firecrawl = Mock()
        mock_firecrawl_app.return_value = mock_firecrawl
        mock_firecrawl.search.side_effect = Exception("API error")

        result = self.tool._run(query="test query")

        assert "Error searching for test query: API error" in result

    @patch("api_tools.settings.FIRECRAWL_API_KEY", "test_api_key")
    @patch("api_tools.FirecrawlApp")
    def test_web_search_url_detection(self, mock_firecrawl_app):
        """Test URL detection for auto-switching to scrape mode."""
        mock_firecrawl = Mock()
        mock_firecrawl_app.return_value = mock_firecrawl

        mock_result = Mock()
        mock_result.markdown = "Page content"
        mock_firecrawl.scrape.return_value = mock_result

        # Mock search response
        mock_search_result = Mock()
        mock_search_result.web = []
        mock_firecrawl.search.return_value = mock_search_result

        # Should auto-detect URL but still do search since search_type is "search"
        result = self.tool._run(query="https://example.com", search_type="search")

        # With search_type="search", it should use search even if query looks like URL
        mock_firecrawl.search.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
