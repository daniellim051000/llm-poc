from rest_framework import serializers

from .models import (
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


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class ItemGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemGroup
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    item_group_name = serializers.CharField(source="item_group.name", read_only=True)
    price_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "model",
            "brand",
            "item_group",
            "item_group_name",
            "price",
            "price_formatted",
        ]

    def get_price_formatted(self, obj):
        return f"RM {obj.price:.2f}"


class InvoiceDetailSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_brand = serializers.CharField(source="item.brand", read_only=True)
    item_model = serializers.CharField(source="item.model", read_only=True)
    unit_price_formatted = serializers.SerializerMethodField()
    total_price_formatted = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceDetail
        fields = [
            "id",
            "item",
            "item_name",
            "item_brand",
            "item_model",
            "quantity",
            "unit_price",
            "unit_price_formatted",
            "total_price",
            "total_price_formatted",
        ]

    def get_unit_price_formatted(self, obj):
        return f"RM {obj.unit_price:.2f}"

    def get_total_price_formatted(self, obj):
        return f"RM {obj.total_price:.2f}"


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    details = InvoiceDetailSerializer(many=True, read_only=True)
    total_amount_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "invoice_number",
            "customer",
            "customer_name",
            "invoice_date",
            "total_amount",
            "total_amount_formatted",
            "status",
            "details",
        ]

    def get_total_amount_formatted(self, obj):
        return f"RM {obj.total_amount:.2f}"


class SerialSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    item_brand = serializers.CharField(source="item.brand", read_only=True)
    item_model = serializers.CharField(source="item.model", read_only=True)

    class Meta:
        model = Serial
        fields = [
            "id",
            "serial_number",
            "item",
            "item_name",
            "item_brand",
            "item_model",
            "status",
            "manufactured_date",
            "warranty_end_date",
        ]


class ContactDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetail
        fields = "__all__"


class ContractSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    contact_details = ContactDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = [
            "id",
            "contract_number",
            "customer",
            "customer_name",
            "start_date",
            "end_date",
            "contract_type",
            "status",
            "terms",
            "contact_details",
        ]


class ServiceDetailSerializer(serializers.ModelSerializer):
    serial_number = serializers.CharField(source="serial.serial_number", read_only=True)
    cost_formatted = serializers.SerializerMethodField()

    class Meta:
        model = ServiceDetail
        fields = [
            "id",
            "serial",
            "serial_number",
            "description",
            "parts_used",
            "labor_hours",
            "cost",
            "cost_formatted",
        ]

    def get_cost_formatted(self, obj):
        return f"RM {obj.cost:.2f}"


class ServiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.name", read_only=True)
    details = ServiceDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "service_name",
            "customer",
            "customer_name",
            "service_date",
            "technician",
            "status",
            "notes",
            "details",
        ]
