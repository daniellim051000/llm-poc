#!/usr/bin/env python3
"""
MCP Server for Django Business API
Provides AI assistants with tools to interact with business data

This server exposes 38+ tools for full CRUD operations on:
- Customers (8 tools)
- Items (6 tools)
- Invoices (6 tools)
- Contracts (6 tools)
- Serials (6 tools)
- Services (6 tools)
"""

import json
import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastmcp import FastMCP
from models import (
    CustomerCreate,
    CustomerUpdate,
    ItemCreate,
    ItemUpdate,
)

# Load environment variables
load_dotenv()

# Configuration
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://localhost:8000")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "ricoh-mcp")

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

# HTTP client for API calls
client = httpx.Client(timeout=30.0)


def handle_api_response(response: httpx.Response, action: str) -> str:
    """Handle API responses consistently"""
    if response.status_code == 200 or response.status_code == 201:
        return json.dumps(response.json(), indent=2, default=str)
    elif response.status_code == 204:
        return f"Success: {action} completed successfully"
    elif response.status_code == 404:
        return "Error: Resource not found"
    elif response.status_code == 400:
        try:
            error_data = response.json()
            return f"Error: Bad request - {json.dumps(error_data, indent=2)}"
        except:
            return f"Error: Bad request - {response.text}"
    else:
        return f"Error: API request failed with status {response.status_code} - {response.text}"


# Customer Tools
@mcp.tool()
def list_customers(name_filter: Optional[str] = None) -> str:
    """List all customers with optional name filtering"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/"
        response = client.get(url)

        if response.status_code == 200:
            customers = response.json()
            if name_filter:
                customers = [
                    c
                    for c in customers
                    if name_filter.lower() in c.get("name", "").lower()
                ]
            return json.dumps(customers, indent=2, default=str)
        return handle_api_response(response, "list customers")
    except Exception as e:
        return f"Error: Failed to list customers - {str(e)}"


@mcp.tool()
def get_customer(customer_id: int) -> str:
    """Get customer details by ID"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/{customer_id}/"
        response = client.get(url)
        return handle_api_response(response, "get customer")
    except Exception as e:
        return f"Error: Failed to get customer - {str(e)}"


@mcp.tool()
def create_customer(customer_data: CustomerCreate) -> str:
    """Create a new customer"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/"
        response = client.post(url, json=customer_data.model_dump(exclude_none=True))
        return handle_api_response(response, "create customer")
    except Exception as e:
        return f"Error: Failed to create customer - {str(e)}"


@mcp.tool()
def update_customer(customer_id: int, customer_data: CustomerUpdate) -> str:
    """Update an existing customer"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/{customer_id}/"
        response = client.patch(url, json=customer_data.model_dump(exclude_none=True))
        return handle_api_response(response, "update customer")
    except Exception as e:
        return f"Error: Failed to update customer - {str(e)}"


@mcp.tool()
def delete_customer(customer_id: int) -> str:
    """Delete a customer"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/{customer_id}/"
        response = client.delete(url)
        return handle_api_response(response, "delete customer")
    except Exception as e:
        return f"Error: Failed to delete customer - {str(e)}"


@mcp.tool()
def get_customer_invoices(customer_id: int) -> str:
    """Get all invoices for a specific customer"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/{customer_id}/invoices/"
        response = client.get(url)
        return handle_api_response(response, "get customer invoices")
    except Exception as e:
        return f"Error: Failed to get customer invoices - {str(e)}"


@mcp.tool()
def get_customer_contracts(customer_id: int) -> str:
    """Get all contracts for a specific customer"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/{customer_id}/contracts/"
        response = client.get(url)
        return handle_api_response(response, "get customer contracts")
    except Exception as e:
        return f"Error: Failed to get customer contracts - {str(e)}"


@mcp.tool()
def get_customer_services(customer_id: int) -> str:
    """Get all services for a specific customer"""
    try:
        url = f"{DJANGO_API_URL}/api/customers/{customer_id}/services/"
        response = client.get(url)
        return handle_api_response(response, "get customer services")
    except Exception as e:
        return f"Error: Failed to get customer services - {str(e)}"


# Item Tools
@mcp.tool()
def list_items(
    name_filter: Optional[str] = None, brand_filter: Optional[str] = None
) -> str:
    """List all items with optional filtering"""
    try:
        url = f"{DJANGO_API_URL}/api/items/"
        params = {}
        if name_filter or brand_filter:
            url = f"{DJANGO_API_URL}/api/items/search/"
            if name_filter:
                params["q"] = name_filter
            if brand_filter:
                params["brand"] = brand_filter

        response = client.get(url, params=params)
        return handle_api_response(response, "list items")
    except Exception as e:
        return f"Error: Failed to list items - {str(e)}"


@mcp.tool()
def get_item(item_id: int) -> str:
    """Get item details by ID"""
    try:
        url = f"{DJANGO_API_URL}/api/items/{item_id}/"
        response = client.get(url)
        return handle_api_response(response, "get item")
    except Exception as e:
        return f"Error: Failed to get item - {str(e)}"


@mcp.tool()
def create_item(item_data: ItemCreate) -> str:
    """Create a new item"""
    try:
        url = f"{DJANGO_API_URL}/api/items/"
        response = client.post(url, json=item_data.model_dump(exclude_none=True))
        return handle_api_response(response, "create item")
    except Exception as e:
        return f"Error: Failed to create item - {str(e)}"


@mcp.tool()
def update_item(item_id: int, item_data: ItemUpdate) -> str:
    """Update an existing item"""
    try:
        url = f"{DJANGO_API_URL}/api/items/{item_id}/"
        response = client.patch(url, json=item_data.model_dump(exclude_none=True))
        return handle_api_response(response, "update item")
    except Exception as e:
        return f"Error: Failed to update item - {str(e)}"


@mcp.tool()
def delete_item(item_id: int) -> str:
    """Delete an item"""
    try:
        url = f"{DJANGO_API_URL}/api/items/{item_id}/"
        response = client.delete(url)
        return handle_api_response(response, "delete item")
    except Exception as e:
        return f"Error: Failed to delete item - {str(e)}"


@mcp.tool()
def search_items(query: Optional[str] = None, brand: Optional[str] = None) -> str:
    """Search items by name, model, or brand"""
    try:
        url = f"{DJANGO_API_URL}/api/items/search/"
        params = {}
        if query:
            params["q"] = query
        if brand:
            params["brand"] = brand

        response = client.get(url, params=params)
        return handle_api_response(response, "search items")
    except Exception as e:
        return f"Error: Failed to search items - {str(e)}"


# Import and register additional tools
from contract_tools import add_contract_tools
from invoice_tools import add_invoice_tools
from serial_tools import add_serial_tools
from service_tools import add_service_tools

# Register all additional tools
add_invoice_tools(mcp, client, DJANGO_API_URL, handle_api_response)
add_contract_tools(mcp, client, DJANGO_API_URL, handle_api_response)
add_serial_tools(mcp, client, DJANGO_API_URL, handle_api_response)
add_service_tools(mcp, client, DJANGO_API_URL, handle_api_response)


if __name__ == "__main__":
    print(f"Starting MCP Server: {MCP_SERVER_NAME}")
    print(f"Django API URL: {DJANGO_API_URL}")
    print("Available tools:")
    print(
        "- Customer tools: list_customers, get_customer, create_customer, update_customer, delete_customer, get_customer_invoices, get_customer_contracts, get_customer_services"
    )
    print(
        "- Item tools: list_items, get_item, create_item, update_item, delete_item, search_items"
    )
    print(
        "- Invoice tools: list_invoices, get_invoice, create_invoice, update_invoice, delete_invoice, search_invoices_by_customer"
    )
    print(
        "- Contract tools: list_contracts, get_contract, create_contract, update_contract, delete_contract, get_active_contracts"
    )
    print(
        "- Serial tools: list_serials, get_serial, create_serial, update_serial, delete_serial, lookup_serials_by_item"
    )
    print(
        "- Service tools: list_services, get_service, create_service, update_service, delete_service, get_services_by_date"
    )
    print("\nServer ready for MCP connections...")

    # Run the MCP server
    mcp.run()
