"""Reusable creation helpers for in-app workflow notifications."""

from django.db import IntegrityError, transaction

from donor.models import Donor, NGO

from .models import Notification


def _recipient_label(recipient):
    if isinstance(recipient, Donor):
        return recipient.name
    if isinstance(recipient, NGO):
        return recipient.ngo_name
    raise TypeError("Notifications can only be sent to existing Donor or NGO accounts.")


def create_notification(
    *,
    recipient,
    title,
    message,
    notification_type,
    event_key=None,
):
    """Create a notification, safely deduplicating stable workflow events."""
    _recipient_label(recipient)
    recipient_kwargs = Notification.recipient_kwargs(recipient)

    if not event_key:
        return Notification.objects.create(
            **recipient_kwargs,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    try:
        with transaction.atomic():
            notification, _ = Notification.objects.get_or_create(
                **recipient_kwargs,
                event_key=event_key,
                defaults={
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                },
            )
    except IntegrityError:
        # A concurrent request may have created the same event after the
        # initial lookup; return that canonical notification instead.
        notification = Notification.objects.for_recipient(recipient).get(
            event_key=event_key
        )

    return notification


def notify_donation_submitted(donation):
    return create_notification(
        recipient=donation.donor,
        title="Donation submitted",
        message=f"Your donation of {donation.quantity} {donation.item_name} has been submitted.",
        notification_type=Notification.NotificationType.DONATION_SUBMITTED,
        event_key=f"donation:{donation.id}:submitted",
    )


def notify_donation_approved(donation):
    return create_notification(
        recipient=donation.donor,
        title="Donation approved",
        message="An NGO has approved your donation. You can now proceed with the pickup process.",
        notification_type=Notification.NotificationType.DONATION_APPROVED,
        event_key=f"donation:{donation.id}:approved",
    )


def notify_donation_rejected(donation):
    return create_notification(
        recipient=donation.donor,
        title="Donation rejected",
        message="An NGO could not accept your donation at this time.",
        notification_type=Notification.NotificationType.DONATION_REJECTED,
        event_key=f"donation:{donation.id}:rejected",
    )


def notify_donation_collected(donation):
    return create_notification(
        recipient=donation.donor,
        title="Donation collected",
        message="Your donation has been marked as collected.",
        notification_type=Notification.NotificationType.DONATION_COLLECTED,
        event_key=f"donation:{donation.id}:collected",
    )


def notify_ai_match(donation, requirement):
    ngo = requirement.ngo
    donor_result = create_notification(
        recipient=donation.donor,
        title="Donation match found",
        message=(
            f"AI found a match for your {donation.item_name} donation with "
            f"{ngo.ngo_name}."
        ),
        notification_type=Notification.NotificationType.DONATION_MATCHED,
        event_key=f"donation:{donation.id}:ai-match:{requirement.id}:donor",
    )
    ngo_result = create_notification(
        recipient=ngo,
        title="Requirement match found",
        message=(
            f"A donor's {donation.item_name} donation matches your "
            f"requirement for {requirement.item_name}."
        ),
        notification_type=Notification.NotificationType.REQUEST_MATCHED,
        event_key=f"donation:{donation.id}:ai-match:{requirement.id}:ngo",
    )
    return donor_result, ngo_result


def notify_allocation_created(allocation):
    donation = allocation.donation
    donor_result = create_notification(
        recipient=donation.donor,
        title="Donation allocated",
        message=(
            f"{allocation.allocated_quantity} {donation.item_name} has been "
            f"allocated to {allocation.ngo.ngo_name}."
        ),
        notification_type=Notification.NotificationType.RESOURCE_ALLOCATED,
        event_key=f"allocation:{allocation.id}:donor",
    )
    ngo_result = create_notification(
        recipient=allocation.ngo,
        title="Donation allocated to your requirement",
        message=(
            f"{allocation.allocated_quantity} {donation.item_name} has been "
            "allocated to one of your requirements."
        ),
        notification_type=Notification.NotificationType.RESOURCE_ALLOCATED,
        event_key=f"allocation:{allocation.id}:ngo",
    )
    return donor_result, ngo_result


def notify_pickup_created(pickup):
    allocation = pickup.allocation
    return create_notification(
        recipient=allocation.ngo,
        title="Pickup scheduled",
        message=(
            f"A pickup for {allocation.donation.item_name} has been scheduled "
            f"for {pickup.scheduled_time}."
        ),
        notification_type=Notification.NotificationType.PICKUP_CREATED,
        event_key=f"pickup:{pickup.id}:created:ngo",
    )


def notify_pickup_status_changed(pickup, *, changed_by):
    """Notify the non-acting party when a real pickup status changes."""
    allocation = pickup.allocation
    donation = allocation.donation

    status_map = {
        "Confirmed": (
            Notification.NotificationType.PICKUP_CONFIRMED,
            "Pickup confirmed",
            "Your pickup has been confirmed by the NGO.",
        ),
        "Dispatched": (
            Notification.NotificationType.PICKUP_DISPATCHED,
            "Pickup dispatched",
            "Your donation pickup is now dispatched.",
        ),
        "Delivered": (
            Notification.NotificationType.DONATION_DELIVERED,
            "Donation delivered",
            "Your donation has been delivered to the NGO.",
        ),
        "Cancelled": (
            Notification.NotificationType.PICKUP_CANCELLED,
            "Pickup cancelled",
            "The pickup for your donation has been cancelled.",
        ),
    }

    notification_type, title, message = status_map[pickup.status]
    recipient = allocation.ngo if changed_by == "Donor" else donation.donor

    return create_notification(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        event_key=f"pickup:{pickup.id}:{pickup.status.lower()}:{changed_by.lower()}",
    )
