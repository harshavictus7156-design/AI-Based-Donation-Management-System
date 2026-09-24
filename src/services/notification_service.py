"""
Notification Service for in-app alert events across Donors and NGOs.
"""

from src.models import Notification, Donor, NGO


def create_notification(
    recipient,
    title: str,
    message: str,
    notification_type: str = "DONATION_SUBMITTED",
    event_key: str = None,
):
    """Creates a notification for either a Donor or an NGO."""
    kwargs = {}
    if isinstance(recipient, Donor):
        kwargs["donor"] = recipient
    elif isinstance(recipient, NGO):
        kwargs["ngo"] = recipient
    elif isinstance(recipient, int):
        donor = Donor.objects.filter(id=recipient).first()
        if donor:
            kwargs["donor"] = donor
        else:
            ngo = NGO.objects.filter(id=recipient).first()
            if ngo:
                kwargs["ngo"] = ngo
            else:
                return None
    else:
        return None

    try:
        if event_key:
            notif, _ = Notification.objects.get_or_create(
                event_key=event_key,
                defaults={
                    **kwargs,
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                },
            )
            return notif
        return Notification.objects.create(
            **kwargs,
            title=title,
            message=message,
            notification_type=notification_type,
        )
    except Exception as e:
        print(f"Error creating notification: {e}")
        return None


def get_user_notifications(user_dict: dict) -> list[Notification]:
    """Fetches all notifications for the given user (Donor or NGO)."""
    if not user_dict:
        return []
    role = user_dict.get("role")
    user_id = user_dict.get("id")
    
    if role == "Donor":
        return list(Notification.objects.filter(donor_id=user_id).order_by("-created_at")[:50])
    elif role == "NGO":
        return list(Notification.objects.filter(ngo_id=user_id).order_by("-created_at")[:50])
    elif role == "Admin":
        return list(Notification.objects.all().order_by("-created_at")[:50])
    return []


def get_unread_count(user_dict: dict) -> int:
    """Returns the unread notifications count."""
    if not user_dict:
        return 0
    role = user_dict.get("role")
    user_id = user_dict.get("id")
    
    if role == "Donor":
        return Notification.objects.filter(donor_id=user_id, is_read=False).count()
    elif role == "NGO":
        return Notification.objects.filter(ngo_id=user_id, is_read=False).count()
    elif role == "Admin":
        return Notification.objects.filter(is_read=False).count()
    return 0


def mark_notification_read(notification_id: int):
    """Marks a single notification as read."""
    Notification.objects.filter(id=notification_id).update(is_read=True)


def mark_all_read(user_dict: dict):
    """Marks all notifications as read for the user."""
    if not user_dict:
        return
    role = user_dict.get("role")
    user_id = user_dict.get("id")
    
    if role == "Donor":
        Notification.objects.filter(donor_id=user_id, is_read=False).update(is_read=True)
    elif role == "NGO":
        Notification.objects.filter(ngo_id=user_id, is_read=False).update(is_read=True)
    elif role == "Admin":
        Notification.objects.filter(is_read=False).update(is_read=True)


def delete_notification(notification_id: int):
    """Deletes a notification by ID."""
    Notification.objects.filter(id=notification_id).delete()
