from datetime import date, timedelta
from decimal import Decimal

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
from django.db import IntegrityError
from django.test import TestCase


class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Company",
            email="test@company.com",
            phone="123-456-7890",
            address="123 Test St",
        )

    def test_customer_creation(self):
        self.assertEqual(self.customer.name, "Test Company")
        self.assertEqual(self.customer.email, "test@company.com")
        self.assertEqual(self.customer.phone, "123-456-7890")
        self.assertEqual(self.customer.address, "123 Test St")
        self.assertTrue(self.customer.created_at)

    def test_customer_str(self):
        self.assertEqual(str(self.customer), "Test Company")

    def test_customer_optional_fields(self):
        customer = Customer.objects.create(name="Minimal Company")
        self.assertEqual(customer.name, "Minimal Company")
        self.assertIsNone(customer.email)
        self.assertIsNone(customer.phone)
        self.assertIsNone(customer.address)


class ItemGroupModelTest(TestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(
            name="Office Equipment", description="Printers, scanners, and copiers"
        )

    def test_item_group_creation(self):
        self.assertEqual(self.item_group.name, "Office Equipment")
        self.assertEqual(self.item_group.description, "Printers, scanners, and copiers")

    def test_item_group_str(self):
        self.assertEqual(str(self.item_group), "Office Equipment")


class ItemModelTest(TestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item = Item.objects.create(
            name="Color Printer",
            model="P3000",
            brand="Ricoh",
            item_group=self.item_group,
            price=Decimal("1500.00"),
        )

    def test_item_creation(self):
        self.assertEqual(self.item.name, "Color Printer")
        self.assertEqual(self.item.model, "P3000")
        self.assertEqual(self.item.brand, "Ricoh")
        self.assertEqual(self.item.item_group, self.item_group)
        self.assertEqual(self.item.price, Decimal("1500.00"))

    def test_item_str(self):
        self.assertEqual(str(self.item), "Ricoh Color Printer (P3000)")

    def test_item_group_cascade_delete(self):
        self.item_group.delete()
        self.assertFalse(Item.objects.filter(id=self.item.id).exists())


class InvoiceModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.invoice = Invoice.objects.create(
            invoice_number="INV-001",
            customer=self.customer,
            invoice_date=date.today(),
            total_amount=Decimal("2500.00"),
            status="paid",
        )

    def test_invoice_creation(self):
        self.assertEqual(self.invoice.invoice_number, "INV-001")
        self.assertEqual(self.invoice.customer, self.customer)
        self.assertEqual(self.invoice.total_amount, Decimal("2500.00"))
        self.assertEqual(self.invoice.status, "paid")

    def test_invoice_str(self):
        self.assertEqual(str(self.invoice), "Invoice INV-001 - Test Company")

    def test_invoice_number_unique(self):
        with self.assertRaises(IntegrityError):
            Invoice.objects.create(
                invoice_number="INV-001",
                customer=self.customer,
                invoice_date=date.today(),
                total_amount=Decimal("1000.00"),
            )


class InvoiceDetailModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item = Item.objects.create(
            name="Printer", item_group=self.item_group, price=Decimal("500.00")
        )
        self.invoice = Invoice.objects.create(
            invoice_number="INV-001",
            customer=self.customer,
            invoice_date=date.today(),
            total_amount=Decimal("1500.00"),
        )
        self.detail = InvoiceDetail.objects.create(
            invoice=self.invoice,
            item=self.item,
            quantity=3,
            unit_price=Decimal("500.00"),
            total_price=Decimal("1500.00"),
        )

    def test_invoice_detail_creation(self):
        self.assertEqual(self.detail.invoice, self.invoice)
        self.assertEqual(self.detail.item, self.item)
        self.assertEqual(self.detail.quantity, 3)
        self.assertEqual(self.detail.unit_price, Decimal("500.00"))
        self.assertEqual(self.detail.total_price, Decimal("1500.00"))

    def test_invoice_detail_str(self):
        self.assertEqual(str(self.detail), "INV-001 - Printer")


class SerialModelTest(TestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item = Item.objects.create(name="Printer", item_group=self.item_group)
        self.serial = Serial.objects.create(
            serial_number="SN123456789",
            item=self.item,
            status="active",
            manufactured_date=date(2023, 1, 1),
            warranty_end_date=date(2026, 1, 1),
        )

    def test_serial_creation(self):
        self.assertEqual(self.serial.serial_number, "SN123456789")
        self.assertEqual(self.serial.item, self.item)
        self.assertEqual(self.serial.status, "active")
        self.assertEqual(self.serial.manufactured_date, date(2023, 1, 1))
        self.assertEqual(self.serial.warranty_end_date, date(2026, 1, 1))

    def test_serial_str(self):
        self.assertEqual(str(self.serial), "SN123456789 (Printer)")

    def test_serial_number_unique(self):
        with self.assertRaises(IntegrityError):
            Serial.objects.create(serial_number="SN123456789", item=self.item)


class ContractModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.contract = Contract.objects.create(
            contract_number="CON-001",
            customer=self.customer,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            contract_type="Service Level Agreement",
            status="active",
            terms="Standard SLA terms and conditions",
        )

    def test_contract_creation(self):
        self.assertEqual(self.contract.contract_number, "CON-001")
        self.assertEqual(self.contract.customer, self.customer)
        self.assertEqual(self.contract.contract_type, "Service Level Agreement")
        self.assertEqual(self.contract.status, "active")
        self.assertEqual(self.contract.terms, "Standard SLA terms and conditions")

    def test_contract_str(self):
        self.assertEqual(str(self.contract), "Contract CON-001 - Test Company")

    def test_contract_number_unique(self):
        with self.assertRaises(IntegrityError):
            Contract.objects.create(
                contract_number="CON-001",
                customer=self.customer,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                contract_type="Maintenance",
            )


class ContactDetailModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.contract = Contract.objects.create(
            contract_number="CON-001",
            customer=self.customer,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            contract_type="SLA",
        )
        self.contact = ContactDetail.objects.create(
            contract=self.contract,
            contact_person="John Doe",
            role="IT Manager",
            phone="123-456-7890",
            email="john.doe@company.com",
        )

    def test_contact_detail_creation(self):
        self.assertEqual(self.contact.contract, self.contract)
        self.assertEqual(self.contact.contact_person, "John Doe")
        self.assertEqual(self.contact.role, "IT Manager")
        self.assertEqual(self.contact.phone, "123-456-7890")
        self.assertEqual(self.contact.email, "john.doe@company.com")

    def test_contact_detail_str(self):
        self.assertEqual(str(self.contact), "John Doe (CON-001)")


class ServiceModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.service = Service.objects.create(
            service_name="Quarterly Maintenance",
            customer=self.customer,
            service_date=date.today(),
            technician="Jane Smith",
            status="completed",
            notes="All systems checked and cleaned",
        )

    def test_service_creation(self):
        self.assertEqual(self.service.service_name, "Quarterly Maintenance")
        self.assertEqual(self.service.customer, self.customer)
        self.assertEqual(self.service.technician, "Jane Smith")
        self.assertEqual(self.service.status, "completed")
        self.assertEqual(self.service.notes, "All systems checked and cleaned")

    def test_service_str(self):
        today_str = date.today().strftime("%Y-%m-%d")
        expected = f"Quarterly Maintenance - Test Company ({today_str})"
        self.assertEqual(str(self.service), expected)


class ServiceDetailModelTest(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item = Item.objects.create(name="Printer", item_group=self.item_group)
        self.serial = Serial.objects.create(serial_number="SN123456789", item=self.item)
        self.service = Service.objects.create(
            service_name="Maintenance",
            customer=self.customer,
            service_date=date.today(),
        )
        self.service_detail = ServiceDetail.objects.create(
            service=self.service,
            serial=self.serial,
            description="Replaced toner cartridge and cleaned print heads",
            parts_used="Toner cartridge (Black)",
            labor_hours=Decimal("2.50"),
            cost=Decimal("150.00"),
        )

    def test_service_detail_creation(self):
        self.assertEqual(self.service_detail.service, self.service)
        self.assertEqual(self.service_detail.serial, self.serial)
        self.assertEqual(
            self.service_detail.description,
            "Replaced toner cartridge and cleaned print heads",
        )
        self.assertEqual(self.service_detail.parts_used, "Toner cartridge (Black)")
        self.assertEqual(self.service_detail.labor_hours, Decimal("2.50"))
        self.assertEqual(self.service_detail.cost, Decimal("150.00"))

    def test_service_detail_str(self):
        expected = (
            "Maintenance Detail - Replaced toner cartridge and cleaned print heads"
        )
        self.assertEqual(str(self.service_detail), expected)
