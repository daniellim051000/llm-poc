import os
from datetime import date
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mock_api.settings")
django.setup()

from api.models import (
    ContactDetail,
    Contract,
    Customer,
    Invoice,
    InvoiceDetail,
    Item,
    ItemGroup,
    Serial,
    Service,
    ServiceDetail,
)


def populate_data():
    print("Creating sample data...")

    # Create customers
    customer_a = Customer.objects.create(
        name="Company A",
        email="contact@companya.com",
        phone="555-0001",
        address="123 Business St, City A",
    )

    customer_b = Customer.objects.create(
        name="Enterprise B",
        email="info@enterpriseb.com",
        phone="555-0002",
        address="456 Corporate Ave, City B",
    )

    # Create item groups
    printers = ItemGroup.objects.create(
        name="Printers", description="Office printing equipment"
    )

    copiers = ItemGroup.objects.create(
        name="Copiers", description="Document copying machines"
    )

    # Create items (Ricoh products)
    ricoh_printer = Item.objects.create(
        name="Color Laser Printer",
        model="SP C360DNw",
        brand="Ricoh",
        item_group=printers,
        price=Decimal("4229.95"),  # Converted from USD 899.99 to MYR (899.99 * 4.7)
    )

    ricoh_copier = Item.objects.create(
        name="Multifunction Copier",
        model="IM C3000",
        brand="Ricoh",
        item_group=copiers,
        price=Decimal("11749.95"),  # Converted from USD 2499.99 to MYR (2499.99 * 4.7)
    )

    # Create serials
    serial1 = Serial.objects.create(
        serial_number="RC2024001",
        item=ricoh_printer,
        status="active",
        manufactured_date=date(2024, 1, 15),
        warranty_end_date=date(2026, 1, 15),
    )

    serial2 = Serial.objects.create(
        serial_number="RC2024002",
        item=ricoh_copier,
        status="active",
        manufactured_date=date(2024, 2, 20),
        warranty_end_date=date(2027, 2, 20),
    )

    # Create invoices
    invoice1 = Invoice.objects.create(
        invoice_number="INV-2024-001",
        customer=customer_a,
        invoice_date=date(2024, 3, 1),
        total_amount=Decimal("899.99"),
        status="paid",
    )

    InvoiceDetail.objects.create(
        invoice=invoice1,
        item=ricoh_printer,
        quantity=1,
        unit_price=Decimal("899.99"),
        total_price=Decimal("899.99"),
    )

    invoice2 = Invoice.objects.create(
        invoice_number="INV-2024-002",
        customer=customer_b,
        invoice_date=date(2024, 4, 15),
        total_amount=Decimal("2499.99"),
        status="paid",
    )

    InvoiceDetail.objects.create(
        invoice=invoice2,
        item=ricoh_copier,
        quantity=1,
        unit_price=Decimal("2499.99"),
        total_price=Decimal("2499.99"),
    )

    # Create contracts
    contract1 = Contract.objects.create(
        contract_number="SLA-2024-001",
        customer=customer_a,
        start_date=date(2024, 3, 1),
        end_date=date(2025, 3, 1),
        contract_type="Service Agreement",
        status="active",
        terms="Monthly maintenance and support",
    )

    ContactDetail.objects.create(
        contract=contract1,
        contact_person="John Smith",
        role="IT Manager",
        phone="555-0001",
        email="john.smith@companya.com",
    )

    contract2 = Contract.objects.create(
        contract_number="SLA-2024-002",
        customer=customer_b,
        start_date=date(2024, 4, 15),
        end_date=date(2025, 4, 15),
        contract_type="Lease Agreement",
        status="active",
        terms="Equipment lease with service included",
    )

    ContactDetail.objects.create(
        contract=contract2,
        contact_person="Jane Doe",
        role="Office Manager",
        phone="555-0002",
        email="jane.doe@enterpriseb.com",
    )

    # Create services
    service1 = Service.objects.create(
        service_name="Quarterly Maintenance",
        customer=customer_a,
        service_date=date(2024, 6, 1),
        technician="Mike Johnson",
        status="completed",
        notes="Routine maintenance completed successfully",
    )

    ServiceDetail.objects.create(
        service=service1,
        serial=serial1,
        description="Toner replacement and cleaning",
        parts_used="Toner cartridge, cleaning kit",
        labor_hours=Decimal("2.5"),
        cost=Decimal("150.00"),
    )

    service2 = Service.objects.create(
        service_name="Paper Jam Repair",
        customer=customer_b,
        service_date=date(2024, 7, 10),
        technician="Sarah Wilson",
        status="completed",
        notes="Fixed paper feed mechanism",
    )

    ServiceDetail.objects.create(
        service=service2,
        serial=serial2,
        description="Repaired paper feed roller",
        parts_used="Feed roller assembly",
        labor_hours=Decimal("1.0"),
        cost=Decimal("85.00"),
    )

    print("Sample data created successfully!")
    print(f"Created {Customer.objects.count()} customers")
    print(f"Created {Item.objects.count()} items")
    print(f"Created {Invoice.objects.count()} invoices")
    print(f"Created {Contract.objects.count()} contracts")
    print(f"Created {Service.objects.count()} services")


if __name__ == "__main__":
    populate_data()
