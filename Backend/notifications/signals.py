from django.db.models.signals import post_save
from django.dispatch import receiver

from donor.models import Donation

from .services import notify_donation_collected


@receiver(post_save, sender=Donation)
def notify_when_donation_is_collected(sender, instance, created, **kwargs):
    # The current application has no API that sets Collected, but it is an
    # existing Donation status and can be changed through the existing admin
    # or other backend callers. The stable event key prevents repeat alerts.
    if not created and instance.status == "Collected":
        notify_donation_collected(instance)
