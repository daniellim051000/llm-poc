#!/usr/bin/env python3
"""
Example usage of the Ricoh MCP Server
Demonstrates how the server would interact with the Ricoh Django API
"""

import json
from datetime import date

from models import (
    ContactDetailCreate,
    ContractCreate,
    CustomerCreate,
    CustomerUpdate,
    InvoiceCreate,
    InvoiceDetailCreate,
    ItemCreate,
    SerialCreate,
    ServiceCreate,
    ServiceDetailCreate,
)


def example_data_creation():
    """Examples of creating data structures for the MCP tools"""

    print("=== Ricoh MCP Server - Example Usage ===\n")

    # Customer Examples
    print("1. Customer Operations:")

    # Create customer
    new_customer = CustomerCreate(
        name="TechCorp Solutions",
        email="contact@techcorp.com",
        phone="+1-555-0199",
        address="456 Innovation Drive, Tech City, TC 12345",
    )
    print(
        f"New customer data: {json.dumps(new_customer.model_dump(exclude_none=True), indent=2)}"
    )

    # Update customer (partial)
    customer_update = CustomerUpdate(phone="+1-555-0200")
    print(
        f"Customer update data: {json.dumps(customer_update.model_dump(exclude_none=True), indent=2)}"
    )

    print("\n" + "=" * 60 + "\n")

    # Item Examples
    print("2. Item/Product Operations:")

    new_item = ItemCreate(
        name="LaserJet Pro 4000",
        model="LJ-4000",
        brand="HP",
        item_group=1,
        price=899.99,
    )
    print(
        f"New item data: {json.dumps(new_item.model_dump(exclude_none=True), indent=2)}"
    )

    print("\n" + "=" * 60 + "\n")

    # Invoice Examples
    print("3. Invoice Operations:")

    # Invoice with multiple line items
    invoice_details = [
        InvoiceDetailCreate(item=1, quantity=2, unit_price=899.99),
        InvoiceDetailCreate(item=2, quantity=5, unit_price=29.99),
    ]

    new_invoice = InvoiceCreate(
        customer=1,
        invoice_date=date(2024, 1, 15),
        status="pending",
        details=invoice_details,
    )

    # Calculate total (as the server would do)
    total = sum(detail.quantity * detail.unit_price for detail in new_invoice.details)

    invoice_data = new_invoice.model_dump(exclude_none=True)
    invoice_data["invoice_date"] = str(
        invoice_data["invoice_date"]
    )  # Convert date for API
    invoice_data["total_amount"] = total

    print(f"New invoice data: {json.dumps(invoice_data, indent=2)}")
    print(f"Calculated total: ${total:.2f}")

    print("\n" + "=" * 60 + "\n")

    # Contract Examples
    print("4. Contract Operations:")

    contact_details = [
        ContactDetailCreate(
            contact_person="Alice Johnson",
            role="IT Manager",
            phone="+1-555-0150",
            email="alice.johnson@techcorp.com",
        ),
        ContactDetailCreate(
            contact_person="Bob Wilson",
            role="Procurement",
            phone="+1-555-0151",
            email="bob.wilson@techcorp.com",
        ),
    ]

    new_contract = ContractCreate(
        customer=1,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        contract_type="Maintenance SLA",
        status="active",
        terms="24/7 support with 4-hour response time. Includes all parts and labor.",
        contact_details=contact_details,
    )

    contract_data = new_contract.model_dump(exclude_none=True)
    contract_data["start_date"] = str(contract_data["start_date"])
    contract_data["end_date"] = str(contract_data["end_date"])

    print(f"New contract data: {json.dumps(contract_data, indent=2)}")

    print("\n" + "=" * 60 + "\n")

    # Serial Examples
    print("5. Serial Number Operations:")

    new_serial = SerialCreate(
        serial_number="HP-LJ4000-2024-001234",
        item=1,
        status="active",
        manufactured_date=date(2024, 1, 5),
        warranty_end_date=date(2027, 1, 5),
    )

    serial_data = new_serial.model_dump(exclude_none=True)
    serial_data["manufactured_date"] = str(serial_data["manufactured_date"])
    serial_data["warranty_end_date"] = str(serial_data["warranty_end_date"])

    print(f"New serial data: {json.dumps(serial_data, indent=2)}")

    print("\n" + "=" * 60 + "\n")

    # Service Examples
    print("6. Service Operations:")

    service_details = [
        ServiceDetailCreate(
            serial=1,
            description="Replaced toner cartridge and performed cleaning cycle",
            parts_used="Toner cartridge (HP-85A), Cleaning kit",
            labor_hours=0.5,
            cost=85.00,
        ),
        ServiceDetailCreate(
            serial=1,
            description="Updated firmware to latest version",
            parts_used="",
            labor_hours=0.25,
            cost=25.00,
        ),
    ]

    new_service = ServiceCreate(
        service_name="Routine Maintenance",
        customer=1,
        service_date=date(2024, 1, 20),
        technician="Mike Rodriguez",
        status="completed",
        notes="Service completed successfully. Next maintenance due in 3 months.",
        details=service_details,
    )

    service_data = new_service.model_dump(exclude_none=True)
    service_data["service_date"] = str(service_data["service_date"])

    total_service_cost = sum(detail.cost for detail in new_service.details)

    print(f"New service data: {json.dumps(service_data, indent=2)}")
    print(f"Total service cost: ${total_service_cost:.2f}")


def example_ai_interactions():
    """Examples of how AI would interact with the MCP server"""

    print("\n" + "=" * 60)
    print("7. Example AI Interactions with Ricoh MCP Server:")
    print("=" * 60 + "\n")

    examples = [
        {
            "query": "List all customers",
            "tool": "list_customers",
            "parameters": {},
            "description": "AI would call list_customers() with no parameters",
        },
        {
            "query": "Find customers with 'Tech' in their name",
            "tool": "list_customers",
            "parameters": {"name_filter": "Tech"},
            "description": "AI would call list_customers(name_filter='Tech')",
        },
        {
            "query": "Show me the invoices for customer ID 1",
            "tool": "get_customer_invoices",
            "parameters": {"customer_id": 1},
            "description": "AI would call get_customer_invoices(customer_id=1)",
        },
        {
            "query": "Create a new customer called 'NewCorp' with email 'info@newcorp.com'",
            "tool": "create_customer",
            "parameters": {
                "customer_data": {"name": "NewCorp", "email": "info@newcorp.com"}
            },
            "description": "AI would call create_customer() with CustomerCreate model",
        },
        {
            "query": "What are all the active contracts?",
            "tool": "get_active_contracts",
            "parameters": {},
            "description": "AI would call get_active_contracts()",
        },
        {
            "query": "Find all HP printers in inventory",
            "tool": "search_items",
            "parameters": {"brand": "HP"},
            "description": "AI would call search_items(brand='HP')",
        },
        {
            "query": "Show me services performed in January 2024",
            "tool": "get_services_by_date",
            "parameters": {"start_date": "2024-01-01", "end_date": "2024-01-31"},
            "description": "AI would call get_services_by_date() with date range",
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f'{i}. User Query: "{example["query"]}"')
        print(f"   MCP Tool: {example['tool']}")
        print(f"   Parameters: {json.dumps(example['parameters'], indent=6)}")
        print(f"   Description: {example['description']}")
        print()


def main():
    """Main example runner"""
    try:
        example_data_creation()
        example_ai_interactions()

        print("=" * 60)
        print("Example completed successfully!")
        print("=" * 60)
        print("\nTo use this MCP server:")
        print("1. Ensure your Django API is running on http://localhost:8000")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Configure environment: cp .env.sample .env")
        print("4. Run the server: python server.py")
        print("5. Configure Claude Desktop with the server path")
        print("6. Use natural language to interact with your business data!")

    except Exception as e:
        print(f"Error running example: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
