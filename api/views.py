from rest_framework import viewsets
from api.models import Vendor,PurchaseOrder,HistoricalPerformance
from api.serializers import VendorSerializer,PurchaseOrderSerializer,HistoricalPerformanceSerializer

class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        vendor = self.get_object()
        serializer = HistoricalPerformanceSerializer(vendor.historicalperformance_set.all(), many=True)
        return Response(serializer.data)
    
    
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        purchase_order = self.get_object()
        purchase_order.acknowledgment_date = models.DateTimeField.now()
        purchase_order.save()
        purchase_order.vendor.historicalperformance_set.update_vendor_performance(purchase_order.vendor)
        return Response({"detail": "Acknowledgment recorded successfully."}, status=status.HTTP_200_OK)

class HistoricalPerformanceViewSet(viewsets.ModelViewSet):
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
