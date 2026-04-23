# Ricoh MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to your Ricoh business API. This server exposes 38+ tools for full CRUD operations on customers, items, invoices, contracts, serials, and services.

## Features

- **Complete CRUD Operations**: Create, Read, Update, Delete for all business entities
- **Universal Compatibility**: Works with Claude Desktop, Cursor, OpenAI, and any MCP-compatible AI system
- **Type Safety**: Strong typing with Pydantic models for reliable data validation
- **Error Handling**: Comprehensive error handling with meaningful error messages
- **Modular Design**: Clean, modular architecture for easy maintenance and extension

## Available Tools

### Customer Tools (8 tools)
- `list_customers` - List all customers with optional name filtering
- `get_customer` - Get customer details by ID
- `create_customer` - Create new customer
- `update_customer` - Update existing customer
- `delete_customer` - Delete customer
- `get_customer_invoices` - Get customer's invoices
- `get_customer_contracts` - Get customer's contracts
- `get_customer_services` - Get customer's services

### Item Tools (6 tools)
- `list_items` - List all items with optional filtering
- `get_item` - Get item details by ID
- `create_item` - Create new item
- `update_item` - Update existing item
- `delete_item` - Delete item
- `search_items` - Search items by name/brand/model

### Invoice Tools (6 tools)
- `list_invoices` - List all invoices with optional customer filtering
- `get_invoice` - Get invoice details with line items
- `create_invoice` - Create new invoice with line items
- `update_invoice` - Update existing invoice
- `delete_invoice` - Delete invoice
- `search_invoices_by_customer` - Search invoices by customer name

### Contract Tools (6 tools)
- `list_contracts` - List all contracts with optional status filtering
- `get_contract` - Get contract details by ID
- `create_contract` - Create new contract
- `update_contract` - Update existing contract
- `delete_contract` - Delete contract
- `get_active_contracts` - Get all active contracts

### Serial Tools (6 tools)
- `list_serials` - List all serial numbers with optional item filtering
- `get_serial` - Get serial details by ID
- `create_serial` - Create new serial number
- `update_serial` - Update existing serial
- `delete_serial` - Delete serial
- `lookup_serials_by_item` - Get serials for specific item

### Service Tools (6 tools)
- `list_services` - List all services with optional date filtering
- `get_service` - Get service details by ID
- `create_service` - Create new service record
- `update_service` - Update existing service
- `delete_service` - Delete service
- `get_services_by_date` - Get services within date range

## Prerequisites

- Python 3.10 or higher
- Django API running on http://localhost:8000 (or configured URL)
- UV package manager (recommended) or pip

## Installation

### Using the Project Virtual Environment (Recommended)

Since this project already has a virtual environment set up, use the existing one:

```bash
# Navigate to the MCP server directory
cd /path/to/llm-poc/mcp_server

# Install dependencies using the existing virtual environment
/path/to/llm-poc/venv/bin/pip install -r requirements.txt
```

### Alternative: Create New Virtual Environment

If you prefer to create a separate environment for the MCP server:

```bash
cd mcp_server
python3 -m venv mcp_venv
source mcp_venv/bin/activate  # On Windows: mcp_venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

1. Copy the environment template:
```bash
cp .env.sample .env
```

2. Edit `.env` file:
```env
# Django API Configuration
DJANGO_API_URL=http://localhost:8000

# Optional configurations
LOG_LEVEL=INFO
MCP_SERVER_NAME=business-api
```

## Usage

### Running the MCP Server

**Important**: The MCP server is automatically started by Claude Desktop when needed. You don't need to run it manually. However, you can test it manually:

```bash
# Test using the project virtual environment
/path/to/llm-poc/venv/bin/python server.py

# Or if using separate virtual environment
source mcp_venv/bin/activate
python server.py
```

The server will start and display available tools:

```
Starting MCP Server: ricoh-mcp
Django API URL: http://localhost:8000
Available tools:
- Customer tools: list_customers, get_customer, create_customer, ...
- Item tools: list_items, get_item, create_item, ...
...
Server ready for MCP connections...
```

### Connecting to Claude Desktop

1. Open Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Add your MCP server using the project's virtual environment:
```json
{
  "mcpServers": {
    "ricoh-mcp": {
      "command": "/absolute/path/to/llm-poc/venv/bin/python",
      "args": [
        "/absolute/path/to/llm-poc/mcp_server/server.py"
      ]
    }
  }
}
```

**Alternative if you created a separate virtual environment:**
```json
{
  "mcpServers": {
    "ricoh-mcp": {
      "command": "/path/to/mcp_server/mcp_venv/bin/python",
      "args": [
        "/path/to/mcp_server/server.py"
      ]
    }
  }
}
```

**Note**: Always use absolute paths for both the Python executable and the server script. Replace `/path/to/` with your actual paths.

3. Restart Claude Desktop completely
4. The MCP tools will be automatically available in your conversations

### Example Usage with AI Assistant

Once connected, you can use natural language with your AI assistant:

```
"List all customers"
"Show me invoices for Company A"
"Create a new customer named 'Acme Corp' with email 'info@acme.com'"
"What contracts are currently active?"
"Find all Ricoh printers in inventory"
"Create an invoice for customer ID 1 with 2 units of item ID 5 at $100 each"
```

## API Integration

This MCP server connects to your Django API endpoints:

- **Base URL**: Configured via `DJANGO_API_URL` environment variable
- **Authentication**: Currently supports API without authentication (can be extended)
- **Data Format**: JSON request/response format
- **Error Handling**: Comprehensive error handling with meaningful messages

### Required Django API Endpoints

The server expects these Django REST API endpoints to be available:

```
GET/POST    /api/customers/
GET/PUT/DELETE /api/customers/{id}/
GET         /api/customers/{id}/invoices/
GET         /api/customers/{id}/contracts/
GET         /api/customers/{id}/services/

GET/POST    /api/items/
GET/PUT/DELETE /api/items/{id}/
GET         /api/items/search/?q={query}&brand={brand}

GET/POST    /api/invoices/
GET/PUT/DELETE /api/invoices/{id}/
GET         /api/invoices/by_customer/?customer_name={name}

GET/POST    /api/contracts/
GET/PUT/DELETE /api/contracts/{id}/
GET         /api/contracts/active/

GET/POST    /api/serials/
GET/PUT/DELETE /api/serials/{id}/
GET         /api/serials/by_item/?item_id={id}

GET/POST    /api/services/
GET/PUT/DELETE /api/services/{id}/
GET         /api/services/by_date_range/?start_date={date}&end_date={date}
```

## Development

### Project Structure

```
mcp_server/
├── server.py           # Main MCP server
├── models.py           # Pydantic models
├── invoice_tools.py    # Invoice-related tools
├── contract_tools.py   # Contract-related tools
├── serial_tools.py     # Serial-related tools
├── service_tools.py    # Service-related tools
├── tests/              # Test suite
├── requirements.txt    # Dependencies
├── pyproject.toml      # Project configuration
├── .env.sample         # Environment template
└── README.md           # This file
```

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

### Adding New Tools

To add new tools:

1. Define Pydantic models in `models.py`
2. Create tool functions using the `@mcp.tool()` decorator
3. Follow the existing pattern for error handling
4. Add tests in the `tests/` directory

Example:
```python
@mcp.tool()
def my_new_tool(param: str) -> str:
    """Tool description"""
    try:
        # Tool implementation
        return "Success"
    except Exception as e:
        return f"Error: {str(e)}"
```

## Troubleshooting

### Common Issues

1. **"spawn python ENOENT" errors**:
   - Use the full absolute path to your Python executable in the Claude Desktop config
   - For this project: `/absolute/path/to/llm-poc/venv/bin/python`
   - Avoid using just `python` or `python3` as commands

2. **"Connection refused" errors**:
   - Ensure Django API is running on the configured port
   - Check `DJANGO_API_URL` in your `.env` file

3. **MCP server not found in Claude Desktop**:
   - Verify absolute paths in your Claude Desktop config
   - Restart Claude Desktop completely (quit and reopen)
   - Check that dependencies are installed in the virtual environment

4. **Import/Module errors**:
   - Ensure all dependencies are installed: `/absolute/path/to/llm-poc/venv/bin/pip install -r requirements.txt`
   - Verify you're using the correct virtual environment path

5. **API errors**:
   - Check Django API logs for detailed error information
   - Verify the API endpoints are working with curl/Postman
   - Ensure data validation matches the expected format

### Debug Mode

Set `LOG_LEVEL=DEBUG` in your `.env` file for more detailed logging:

```env
LOG_LEVEL=DEBUG
```

## Security Considerations

- **Data Access**: This server provides full CRUD access to your business data
- **Authentication**: Consider adding API authentication for production use
- **Network**: Run on secure networks and use HTTPS for API connections
- **User Consent**: Users should understand what data is being accessed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review Django API logs and MCP server output
3. Open an issue in the project repository
