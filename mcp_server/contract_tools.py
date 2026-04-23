"""Contract-related MCP tools"""

from typing import Optional

import httpx
from models import ContractCreate, ContractUpdate


def add_contract_tools(
    mcp, client: httpx.Client, django_api_url: str, handle_api_response
):
    """Add contract-related tools to the MCP server"""

    @mcp.tool()
    def list_contracts(status_filter: Optional[str] = None) -> str:
        """List all contracts with optional status filtering"""
        try:
            if status_filter == "active":
                url = f"{django_api_url}/api/contracts/active/"
            else:
                url = f"{django_api_url}/api/contracts/"

            response = client.get(url)
            return handle_api_response(response, "list contracts")
        except Exception as e:
            return f"Error: Failed to list contracts - {str(e)}"

    @mcp.tool()
    def get_contract(contract_id: int) -> str:
        """Get contract details by ID"""
        try:
            url = f"{django_api_url}/api/contracts/{contract_id}/"
            response = client.get(url)
            return handle_api_response(response, "get contract")
        except Exception as e:
            return f"Error: Failed to get contract - {str(e)}"

    @mcp.tool()
    def create_contract(contract_data: ContractCreate) -> str:
        """Create a new contract"""
        try:
            data = contract_data.model_dump(exclude_none=True)
            # Handle date serialization
            if "start_date" in data:
                data["start_date"] = str(data["start_date"])
            if "end_date" in data:
                data["end_date"] = str(data["end_date"])

            url = f"{django_api_url}/api/contracts/"
            response = client.post(url, json=data)
            return handle_api_response(response, "create contract")
        except Exception as e:
            return f"Error: Failed to create contract - {str(e)}"

    @mcp.tool()
    def update_contract(contract_id: int, contract_data: ContractUpdate) -> str:
        """Update an existing contract"""
        try:
            data = contract_data.model_dump(exclude_none=True)
            # Handle date serialization
            if "start_date" in data:
                data["start_date"] = str(data["start_date"])
            if "end_date" in data:
                data["end_date"] = str(data["end_date"])

            url = f"{django_api_url}/api/contracts/{contract_id}/"
            response = client.patch(url, json=data)
            return handle_api_response(response, "update contract")
        except Exception as e:
            return f"Error: Failed to update contract - {str(e)}"

    @mcp.tool()
    def delete_contract(contract_id: int) -> str:
        """Delete a contract"""
        try:
            url = f"{django_api_url}/api/contracts/{contract_id}/"
            response = client.delete(url)
            return handle_api_response(response, "delete contract")
        except Exception as e:
            return f"Error: Failed to delete contract - {str(e)}"

    @mcp.tool()
    def get_active_contracts() -> str:
        """Get all active contracts"""
        try:
            url = f"{django_api_url}/api/contracts/active/"
            response = client.get(url)
            return handle_api_response(response, "get active contracts")
        except Exception as e:
            return f"Error: Failed to get active contracts - {str(e)}"
