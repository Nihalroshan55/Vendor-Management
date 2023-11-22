from django.db import models
from django.db.models import Count, Avg
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_positive(value):
    if value < 0:
        raise ValidationError("Value must be non-negative.")
     
class Vendor(models.Model):
    name = models.CharField(max_length=255)
    contact_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def clean(self):
        if self.on_time_delivery_rate > 100 or self.quality_rating_avg > 100 or self.fulfillment_rate > 100:
            raise ValidationError("Percentage values cannot exceed 100%.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure clean() is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField()
    items = models.JSONField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=50)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgment_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.delivery_date < self.order_date:
            raise ValidationError("Delivery date must be equal to or after the order date.")

        if self.acknowledgment_date and self.acknowledgment_date < self.issue_date:
            raise ValidationError("Acknowledgment date must be equal to or after the issue date.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Ensure clean() is called before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_number} - {self.vendor.name}"

class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    average_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()
    
    @classmethod
    def update_vendor_performance(cls, vendor):
        # Calculate and update on-time delivery rate
        completed_orders = PurchaseOrder.objects.filter(vendor=vendor, status='completed')
        total_completed_orders = completed_orders.count()
        on_time_delivery_orders = completed_orders.filter(delivery_date__lte=models.F('acknowledgment_date'))
        on_time_delivery_rate = (on_time_delivery_orders.count() / total_completed_orders) * 100 if total_completed_orders > 0 else 0
        vendor.on_time_delivery_rate = on_time_delivery_rate

        # Calculate and update quality rating average
        quality_ratings = completed_orders.exclude(quality_rating__isnull=True).aggregate(quality_rating_avg=Avg('quality_rating'))
        vendor.quality_rating_avg = quality_ratings['quality_rating_avg'] if quality_ratings['quality_rating_avg'] is not None else 0.0

        # Calculate and update average response time
        response_times = completed_orders.exclude(acknowledgment_date__isnull=True).aggregate(avg_response_time=Avg(models.F('acknowledgment_date') - models.F('issue_date')))
        vendor.average_response_time = response_times['avg_response_time'].total_seconds() / 3600 if response_times['avg_response_time'] is not None else 0.0

        # Calculate and update fulfillment rate
        fulfilled_orders = completed_orders.filter(status='completed')
        fulfillment_rate = (fulfilled_orders.count() / total_completed_orders) * 100 if total_completed_orders > 0 else 0
        vendor.fulfillment_rate = fulfillment_rate

        # Save the updated vendor metrics
        vendor.save()

    @classmethod
    def record_historical_performance(cls, vendor):
        # Record historical performance data
        historical_performance = HistoricalPerformance(
            vendor=vendor,
            date=models.DateTimeField.now(),
            on_time_delivery_rate=vendor.on_time_delivery_rate,
            quality_rating_avg=vendor.quality_rating_avg,
            average_response_time=vendor.average_response_time,
            fulfillment_rate=vendor.fulfillment_rate
        )
        historical_performance.save()

    def __str__(self):
        return f"{self.vendor.name} - {self.date}"
