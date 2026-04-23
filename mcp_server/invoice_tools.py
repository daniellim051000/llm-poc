"""Invoice-related MCP tools"""

from typing import Optional

import httpx
from models import InvoiceCreate, InvoiceUpdate


def add_invoice_tools(
    mcp, client: httpx.Client, django_api_url: str, handle_api_response
):
    """Add invoice-related tools to the MCP server"""

    @mcp.tool()
    def list_invoices(customer_name_filter: Optional[str] = None) -> str:
        """List all invoices with optional customer name filtering"""
        try:
            if customer_name_filter:
                url = f"{django_api_url}/api/invoices/by_customer/?customer_name={customer_name_filter}"
            else:
                url = f"{django_api_url}/api/invoices/"

            response = client.get(url)
            return handle_api_response(response, "list invoices")
        except Exception as e:
            return f"Error: Failed to list invoices - {str(e)}"

    @mcp.tool()
    def get_invoice(invoice_id: int) -> str:
        """Get invoice details by ID with line items"""
        try:
            url = f"{django_api_url}/api/invoices/{invoice_id}/"
            response = client.get(url)
            return handle_api_response(response, "get invoice")
        except Exception as e:
            return f"Error: Failed to get invoice - {str(e)}"

    @mcp.tool()
    def create_invoice(invoice_data: InvoiceCreate) -> str:
        """Create a new invoice with line items"""
        try:
            # Convert the invoice data, handling date serialization
            data = invoice_data.model_dump(exclude_none=True)
            if "invoice_date" in data:
                data["invoice_date"] = str(data["invoice_date"])

            # Calculate total amount from details
            total_amount = 0.0
            for detail in data.get("details", []):
                detail_total = detail["quantity"] * detail["unit_price"]
                detail["total_price"] = detail_total
                total_amount += detail_total
            data["total_amount"] = total_amount

            url = f"{django_api_url}/api/invoices/"
            response = client.post(url, json=data)
            return handle_api_response(response, "create invoice")
        except Exception as e:
            return f"Error: Failed to create invoice - {str(e)}"

    @mcp.tool()
    def update_invoice(invoice_id: int, invoice_data: InvoiceUpdate) -> str:
        """Update an existing invoice"""
        try:
            data = invoice_data.model_dump(exclude_none=True)
            if "invoice_date" in data:
                data["invoice_date"] = str(data["invoice_date"])

            url = f"{django_api_url}/api/invoices/{invoice_id}/"
            response = client.patch(url, json=data)
            return handle_api_response(response, "update invoice")
        except Exception as e:
            return f"Error: Failed to update invoice - {str(e)}"

    @mcp.tool()
    def delete_invoice(invoice_id: int) -> str:
        """Delete an invoice"""
        try:
            url = f"{django_api_url}/api/invoices/{invoice_id}/"
            response = client.delete(url)
            return handle_api_response(response, "delete invoice")
        except Exception as e:
            return f"Error: Failed to delete invoice - {str(e)}"

    @mcp.tool()
    def search_invoices_by_customer(customer_name: str) -> str:
        """Search invoices by customer name"""
        try:
            url = f"{django_api_url}/api/invoices/by_customer/?customer_name={customer_name}"
            response = client.get(url)
            return handle_api_response(response, "search invoices by customer")
        except Exception as e:
            return f"Error: Failed to search invoices by customer - {str(e)}"
