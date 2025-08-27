import os
from datetime import date, timedelta
from decimal import Decimal

import django
import pytest
from django.conf import settings

# Configure Django settings before importing models
if not settings.configured:
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


@pytest.fixture
def sample_customer():
    """Create a sample customer for testing."""
    return Customer.objects.create(
        name="Test Company",
        email="test@company.com",
        phone="123-456-7890",
        address="123 Test St",
    )


@pytest.fixture
def sample_item_group():
    """Create a sample item group for testing."""
    return ItemGroup.objects.create(
        name="Office Equipment", description="Printers, scanners, and copiers"
    )


@pytest.fixture
def sample_item(sample_item_group):
    """Create a sample item for testing."""
    return Item.objects.create(
        name="Color Printer",
        model="P3000",
        brand="Ricoh",
        item_group=sample_item_group,
        price=Decimal("1500.00"),
    )


@pytest.fixture
def sample_invoice(sample_customer):
    """Create a sample invoice for testing."""
    return Invoice.objects.create(
        invoice_number="INV-001",
        customer=sample_customer,
        invoice_date=date.today(),
        total_amount=Decimal("1500.00"),
        status="paid",
    )


@pytest.fixture
def sample_invoice_detail(sample_invoice, sample_item):
    """Create a sample invoice detail for testing."""
    return InvoiceDetail.objects.create(
        invoice=sample_invoice,
        item=sample_item,
        quantity=1,
        unit_price=Decimal("1500.00"),
        total_price=Decimal("1500.00"),
    )


@pytest.fixture
def sample_serial(sample_item):
    """Create a sample serial for testing."""
    return Serial.objects.create(
        serial_number="SN123456789",
        item=sample_item,
        status="active",
        manufactured_date=date(2023, 1, 1),
        warranty_end_date=date(2026, 1, 1),
    )


@pytest.fixture
def sample_contract(sample_customer):
    """Create a sample contract for testing."""
    return Contract.objects.create(
        contract_number="CON-001",
        customer=sample_customer,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
        contract_type="Service Level Agreement",
        status="active",
        terms="Standard SLA terms",
    )


@pytest.fixture
def sample_contact_detail(sample_contract):
    """Create a sample contact detail for testing."""
    return ContactDetail.objects.create(
        contract=sample_contract,
        contact_person="John Doe",
        role="IT Manager",
        phone="123-456-7890",
        email="john.doe@company.com",
    )


@pytest.fixture
def sample_service(sample_customer):
    """Create a sample service for testing."""
    return Service.objects.create(
        service_name="Quarterly Maintenance",
        customer=sample_customer,
        service_date=date.today(),
        technician="Jane Smith",
        status="completed",
        notes="All systems checked",
    )


@pytest.fixture
def sample_service_detail(sample_service, sample_serial):
    """Create a sample service detail for testing."""
    return ServiceDetail.objects.create(
        service=sample_service,
        serial=sample_serial,
        description="Replaced toner cartridge",
        parts_used="Toner cartridge (Black)",
        labor_hours=Decimal("1.50"),
        cost=Decimal("75.00"),
    )
