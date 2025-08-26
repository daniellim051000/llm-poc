from typing import Optional, Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class CustomerSearchInput(BaseModel):
    customer_name: Optional[str] = Field(
        None, description="Name of the customer to search for"
    )


class ItemSearchInput(BaseModel):
    query: Optional[str] = Field(
        None, description="Search term for item name, model, or brand"
    )
    brand: Optional[str] = Field(
        None, description="Filter by specific brand (e.g., 'Ricoh')"
    )


class InvoiceSearchInput(BaseModel):
    customer_name: Optional[str] = Field(
        None, description="Filter invoices by customer name"
    )


class CustomerSearchTool(BaseTool):
    name: str = "customer_search"
    description: str = "Search for customers and get their basic information"
    args_schema: Type[BaseModel] = CustomerSearchInput

    def _run(self, customer_name: Optional[str] = None) -> str:
        url = "http://localhost:8000/api/customers/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                customers = response.json()
                if customer_name:
                    filtered = [
                        c
                        for c in customers
                        if customer_name.lower() in c["name"].lower()
                    ]
                    return str(filtered)
                return str(customers)
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class CustomerInvoicesTool(BaseTool):
    name: str = "customer_invoices"
    description: str = "Get all invoices for a specific customer by customer ID"

    def _run(self, customer_id: int) -> str:
        url = f"http://localhost:8000/api/customers/{customer_id}/invoices/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class CustomerContractsTool(BaseTool):
    name: str = "customer_contracts"
    description: str = "Get all contracts for a specific customer by customer ID"

    def _run(self, customer_id: int) -> str:
        url = f"http://localhost:8000/api/customers/{customer_id}/contracts/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class CustomerServicesTool(BaseTool):
    name: str = "customer_services"
    description: str = "Get all services for a specific customer by customer ID"

    def _run(self, customer_id: int) -> str:
        url = f"http://localhost:8000/api/customers/{customer_id}/services/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class ItemSearchTool(BaseTool):
    name: str = "item_search"
    description: str = "Search for items/products by name, model, or brand"
    args_schema: Type[BaseModel] = ItemSearchInput

    def _run(self, query: Optional[str] = None, brand: Optional[str] = None) -> str:
        url = "http://localhost:8000/api/items/search/"
        params = {}
        if query:
            params["q"] = query
        if brand:
            params["brand"] = brand

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class InvoiceSearchTool(BaseTool):
    name: str = "invoice_search"
    description: str = "Search for invoices, optionally filtered by customer name"
    args_schema: Type[BaseModel] = InvoiceSearchInput

    def _run(self, customer_name: Optional[str] = None) -> str:
        if customer_name:
            url = f"http://localhost:8000/api/invoices/by_customer/?customer_name={customer_name}"
        else:
            url = "http://localhost:8000/api/invoices/"

        try:
            response = requests.get(url)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class ActiveContractsTool(BaseTool):
    name: str = "active_contracts"
    description: str = "Get all active contracts with SLA details"

    def _run(self) -> str:
        url = "http://localhost:8000/api/contracts/active/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class SerialLookupTool(BaseTool):
    name: str = "serial_lookup"
    description: str = "Look up serial numbers and machine information"

    def _run(self, item_id: Optional[int] = None) -> str:
        url = "http://localhost:8000/api/serials/"
        params = {}
        if item_id:
            params["item_id"] = item_id

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"


class ServiceHistoryTool(BaseTool):
    name: str = "service_history"
    description: str = "Get service history and machine maintenance records"

    def _run(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> str:
        url = "http://localhost:8000/api/services/"
        if start_date or end_date:
            url += "by_date_range/"
            params = {}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
        else:
            params = {}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return str(response.json())
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error connecting to API: {str(e)}"
