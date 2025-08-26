# LLM Business Data Query System

A proof of concept system that uses LangChain and Azure OpenAI to query business data through natural language.

## Architecture

```
User Query → Flask App → LangChain Agent → Django REST API → Database
```

## Setup

1. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

2. **Install Dependencies**
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start Django API** (in separate terminal)
   ```bash
   cd ../django_api
   source venv/bin/activate
   python manage.py runserver 8000
   ```

4. **Start Flask App**
   ```bash
   source venv/bin/activate
   python app.py
   ```

## Usage

### Health Check
```bash
curl http://localhost:5000/
```

### Query Examples
```bash
# Get sample queries
curl http://localhost:5000/examples

# Ask about invoice history
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the purchase history for Company A?"}'

# Ask about Ricoh products
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What model did Company A purchase from Ricoh?"}'

# Ask about active contracts
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What contracts are currently active?"}'
```

## Environment Variables

- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your model deployment name
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)
- `DJANGO_API_URL`: Django API URL (default: http://localhost:8000)

## Available Tools

The LangChain agent has access to these tools:
- **Customer Search**: Find customers by name
- **Customer Invoices**: Get invoices for a specific customer
- **Customer Contracts**: Get contracts for a specific customer
- **Customer Services**: Get service history for a customer
- **Item Search**: Search products by name, model, or brand
- **Invoice Search**: Search invoices, filter by customer
- **Active Contracts**: Get all active SLA agreements
- **Serial Lookup**: Look up machine serial numbers
- **Service History**: Get maintenance and service records
