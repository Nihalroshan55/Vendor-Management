from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendorViewSet , PurchaseOrderViewSet,HistoricalPerformanceViewSet


router = DefaultRouter()
router.register(r'vendors', VendorViewSet, basename='vendor')
router.register(r'purchase_orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'HistoricalPerformance', HistoricalPerformanceViewSet, basename='HistoricalPerformance')

urlpatterns = [
    path('', include(router.urls)),
]