from django.db.models import Q
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Contract, Customer, Invoice, Item, Serial, Service
from .serializers import (
    ContractSerializer,
    CustomerSerializer,
    InvoiceSerializer,
    ItemSerializer,
    SerialSerializer,
    ServiceSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=True, methods=["get"])
    def invoices(self, request, pk=None):
        customer = self.get_object()
        invoices = Invoice.objects.filter(customer=customer)
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def contracts(self, request, pk=None):
        customer = self.get_object()
        contracts = Contract.objects.filter(customer=customer)
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def services(self, request, pk=None):
        customer = self.get_object()
        services = Service.objects.filter(customer=customer)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = (
        Invoice.objects.all()
        .select_related("customer")
        .prefetch_related("details__item")
    )
    serializer_class = InvoiceSerializer

    @action(detail=False, methods=["get"])
    def by_customer(self, request):
        customer_name = request.query_params.get("customer_name", "")
        if customer_name:
            invoices = self.queryset.filter(customer__name__icontains=customer_name)
            serializer = self.get_serializer(invoices, many=True)
            return Response(serializer.data)
        return Response({"error": "customer_name parameter required"}, status=400)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().select_related("item_group")
    serializer_class = ItemSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        brand = request.query_params.get("brand", "")

        queryset = self.queryset
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(model__icontains=query)
                | Q(brand__icontains=query)
            )
        if brand:
            queryset = queryset.filter(brand__icontains=brand)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = (
        Contract.objects.all()
        .select_related("customer")
        .prefetch_related("contact_details")
    )
    serializer_class = ContractSerializer

    @action(detail=False, methods=["get"])
    def active(self, request):
        contracts = self.queryset.filter(status="active")
        serializer = self.get_serializer(contracts, many=True)
        return Response(serializer.data)


class SerialViewSet(viewsets.ModelViewSet):
    queryset = Serial.objects.all().select_related("item")
    serializer_class = SerialSerializer

    @action(detail=False, methods=["get"])
    def by_item(self, request):
        item_id = request.query_params.get("item_id", "")
        if item_id:
            serials = self.queryset.filter(item_id=item_id)
            serializer = self.get_serializer(serials, many=True)
            return Response(serializer.data)
        return Response({"error": "item_id parameter required"}, status=400)


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = (
        Service.objects.all()
        .select_related("customer")
        .prefetch_related("details__serial")
    )
    serializer_class = ServiceSerializer

    @action(detail=False, methods=["get"])
    def by_date_range(self, request):
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = self.queryset
        if start_date:
            queryset = queryset.filter(service_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(service_date__lte=end_date)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def health_check(request):
    """Health check endpoint for Docker container monitoring"""
    return JsonResponse({"status": "healthy", "service": "django-api"})
