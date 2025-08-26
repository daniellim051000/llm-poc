from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ContractViewSet,
    CustomerViewSet,
    InvoiceViewSet,
    ItemViewSet,
    SerialViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"items", ItemViewSet)
router.register(r"invoices", InvoiceViewSet)
router.register(r"contracts", ContractViewSet)
router.register(r"serials", SerialViewSet)
router.register(r"services", ServiceViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]
