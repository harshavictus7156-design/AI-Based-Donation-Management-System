"""
Donation Service handling Donation CRUD, allocations, and pickup requests.
"""

from django.db import transaction
from src.models import (
    Donation,
    Donor,
    NGO,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
)
from src.services.notification_service import create_notification


def create_donation(
    donor_id: int,
    item_name: str,
    category: str,
    quantity: int,
    condition: str,
    description: str,
    location: str,
    image_path: str = None,
    ngo_id: int = None,
    pickup_date = None,
    pickup_time: str = None,
    pickup_notes: str = "",
) -> tuple[bool, str, Donation]:
    """Creates a new donation record with optional allocation and pickup."""
    try:
        donor = Donor.objects.get(id=donor_id)
    except Donor.DoesNotExist:
        return False, "Donor account not found.", None

    if not item_name or not item_name.strip():
        return False, "Item name is required.", None
    if quantity <= 0:
        return False, "Quantity must be greater than 0.", None
    if not location or not location.strip():
        return False, "Pickup location is required.", None

    ngo = None
    if ngo_id:
        ngo = NGO.objects.filter(id=ngo_id, status="Approved").first()

    with transaction.atomic():
        donation = Donation.objects.create(
            donor=donor,
            ngo=ngo,
            item_name=item_name.strip(),
            category=category,
            quantity=quantity,
            condition=condition,
            description=description.strip(),
            location=location.strip(),
            item_image=image_path if image_path else None,
            status="Pending",
            pickup_date=pickup_date,
            pickup_time=pickup_time,
            pickup_status="Scheduled" if pickup_date else "Not Scheduled",
        )

        # Notify donor
        create_notification(
            recipient=donor,
            title="Donation submitted",
            message=f"Your donation of {quantity} {item_name} has been submitted successfully.",
            notification_type="DONATION_SUBMITTED",
            event_key=f"donation:{donation.id}:submitted",
        )

        # If an NGO was chosen directly, create an allocation
        if ngo:
            allocation = DonationAllocation.objects.create(
                donation=donation,
                ngo=ngo,
                allocated_quantity=quantity,
                status="Pending",
                pickup_date=pickup_date,
                pickup_time=pickup_time,
                pickup_status="Scheduled" if pickup_date else "Not Scheduled",
            )
            # Create pickup request if pickup details provided
            if pickup_date:
                import datetime
                try:
                    dt = datetime.datetime.combine(pickup_date, datetime.time(10, 0))
                except Exception:
                    dt = datetime.datetime.now()
                PickupRequest.objects.create(
                    allocation=allocation,
                    pickup_address=location.strip(),
                    scheduled_time=dt,
                    notes=pickup_notes.strip(),
                    status="Pending",
                )
            # Notify NGO
            create_notification(
                recipient=ngo,
                title="Incoming Donation Allocation",
                message=f"A donor has allocated {quantity} {item_name} to your organization.",
                notification_type="RESOURCE_ALLOCATED",
                event_key=f"allocation:{allocation.id}:ngo",
            )

    return True, "Donation created successfully!", donation


def update_donation(
    donation_id: int,
    donor_id: int,
    item_name: str,
    category: str,
    quantity: int,
    condition: str,
    description: str,
    location: str,
) -> tuple[bool, str]:
    """Updates an existing donation if it is in Pending status."""
    try:
        donation = Donation.objects.get(id=donation_id, donor_id=donor_id)
    except Donation.DoesNotExist:
        return False, "Donation not found."

    if donation.status != "Pending":
        return False, f"Cannot edit a donation with status '{donation.status}'."

    donation.item_name = item_name.strip()
    donation.category = category
    donation.quantity = quantity
    donation.condition = condition
    donation.description = description.strip()
    donation.location = location.strip()
    donation.save()

    return True, "Donation updated successfully."


def allocate_donation(
    donation_id: int,
    donor_id: int,
    allocations_list: list[dict],
    pickup_date = None,
    pickup_time: str = None,
    pickup_notes: str = "",
) -> tuple[bool, str]:
    """
    Allocates donation quantity to NGO requirements or specific NGOs.
    allocations_list = [{"ngo_id": int, "requirement_id": int, "quantity": int}]
    """
    try:
        donation = Donation.objects.get(id=donation_id, donor_id=donor_id)
    except Donation.DoesNotExist:
        return False, "Donation not found."

    if donation.status != "Pending":
        return False, f"Cannot allocate donation in '{donation.status}' status."

    total_allocated = sum(int(a.get("quantity", 0)) for a in allocations_list)
    if total_allocated <= 0:
        return False, "Allocated quantity must be greater than 0."
    if total_allocated > donation.quantity:
        return False, f"Allocated quantity ({total_allocated}) exceeds donated quantity ({donation.quantity})."

    with transaction.atomic():
        for alloc in allocations_list:
            ngo_id = alloc.get("ngo_id")
            req_id = alloc.get("requirement_id")
            qty = int(alloc.get("quantity", 0))
            if qty <= 0:
                continue

            ngo = NGO.objects.filter(id=ngo_id, status="Approved").first()
            if not ngo:
                continue

            req = None
            if req_id:
                req = NGORequirement.objects.filter(id=req_id, is_active=True).first()

            allocation = DonationAllocation.objects.create(
                donation=donation,
                ngo=ngo,
                requirement=req,
                allocated_quantity=qty,
                status="Pending",
                pickup_date=pickup_date,
                pickup_time=pickup_time,
                pickup_status="Scheduled" if pickup_date else "Not Scheduled",
            )

            # Update donation NGO pointer if not set
            if not donation.ngo:
                donation.ngo = ngo
                donation.save()

            # Create pickup request if scheduled
            if pickup_date:
                import datetime
                try:
                    dt = datetime.datetime.combine(pickup_date, datetime.time(10, 0))
                except Exception:
                    dt = datetime.datetime.now()
                PickupRequest.objects.create(
                    allocation=allocation,
                    pickup_address=donation.location,
                    scheduled_time=dt,
                    notes=pickup_notes,
                    status="Pending",
                )

            # Notifications
            create_notification(
                recipient=ngo,
                title="New Donation Allocation",
                message=f"{qty} {donation.item_name} has been allocated to your organization.",
                notification_type="RESOURCE_ALLOCATED",
                event_key=f"allocation:{allocation.id}:ngo",
            )
            create_notification(
                recipient=donation.donor,
                title="Donation Allocated",
                message=f"You allocated {qty} {donation.item_name} to {ngo.ngo_name}.",
                notification_type="RESOURCE_ALLOCATED",
                event_key=f"allocation:{allocation.id}:donor",
            )

    return True, "Donation successfully allocated!"


def create_or_update_pickup_request(
    allocation_id: int,
    pickup_address: str,
    scheduled_datetime,
    notes: str = "",
) -> tuple[bool, str]:
    """Creates or updates a pickup request for an allocation."""
    try:
        allocation = DonationAllocation.objects.get(id=allocation_id)
    except DonationAllocation.DoesNotExist:
        return False, "Allocation not found."

    pickup, created = PickupRequest.objects.get_or_create(
        allocation=allocation,
        defaults={
            "pickup_address": pickup_address,
            "scheduled_time": scheduled_datetime,
            "notes": notes,
            "status": "Pending",
        },
    )
    if not created:
        pickup.pickup_address = pickup_address
        pickup.scheduled_time = scheduled_datetime
        pickup.notes = notes
        pickup.status = "Pending"
        pickup.save()

    # Update allocation & donation pickup status
    allocation.pickup_status = "Scheduled"
    allocation.pickup_date = scheduled_datetime.date() if hasattr(scheduled_datetime, "date") else None
    allocation.save()

    allocation.donation.pickup_status = "Scheduled"
    allocation.donation.pickup_date = allocation.pickup_date
    allocation.donation.save()

    # Notify NGO
    create_notification(
        recipient=allocation.ngo,
        title="Pickup Scheduled",
        message=f"Donor scheduled pickup for {allocation.donation.item_name} on {allocation.pickup_date}.",
        notification_type="PICKUP_CREATED",
        event_key=f"pickup:{pickup.id}:created",
    )

    return True, "Pickup request submitted successfully!"


def cancel_pickup_request(pickup_id: int, user_dict: dict) -> tuple[bool, str]:
    """Cancels an active pickup request."""
    try:
        pickup = PickupRequest.objects.select_related("allocation__donation", "allocation__ngo").get(id=pickup_id)
    except PickupRequest.DoesNotExist:
        return False, "Pickup request not found."

    pickup.status = "Cancelled"
    pickup.save()

    allocation = pickup.allocation
    allocation.pickup_status = "Cancelled"
    allocation.save()

    donation = allocation.donation
    donation.pickup_status = "Cancelled"
    donation.save()

    # Notifications
    create_notification(
        recipient=allocation.ngo,
        title="Pickup Cancelled",
        message=f"Pickup for {donation.item_name} has been cancelled.",
        notification_type="PICKUP_CANCELLED",
    )
    create_notification(
        recipient=donation.donor,
        title="Pickup Cancelled",
        message=f"Your pickup for {donation.item_name} has been cancelled.",
        notification_type="PICKUP_CANCELLED",
    )

    return True, "Pickup request cancelled successfully."
