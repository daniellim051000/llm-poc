# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a proof of concept LLM Business Data Query System that allows natural language queries against business data through a Flask frontend and Django REST API backend. The system uses LangChain agents with Azure OpenAI to process queries and retrieve data through structured API calls.

## Architecture

```
User Query → Flask App (Port 5000) → LangChain Agent → Django REST API (Port 8000) → SQLite Database
```

## Development Setup

### Prerequisites
- Python 3.13+
- Azure OpenAI API credentials
- Virtual environments for both applications

### Environment Configuration
Create `.env` file in `flask_llm/` with:
```
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
DJANGO_API_URL=http://localhost:8000
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

### Django API Setup
```bash
cd django_api
source venv/bin/activate
python manage.py migrate
python populate_data.py  # Load sample data
python manage.py runserver 8000
```

### Flask LLM App Setup
```bash
cd flask_llm
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade  # Apply SQLAlchemy migrations
python app.py  # Runs on port 5000
```

## Key Components

### Django API (`django_api/`)
- **Models**: Customer, Item, Invoice, Contract, Service with related tables
- **API Endpoints**: RESTful endpoints for all business entities
- **Database**: SQLite with sample business data
- **Data Population**: `populate_data.py` creates test customers, invoices, contracts
- **Test Suite**: Complete model and API endpoint testing in `tests/` directory

### Flask LLM App (`flask_llm/`)
- **LangChain Agent**: `llm_agent.py` - Azure OpenAI integration with tool access
- **API Tools**: `api_tools.py` - 10 specialized tools for querying Django API and web search
- **Flask Routes**: Health check, query endpoint, examples endpoint
- **Templates**: Simple HTML interface at `/`
- **Database**: SQLite with SQLAlchemy ORM and Alembic migrations
- **Authentication**: User login system with Flask-Login
- **Test Suite**: Comprehensive unit tests in `tests/` directory with mocked external services

### LangChain Tools Available
1. `customer_search` - Find customers by name
2. `customer_invoices` - Get customer invoice history
3. `customer_contracts` - Get customer contracts/SLAs
4. `customer_services` - Get service records
5. `item_search` - Search products by name/brand/model
6. `invoice_search` - Search all invoices, filter by customer
7. `active_contracts` - Get all active SLA agreements
8. `serial_lookup` - Machine serial number lookup
9. `service_history` - Maintenance and service records
10. `web_search` - Search the web or scrape URLs using Firecrawl

## Sample Queries
- "What is the purchase history for Company A?"
- "What model did Company A purchase from Ricoh?"
- "What contracts are currently active?"
- "Show me the service history for customer Company B"
- "Search for industry trends about office equipment leasing"
- "What are the latest news about Ricoh printers?"
- "Find information about our competitor's pricing on copiers"

## Testing the System

### Manual Testing
```bash
# Health check
curl http://localhost:5000/health

# Natural language query
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What contracts are currently active?"}'
```

### Automated Unit Tests

The project includes comprehensive unit tests (99 tests total):

```bash
# Run all tests
python run_tests.py

# Run specific test suites
python run_tests.py --django-only    # Django API tests (50 tests)
python run_tests.py --flask-only     # Flask LLM tests (49 tests)
python run_tests.py --verbose        # Detailed output
```

**Test Coverage:**
- **Django API**: All models, views, API endpoints, and error handling
- **Flask LLM**: All routes, authentication, API tools, and LLM agent functionality
- **Mocking**: External services (Azure OpenAI, Firecrawl) are mocked for reliable testing
- **Fixtures**: Comprehensive test data setup for consistent testing

## Database Management

### Django API (Django ORM)
```bash
cd django_api
python manage.py migrate          # Apply Django migrations
python populate_data.py           # Load sample business data
```

### Flask LLM App (SQLAlchemy + Alembic)
```bash
cd flask_llm
flask db upgrade                  # Apply SQLAlchemy migrations
flask db migrate -m "message"    # Create new migration
python create_user.py             # Create user accounts
```

## Important Notes
- Both services must be running simultaneously (Django on 8000, Flask on 5000)
- Django API must be populated with sample data before testing
- Flask app database must be initialized with `flask db upgrade`
- Azure OpenAI credentials are required for LLM functionality
- The system is designed for business data queries, not general conversation
