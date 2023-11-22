from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import PurchaseOrder, Vendor

@receiver(post_save, sender=PurchaseOrder)
@receiver(pre_delete, sender=PurchaseOrder)
def update_vendor_performance(sender, instance, **kwargs):
    # Update vendor performance metrics when a related Purchase Order is saved or deleted
    vendor = instance.vendor
    vendor.historicalperformance_set.update_vendor_performance(vendor)