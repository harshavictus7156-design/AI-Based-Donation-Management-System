from django.db import models
from django.db.models import Q

from donor.models import Donor, NGO


class NotificationQuerySet(models.QuerySet):
    def for_recipient(self, recipient):
        if isinstance(recipient, Donor):
            return self.filter(donor=recipient)

        if isinstance(recipient, NGO):
            return self.filter(ngo=recipient)

        raise TypeError(
            "Notifications can only be queried for existing Donor or NGO accounts."
        )


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        DONATION_SUBMITTED = "DONATION_SUBMITTED", "Donation submitted"
        DONATION_APPROVED = "DONATION_APPROVED", "Donation approved"
        DONATION_REJECTED = "DONATION_REJECTED", "Donation rejected"
        DONATION_COLLECTED = "DONATION_COLLECTED", "Donation collected"
        DONATION_MATCHED = "DONATION_MATCHED", "Donation matched"
        REQUEST_MATCHED = "REQUEST_MATCHED", "Requirement matched"
        RESOURCE_ALLOCATED = "RESOURCE_ALLOCATED", "Resource allocated"
        PICKUP_CREATED = "PICKUP_CREATED", "Pickup created"
        PICKUP_CONFIRMED = "PICKUP_CONFIRMED", "Pickup confirmed"
        PICKUP_DISPATCHED = "PICKUP_DISPATCHED", "Pickup dispatched"
        DONATION_DELIVERED = "DONATION_DELIVERED", "Donation delivered"
        PICKUP_CANCELLED = "PICKUP_CANCELLED", "Pickup cancelled"

    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )
    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
    )

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # A stable key makes workflow notifications idempotent when a client
    # repeats a request (for example, reopening the AI match endpoint).
    event_key = models.CharField(max_length=255, blank=True, null=True)

    objects = NotificationQuerySet.as_manager()

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["donor", "is_read", "-created_at"],
                name="notif_donor_read_created_idx",
            ),
            models.Index(
                fields=["ngo", "is_read", "-created_at"],
                name="notif_ngo_read_created_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(donor__isnull=False, ngo__isnull=True)
                    | Q(donor__isnull=True, ngo__isnull=False)
                ),
                name="notification_exactly_one_recipient",
            ),
            models.UniqueConstraint(
                fields=["donor", "event_key"],
                condition=Q(donor__isnull=False, event_key__isnull=False),
                name="notification_donor_event_key_uniq",
            ),
            models.UniqueConstraint(
                fields=["ngo", "event_key"],
                condition=Q(ngo__isnull=False, event_key__isnull=False),
                name="notification_ngo_event_key_uniq",
            ),
        ]

    @classmethod
    def recipient_kwargs(cls, recipient):
        if isinstance(recipient, Donor):
            return {"donor": recipient}

        if isinstance(recipient, NGO):
            return {"ngo": recipient}

        raise TypeError(
            "Notifications can only be sent to existing Donor or NGO accounts."
        )

    @property
    def recipient(self):
        return self.donor or self.ngo

    def __str__(self):
        return f"{self.get_notification_type_display()}: {self.title}"
