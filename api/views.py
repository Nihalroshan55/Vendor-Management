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


class HistoricalPerformanceViewSet(viewsets.ModelViewSet):
    queryset = HistoricalPerformance.objects.all()
    serializer_class = HistoricalPerformanceSerializer
