from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ItemGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    item_group = models.ForeignKey(ItemGroup, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.model})"


class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.customer.name}"


class InvoiceDetail(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="details"
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.item.name}"


class Serial(models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="active")
    manufactured_date = models.DateField(blank=True, null=True)
    warranty_end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.serial_number} ({self.item.name})"


class Contract(models.Model):
    contract_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    contract_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default="active")
    terms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Contract {self.contract_number} - {self.customer.name}"


class ContactDetail(models.Model):
    contract = models.ForeignKey(
        Contract, on_delete=models.CASCADE, related_name="contact_details"
    )
    contact_person = models.CharField(max_length=200)
    role = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.contact_person} ({self.contract.contract_number})"


class Service(models.Model):
    service_name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service_date = models.DateField()
    technician = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20, default="scheduled")
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.service_name} - {self.customer.name} ({self.service_date})"


class ServiceDetail(models.Model):
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name="details"
    )
    serial = models.ForeignKey(Serial, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField()
    parts_used = models.TextField(blank=True, null=True)
    labor_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.service.service_name} Detail - {self.description[:50]}"
