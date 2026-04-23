"""Serial-related MCP tools"""

from typing import Optional

import httpx
from models import SerialCreate, SerialUpdate


def add_serial_tools(
    mcp, client: httpx.Client, django_api_url: str, handle_api_response
):
    """Add serial-related tools to the MCP server"""

    @mcp.tool()
    def list_serials(item_id_filter: Optional[int] = None) -> str:
        """List all serial numbers with optional item ID filtering"""
        try:
            url = f"{django_api_url}/api/serials/"
            params = {}
            if item_id_filter:
                params["item_id"] = item_id_filter

            response = client.get(url, params=params)
            return handle_api_response(response, "list serials")
        except Exception as e:
            return f"Error: Failed to list serials - {str(e)}"

    @mcp.tool()
    def get_serial(serial_id: int) -> str:
        """Get serial details by ID"""
        try:
            url = f"{django_api_url}/api/serials/{serial_id}/"
            response = client.get(url)
            return handle_api_response(response, "get serial")
        except Exception as e:
            return f"Error: Failed to get serial - {str(e)}"

    @mcp.tool()
    def create_serial(serial_data: SerialCreate) -> str:
        """Create a new serial number"""
        try:
            data = serial_data.model_dump(exclude_none=True)
            # Handle date serialization
            if "manufactured_date" in data:
                data["manufactured_date"] = str(data["manufactured_date"])
            if "warranty_end_date" in data:
                data["warranty_end_date"] = str(data["warranty_end_date"])

            url = f"{django_api_url}/api/serials/"
            response = client.post(url, json=data)
            return handle_api_response(response, "create serial")
        except Exception as e:
            return f"Error: Failed to create serial - {str(e)}"

    @mcp.tool()
    def update_serial(serial_id: int, serial_data: SerialUpdate) -> str:
        """Update an existing serial"""
        try:
            data = serial_data.model_dump(exclude_none=True)
            # Handle date serialization
            if "manufactured_date" in data:
                data["manufactured_date"] = str(data["manufactured_date"])
            if "warranty_end_date" in data:
                data["warranty_end_date"] = str(data["warranty_end_date"])

            url = f"{django_api_url}/api/serials/{serial_id}/"
            response = client.patch(url, json=data)
            return handle_api_response(response, "update serial")
        except Exception as e:
            return f"Error: Failed to update serial - {str(e)}"

    @mcp.tool()
    def delete_serial(serial_id: int) -> str:
        """Delete a serial"""
        try:
            url = f"{django_api_url}/api/serials/{serial_id}/"
            response = client.delete(url)
            return handle_api_response(response, "delete serial")
        except Exception as e:
            return f"Error: Failed to delete serial - {str(e)}"

    @mcp.tool()
    def lookup_serials_by_item(item_id: int) -> str:
        """Get all serial numbers for a specific item"""
        try:
            url = f"{django_api_url}/api/serials/by_item/?item_id={item_id}"
            response = client.get(url)
            return handle_api_response(response, "lookup serials by item")
        except Exception as e:
            return f"Error: Failed to lookup serials by item - {str(e)}"
