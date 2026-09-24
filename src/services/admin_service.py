"""
Admin Service for platform governance, NGO approvals, donor management, and platform analytics.
"""

from django.db.models import Count, Sum
from src.models import (
    Donor,
    NGO,
    Donation,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
    Notification,
)
from src.services.notification_service import create_notification


def get_admin_dashboard_stats() -> dict:
    """Calculates platform-wide KPIs for the Administrator dashboard."""
    total_donors = Donor.objects.count()
    active_donors = Donor.objects.filter(status_active=True).count()

    total_ngos = NGO.objects.count()
    pending_ngos = NGO.objects.filter(status="Pending").count()
    approved_ngos = NGO.objects.filter(status="Approved").count()
    rejected_ngos = NGO.objects.filter(status="Rejected").count()

    total_donations = Donation.objects.count()
    total_items = Donation.objects.aggregate(sum_qty=Sum("quantity"))["sum_qty"] or 0
    pending_donations = Donation.objects.filter(status="Pending").count()
    accepted_donations = Donation.objects.filter(status="Accepted").count()
    collected_donations = Donation.objects.filter(status="Collected").count()

    total_allocations = DonationAllocation.objects.count()
    total_pickups = PickupRequest.objects.count()
    pending_pickups = PickupRequest.objects.filter(status="Pending").count()
    completed_pickups = PickupRequest.objects.filter(status="Delivered").count()

    total_requirements = NGORequirement.objects.count()
    active_requirements = NGORequirement.objects.filter(is_active=True).count()

    return {
        "total_donors": total_donors,
        "active_donors": active_donors,
        "total_ngos": total_ngos,
        "pending_ngos": pending_ngos,
        "approved_ngos": approved_ngos,
        "rejected_ngos": rejected_ngos,
        "total_donations": total_donations,
        "total_items": total_items,
        "pending_donations": pending_donations,
        "accepted_donations": accepted_donations,
        "collected_donations": collected_donations,
        "total_allocations": total_allocations,
        "total_pickups": total_pickups,
        "pending_pickups": pending_pickups,
        "completed_pickups": completed_pickups,
        "total_requirements": total_requirements,
        "active_requirements": active_requirements,
    }


def approve_ngo(ngo_id: int) -> tuple[bool, str]:
    """Approves a registered NGO, allowing them to participate on the platform."""
    try:
        ngo = NGO.objects.get(id=ngo_id)
    except NGO.DoesNotExist:
        return False, "NGO not found."

    ngo.status = "Approved"
    ngo.save()

    create_notification(
        recipient=ngo,
        title="NGO Application Approved!",
        message="Congratulations! Your NGO registration has been verified and approved by the platform administrator.",
        notification_type="DONATION_APPROVED",
    )
    return True, f"NGO '{ngo.ngo_name}' approved successfully!"


def reject_ngo(ngo_id: int) -> tuple[bool, str]:
    """Rejects an NGO registration."""
    try:
        ngo = NGO.objects.get(id=ngo_id)
    except NGO.DoesNotExist:
        return False, "NGO not found."

    ngo.status = "Rejected"
    ngo.save()

    create_notification(
        recipient=ngo,
        title="NGO Application Status",
        message="Your NGO application could not be approved at this time. Please contact support.",
        notification_type="DONATION_REJECTED",
    )
    return True, f"NGO '{ngo.ngo_name}' application marked as Rejected."


def toggle_donor_status(donor_id: int) -> tuple[bool, str, bool]:
    """Toggles a donor's active status."""
    try:
        donor = Donor.objects.get(id=donor_id)
    except Donor.DoesNotExist:
        return False, "Donor not found.", False

    donor.status_active = not donor.status_active
    donor.save()
    state_str = "Activated" if donor.status_active else "Deactivated"
    return True, f"Donor '{donor.name}' has been {state_str}.", donor.status_active
