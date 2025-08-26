# LLM Business Data Query System

A proof of concept system that enables natural language querying of business data through an intelligent LLM agent. The system combines a Flask frontend with LangChain agents and a Django REST API backend to process queries and retrieve structured business data.

## 🏗️ Architecture

```
User Query → Flask App (Port 5000) → LangChain Agent → Django REST API (Port 8000) → SQLite Database
```

The system consists of two main components:

- **Flask LLM App**: Web interface and LangChain agent for processing natural language queries
- **Django API**: RESTful backend providing structured access to business data

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Azure OpenAI API credentials
- Virtual environment support

### 1. Environment Setup

Create a `.env` file in the `flask_llm/` directory:

```env
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=your_endpoint_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
DJANGO_API_URL=http://localhost:8000
```

### 2. Django API Setup

```bash
cd django_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
python manage.py migrate
python populate_data.py  # Load sample business data
python manage.py runserver 8000
```

### 3. Flask LLM App Setup

Open a new terminal:

```bash
cd flask_llm
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py  # Runs on port 5000
```

### 4. Access the Application

- Web Interface: http://localhost:5000
- Health Check: http://localhost:5000/health
- API Examples: http://localhost:5000/examples

## 📊 Data Model

The system manages comprehensive business data including:

- **Customers**: Company information and contact details
- **Items**: Products with brands, models, and pricing
- **Invoices**: Purchase history and billing records
- **Contracts**: Service level agreements and terms
- **Services**: Maintenance records and technician reports
- **Serials**: Equipment tracking with warranty information

## 🛠️ API Tools

The LangChain agent has access to 9 specialized tools for querying business data:

| Tool | Purpose |
|------|---------|
| `customer_search` | Find customers by name |
| `customer_invoices` | Get customer invoice history |
| `customer_contracts` | Get customer contracts/SLAs |
| `customer_services` | Get service records |
| `item_search` | Search products by name/brand/model |
| `invoice_search` | Search all invoices, filter by customer |
| `active_contracts` | Get all active SLA agreements |
| `serial_lookup` | Machine serial number lookup |
| `service_history` | Maintenance and service records |

## 💬 Sample Queries

Try these natural language queries:

- "What is the purchase history for Company A?"
- "What model did Company A purchase from Ricoh?"
- "What contracts are currently active?"
- "Show me the service history for customer Company B"
- "What machines does Enterprise B have under contract?"
- "Find all items from Ricoh brand"
- "What is the residual value information for our machines?"

## 🧪 Testing the System

### Health Check
```bash
curl http://localhost:5000/health
```

### Query via API
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What contracts are currently active?"}'
```

### Get Sample Queries
```bash
curl http://localhost:5000/examples
```

## 📁 Project Structure

```
llm-poc/
├── django_api/                 # Django REST API backend
│   ├── api/                   # Main API application
│   │   ├── models.py          # Data models
│   │   ├── serializers.py     # API serializers
│   │   ├── views.py           # API endpoints
│   │   └── urls.py            # URL routing
│   ├── populate_data.py       # Sample data loader
│   └── manage.py              # Django management
├── flask_llm/                 # Flask LLM frontend
│   ├── app.py                 # Main Flask application
│   ├── llm_agent.py           # LangChain agent setup
│   ├── api_tools.py           # Business data tools
│   └── templates/             # HTML templates
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

### Flask App Endpoints

- `GET /` - Web interface
- `GET /health` - System health check
- `POST /query` - Natural language query endpoint
- `GET /examples` - Sample queries

### Django API Endpoints

- `/api/customers/` - Customer management
- `/api/items/` - Product catalog
- `/api/invoices/` - Invoice records
- `/api/contracts/` - Contract management
- `/api/services/` - Service records

## ⚠️ Important Notes

- **Both services must run simultaneously** (Django on port 8000, Flask on port 5000)
- **Sample data required**: Run `populate_data.py` before testing
- **Azure OpenAI credentials**: Required for LLM functionality
- **Business focus**: Designed for business data queries, not general conversation

## 🛠️ Development

### Code Quality
```bash
# Format code
ruff format .

# Lint code
ruff check .
```

### Dependencies
All dependencies are managed in the root `requirements.txt` file for both Flask and Django applications.

## 📝 License

This is a proof of concept project for demonstration purposes.
