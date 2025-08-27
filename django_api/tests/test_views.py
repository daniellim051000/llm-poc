from datetime import date, timedelta
from decimal import Decimal

from api.models import (
    Contract,
    Customer,
    Invoice,
    Item,
    ItemGroup,
    Serial,
    Service,
)
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CustomerViewSetTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            name="Test Company", email="test@company.com", phone="123-456-7890"
        )
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item = Item.objects.create(
            name="Printer", item_group=self.item_group, price=Decimal("500.00")
        )

    def test_customer_list(self):
        url = reverse("customer-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Company")

    def test_customer_detail(self):
        url = reverse("customer-detail", kwargs={"pk": self.customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Test Company")
        self.assertEqual(response.data["email"], "test@company.com")

    def test_customer_invoices_action(self):
        # Create an invoice for the customer
        invoice = Invoice.objects.create(
            invoice_number="INV-001",
            customer=self.customer,
            invoice_date=date.today(),
            total_amount=Decimal("500.00"),
        )

        url = reverse("customer-invoices", kwargs={"pk": self.customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["invoice_number"], "INV-001")

    def test_customer_contracts_action(self):
        # Create a contract for the customer
        contract = Contract.objects.create(
            contract_number="CON-001",
            customer=self.customer,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            contract_type="SLA",
        )

        url = reverse("customer-contracts", kwargs={"pk": self.customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["contract_number"], "CON-001")

    def test_customer_services_action(self):
        # Create a service for the customer
        service = Service.objects.create(
            service_name="Maintenance",
            customer=self.customer,
            service_date=date.today(),
        )

        url = reverse("customer-services", kwargs={"pk": self.customer.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["service_name"], "Maintenance")

    def test_customer_create(self):
        url = reverse("customer-list")
        data = {
            "name": "New Company",
            "email": "new@company.com",
            "phone": "987-654-3210",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 2)

    def test_customer_update(self):
        url = reverse("customer-detail", kwargs={"pk": self.customer.pk})
        data = {
            "name": "Updated Company",
            "email": "updated@company.com",
            "phone": "123-456-7890",
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, "Updated Company")


class InvoiceViewSetTest(APITestCase):
    def setUp(self):
        self.customer1 = Customer.objects.create(name="Company A")
        self.customer2 = Customer.objects.create(name="Company B")
        self.invoice1 = Invoice.objects.create(
            invoice_number="INV-001",
            customer=self.customer1,
            invoice_date=date.today(),
            total_amount=Decimal("1000.00"),
        )
        self.invoice2 = Invoice.objects.create(
            invoice_number="INV-002",
            customer=self.customer2,
            invoice_date=date.today(),
            total_amount=Decimal("2000.00"),
        )

    def test_invoice_list(self):
        url = reverse("invoice-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_invoice_by_customer_action(self):
        url = reverse("invoice-by-customer")
        response = self.client.get(url, {"customer_name": "Company A"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["customer_name"], "Company A")

    def test_invoice_by_customer_no_param(self):
        url = reverse("invoice-by-customer")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_invoice_by_customer_partial_match(self):
        url = reverse("invoice-by-customer")
        response = self.client.get(url, {"customer_name": "Company"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class ItemViewSetTest(APITestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item1 = Item.objects.create(
            name="Color Printer",
            model="P3000",
            brand="Ricoh",
            item_group=self.item_group,
            price=Decimal("1500.00"),
        )
        self.item2 = Item.objects.create(
            name="Scanner",
            model="S200",
            brand="Canon",
            item_group=self.item_group,
            price=Decimal("800.00"),
        )

    def test_item_list(self):
        url = reverse("item-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_item_search_by_name(self):
        url = reverse("item-search")
        response = self.client.get(url, {"q": "Printer"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Color Printer")

    def test_item_search_by_brand(self):
        url = reverse("item-search")
        response = self.client.get(url, {"brand": "Canon"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["brand"], "Canon")

    def test_item_search_by_model(self):
        url = reverse("item-search")
        response = self.client.get(url, {"q": "P3000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["model"], "P3000")

    def test_item_search_no_results(self):
        url = reverse("item-search")
        response = self.client.get(url, {"q": "Nonexistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class ContractViewSetTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.active_contract = Contract.objects.create(
            contract_number="CON-001",
            customer=self.customer,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            contract_type="SLA",
            status="active",
        )
        self.inactive_contract = Contract.objects.create(
            contract_number="CON-002",
            customer=self.customer,
            start_date=date.today() - timedelta(days=730),
            end_date=date.today() - timedelta(days=365),
            contract_type="Maintenance",
            status="expired",
        )

    def test_contract_list(self):
        url = reverse("contract-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_contract_active_action(self):
        url = reverse("contract-active")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "active")
        self.assertEqual(response.data[0]["contract_number"], "CON-001")


class SerialViewSetTest(APITestCase):
    def setUp(self):
        self.item_group = ItemGroup.objects.create(name="Office Equipment")
        self.item1 = Item.objects.create(name="Printer", item_group=self.item_group)
        self.item2 = Item.objects.create(name="Scanner", item_group=self.item_group)
        self.serial1 = Serial.objects.create(
            serial_number="SN123456789", item=self.item1, status="active"
        )
        self.serial2 = Serial.objects.create(
            serial_number="SN987654321", item=self.item2, status="active"
        )

    def test_serial_list(self):
        url = reverse("serial-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_serial_by_item_action(self):
        url = reverse("serial-by-item")
        response = self.client.get(url, {"item_id": self.item1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["serial_number"], "SN123456789")

    def test_serial_by_item_no_param(self):
        url = reverse("serial-by-item")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class ServiceViewSetTest(APITestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Company")
        self.service1 = Service.objects.create(
            service_name="Maintenance",
            customer=self.customer,
            service_date=date.today(),
            status="completed",
        )
        self.service2 = Service.objects.create(
            service_name="Repair",
            customer=self.customer,
            service_date=date.today() - timedelta(days=30),
            status="completed",
        )

    def test_service_list(self):
        url = reverse("service-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_service_by_date_range_start(self):
        url = reverse("service-by-date-range")
        start_date = date.today().strftime("%Y-%m-%d")
        response = self.client.get(url, {"start_date": start_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_service_by_date_range_end(self):
        url = reverse("service-by-date-range")
        end_date = (date.today() - timedelta(days=15)).strftime("%Y-%m-%d")
        response = self.client.get(url, {"end_date": end_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_service_by_date_range_both(self):
        url = reverse("service-by-date-range")
        start_date = (date.today() - timedelta(days=45)).strftime("%Y-%m-%d")
        end_date = date.today().strftime("%Y-%m-%d")
        response = self.client.get(
            url, {"start_date": start_date, "end_date": end_date}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
