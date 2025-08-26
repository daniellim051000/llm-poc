from typing import Optional, Type

import requests
from firecrawl import FirecrawlApp
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


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query or URL to scrape")
    search_type: str = Field(
        default="search",
        description="Type: 'search' for web search or 'scrape' for single URL",
    )
    max_results: Optional[int] = Field(
        default=5, description="Maximum number of search results to return"
    )


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = """Search the web or scrape specific URLs for information using Firecrawl.
    Use search_type='scrape' when user provides a specific URL to extract content from.
    Use search_type='search' (default) for general web searches and queries."""
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(
        self, query: str, search_type: str = "search", max_results: int = 5
    ) -> str:
        import os
        import re

        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            return "Error: Firecrawl API key not configured. Please set FIRECRAWL_API_KEY environment variable."

        # Debug: Check what we're receiving
        print(f"DEBUG: Received query type: {type(query)}, value: {query}")
        print(f"DEBUG: search_type: {search_type}, max_results: {max_results}")

        # Ensure query is a string
        if not isinstance(query, str):
            if isinstance(query, dict):
                # If it's a dict, try to extract the URL
                query = query.get("query", query.get("url", str(query)))
            else:
                query = str(query)

        try:
            firecrawl = FirecrawlApp(api_key=api_key)

            # Auto-detect if this should be a scrape or search
            url_pattern = re.compile(r"^https?://[^\s]+")
            is_url = url_pattern.match(query.strip())

            # If search_type is scrape but query isn't a URL, check if there's a URL in the query
            if search_type == "scrape" and not is_url:
                # Look for URLs within the query text
                url_in_text = re.search(r"https?://[^\s]+", query)
                if url_in_text:
                    query = url_in_text.group()
                    is_url = url_pattern.match(query.strip())

            if search_type == "scrape" and is_url:
                # Scrape a specific URL
                print(f"DEBUG: About to scrape URL: {query.strip()}")
                try:
                    result = firecrawl.scrape(
                        url=query.strip(), formats=["markdown"], only_main_content=True
                    )
                    print(f"DEBUG: Scrape result: {result}")
                    print(f"DEBUG: Result type: {type(result)}")

                    # Handle different response formats from Firecrawl
                    if hasattr(result, "markdown") and result.markdown:
                        # New format: Document object with markdown attribute
                        content = result.markdown
                        return f"Content from {query}:\n\n{content}"
                    elif isinstance(result, dict):
                        # Old format: Dictionary response
                        if result.get("success"):
                            data = result.get("data", {})
                            if isinstance(data, dict):
                                content = data.get("markdown", "No content available")
                            else:
                                content = str(data)
                            return f"Content from {query}:\n\n{content}"
                        else:
                            error_msg = result.get("error", "Unknown error")
                            return f"Error: Could not scrape URL {query}. {error_msg}"
                    elif hasattr(result, "data") and result.data:
                        # Alternative format: Object with data attribute
                        if hasattr(result.data, "markdown"):
                            content = result.data.markdown
                        else:
                            content = str(result.data)
                        return f"Content from {query}:\n\n{content}"
                    else:
                        return f"Error: Could not scrape URL {query}. Unexpected response format: {type(result)}"
                except Exception as scrape_error:
                    print(f"DEBUG: Scrape exception: {scrape_error}")
                    return f"Error scraping {query}: {str(scrape_error)}"

            elif search_type == "scrape" and not is_url:
                return f"Error: Cannot scrape '{query}' - no valid URL found. Please provide a URL starting with http:// or https://"

            else:
                # Perform web search (default behavior)
                print(f"DEBUG: About to search for: {query.strip()}")
                try:
                    search_result = firecrawl.search(
                        query=query.strip(), limit=max_results
                    )
                    print(f"DEBUG: Search result: {search_result}")

                    # Handle different response formats
                    if hasattr(search_result, "web") and search_result.web:
                        # New format: SearchResponse object with web results
                        data = search_result.web
                        formatted_results = []
                        for i, item in enumerate(data[:max_results], 1):
                            title = getattr(item, "title", "No title")
                            url = getattr(item, "url", "No URL")
                            description = getattr(
                                item, "description", "No description"
                            )[:300]
                            formatted_results.append(
                                f"{i}. **{title}**\n   URL: {url}\n   Content: {description}..."
                            )

                        return f"Search results for '{query}':\n\n" + "\n\n".join(
                            formatted_results
                        )

                    elif isinstance(search_result, dict) and "success" in search_result:
                        # Old format: Dictionary response
                        if search_result["success"]:
                            data = search_result.get("data", [])
                            if data and len(data) > 0:
                                formatted_results = []
                                for i, item in enumerate(data[:max_results], 1):
                                    title = item.get("title", "No title")
                                    url = item.get("url", "No URL")
                                    snippet = item.get(
                                        "markdown",
                                        item.get("description", "No description"),
                                    )[:300]
                                    formatted_results.append(
                                        f"{i}. **{title}**\n   URL: {url}\n   Content: {snippet}..."
                                    )

                                return (
                                    f"Search results for '{query}':\n\n"
                                    + "\n\n".join(formatted_results)
                                )

                    return f"No search results found for: {query}"
                except Exception as search_error:
                    print(f"DEBUG: Search exception: {search_error}")
                    return f"Error searching for {query}: {str(search_error)}"

        except Exception as e:
            return f"Error performing web search: {str(e)}"
