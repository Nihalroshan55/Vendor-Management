from rest_framework import viewsets, permissions,status
from django.core.exceptions import ValidationError
from api.models import Vendor,PurchaseOrder,HistoricalPerformance
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers import VendorSerializer,PurchaseOrderSerializer,HistoricalPerformanceSerializer



class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes=[permissions.AllowAny]
    
    
    
    
    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        vendor = self.get_object()
        print("Data to be saved:", vendor.__dict__)
        serializer = HistoricalPerformanceSerializer(vendor.historicalperformance_set.all(), many=True)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            errors_dict = dict(e)
            error_messages = self.get_error_messages(errors_dict)
            return Response({"error": error_messages}, status=status.HTTP_400_BAD_REQUEST)

    # def get_error_messages(self, errors_dict):
    #     error_messages = []
    #     for field, field_errors in errors_dict.items():
    #         if field == 'on_time_delivery_rate':
    #             error_messages.append("Invalid value for on-time delivery rate. Please ensure it is between 0 and 100.")
    #         elif field == 'quality_rating_avg':
    #             error_messages.append("Invalid value for quality rating average. Please ensure it is between 0 and 100.")
    #         elif field == 'average_response_time':
    #             error_messages.append("Invalid value for average response time. Please ensure it is between 0 and 100.")
    #         elif field == 'fulfillment_rate':
    #             error_messages.append("Invalid value for fulfillment rate. Please ensure it is between 0 and 100.")
    #         else:
    #             # Default error message for other fields
    #             error_messages.append("Invalid data. Please check the provided values.")
    #     return error_messages
   
    
    
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes=[permissions.AllowAny]
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
    permission_classes=[permissions.AllowAny]
