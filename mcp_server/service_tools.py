"""Service-related MCP tools"""

from typing import Optional

import httpx
from models import ServiceCreate, ServiceUpdate


def add_service_tools(
    mcp, client: httpx.Client, django_api_url: str, handle_api_response
):
    """Add service-related tools to the MCP server"""

    @mcp.tool()
    def list_services(
        start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> str:
        """List all services with optional date range filtering (YYYY-MM-DD format)"""
        try:
            url = f"{django_api_url}/api/services/"
            params = {}

            if start_date or end_date:
                url = f"{django_api_url}/api/services/by_date_range/"
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date

            response = client.get(url, params=params)
            return handle_api_response(response, "list services")
        except Exception as e:
            return f"Error: Failed to list services - {str(e)}"

    @mcp.tool()
    def get_service(service_id: int) -> str:
        """Get service details by ID"""
        try:
            url = f"{django_api_url}/api/services/{service_id}/"
            response = client.get(url)
            return handle_api_response(response, "get service")
        except Exception as e:
            return f"Error: Failed to get service - {str(e)}"

    @mcp.tool()
    def create_service(service_data: ServiceCreate) -> str:
        """Create a new service record"""
        try:
            data = service_data.model_dump(exclude_none=True)
            # Handle date serialization
            if "service_date" in data:
                data["service_date"] = str(data["service_date"])

            url = f"{django_api_url}/api/services/"
            response = client.post(url, json=data)
            return handle_api_response(response, "create service")
        except Exception as e:
            return f"Error: Failed to create service - {str(e)}"

    @mcp.tool()
    def update_service(service_id: int, service_data: ServiceUpdate) -> str:
        """Update an existing service"""
        try:
            data = service_data.model_dump(exclude_none=True)
            # Handle date serialization
            if "service_date" in data:
                data["service_date"] = str(data["service_date"])

            url = f"{django_api_url}/api/services/{service_id}/"
            response = client.patch(url, json=data)
            return handle_api_response(response, "update service")
        except Exception as e:
            return f"Error: Failed to update service - {str(e)}"

    @mcp.tool()
    def delete_service(service_id: int) -> str:
        """Delete a service"""
        try:
            url = f"{django_api_url}/api/services/{service_id}/"
            response = client.delete(url)
            return handle_api_response(response, "delete service")
        except Exception as e:
            return f"Error: Failed to delete service - {str(e)}"

    @mcp.tool()
    def get_services_by_date(start_date: str, end_date: Optional[str] = None) -> str:
        """Get services within a specific date range (YYYY-MM-DD format)"""
        try:
            url = f"{django_api_url}/api/services/by_date_range/"
            params = {"start_date": start_date}
            if end_date:
                params["end_date"] = end_date

            response = client.get(url, params=params)
            return handle_api_response(response, "get services by date")
        except Exception as e:
            return f"Error: Failed to get services by date - {str(e)}"
