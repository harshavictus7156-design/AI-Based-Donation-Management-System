"""
NGO Service for NGO registration, profile management, requirement lifecycle,
incoming donation acceptance/rejection, and pickup status updates.
"""

from django.db import transaction
from django.db.models import Count, Sum, Q
from src.models import (
    NGO,
    NGORequirement,
    Donation,
    DonationAllocation,
    PickupRequest,
)
from src.auth import hash_password
from src.services.notification_service import create_notification


def register_ngo(data: dict) -> tuple[bool, str, NGO]:
    """Registers a new NGO organization account (default status: 'Pending')."""
    ngo_name = str(data.get("ngo_name", "")).strip()
    registration_no = str(data.get("registration_no", "")).strip()
    email_id = str(data.get("email_id", "")).strip().lower()
    phone_no = str(data.get("phone_no", "")).strip()
    password = str(data.get("password", "")).strip()
    description = str(data.get("description", "")).strip()
    address = str(data.get("address", "")).strip()
    city = str(data.get("city", "")).strip()
    state = str(data.get("state", "")).strip()
    pincode = str(data.get("pincode", "")).strip()
    website_link = str(data.get("website_link", "")).strip()
    language = str(data.get("language", "English")).strip()
    picture_path = data.get("picture")
    certificate_path = data.get("certificate_files")

    if not ngo_name or not registration_no or not email_id or not password:
        return False, "Organization name, registration number, email, and password are required.", None

    if NGO.objects.filter(email_id__iexact=email_id).exists():
        return False, "An NGO with this email already exists.", None

    if NGO.objects.filter(registration_no__iexact=registration_no).exists():
        return False, "An NGO with this registration number already exists.", None

    try:
        ngo = NGO.objects.create(
            ngo_name=ngo_name,
            registration_no=registration_no,
            email_id=email_id,
            phone_no=phone_no,
            password=hash_password(password),
            description=description,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            website_link=website_link,
            language=language,
            picture=picture_path if picture_path else None,
            certificate_files=certificate_path if certificate_path else None,
            status="Pending",
        )
        return True, "NGO registered successfully! Your account is pending administrator approval.", ngo
    except Exception as e:
        return False, f"NGO registration failed: {e}", None


def update_ngo_profile(ngo_id: int, data: dict) -> tuple[bool, str]:
    """Updates NGO profile details."""
    try:
        ngo = NGO.objects.get(id=ngo_id)
    except NGO.DoesNotExist:
        return False, "NGO not found."

    ngo.ngo_name = str(data.get("ngo_name", ngo.ngo_name)).strip()
    ngo.phone_no = str(data.get("phone_no", ngo.phone_no)).strip()
    ngo.website_link = str(data.get("website_link", ngo.website_link)).strip()
    ngo.description = str(data.get("description", ngo.description)).strip()
    ngo.address = str(data.get("address", ngo.address)).strip()
    ngo.city = str(data.get("city", ngo.city)).strip()
    ngo.state = str(data.get("state", ngo.state)).strip()
    ngo.pincode = str(data.get("pincode", ngo.pincode)).strip()

    if data.get("picture"):
        ngo.picture = data.get("picture")
    if data.get("certificate_files"):
        ngo.certificate_files = data.get("certificate_files")

    ngo.save()
    return True, "NGO Profile updated successfully."


def get_approved_ngos(search_query: str = "", city_filter: str = "All") -> list[NGO]:
    """Fetches approved NGOs with optional search and city filters."""
    qs = NGO.objects.filter(status="Approved").prefetch_related("requirements")

    if city_filter and city_filter != "All":
        qs = qs.filter(city__iexact=city_filter)
    if search_query and search_query.strip():
        q = search_query.strip()
        qs = qs.filter(
            Q(ngo_name__icontains=q)
            | Q(description__icontains=q)
            | Q(city__icontains=q)
            | Q(state__icontains=q)
        )

    return list(qs.order_by("ngo_name"))


def get_ngo_dashboard_stats(ngo_id: int) -> dict:
    """Calculates summary KPIs and analytics for the NGO workspace."""
    allocations = DonationAllocation.objects.filter(ngo_id=ngo_id)
    requirements = NGORequirement.objects.filter(ngo_id=ngo_id)
    pickups = PickupRequest.objects.filter(allocation__ngo_id=ngo_id)

    total_allocations = allocations.count()
    pending_allocations = allocations.filter(status="Pending").count()
    accepted_allocations = allocations.filter(status="Accepted").count()
    collected_allocations = allocations.filter(status="Collected").count()

    total_requirements = requirements.count()
    active_requirements = requirements.filter(is_active=True).count()
    fulfilled_requirements = sum(1 for r in requirements if r.is_fulfilled)

    pending_pickups = pickups.filter(status__in=["Pending", "Confirmed", "Dispatched"]).count()

    return {
        "total_allocations": total_allocations,
        "pending_allocations": pending_allocations,
        "accepted_allocations": accepted_allocations,
        "collected_allocations": collected_allocations,
        "total_requirements": total_requirements,
        "active_requirements": active_requirements,
        "fulfilled_requirements": fulfilled_requirements,
        "pending_pickups": pending_pickups,
    }


def add_requirement(
    ngo_id: int,
    item_name: str,
    category: str,
    required_quantity: int,
    priority: str = "Medium",
    description: str = "",
) -> tuple[bool, str, NGORequirement]:
    """Adds a new requirement for an NGO."""
    try:
        ngo = NGO.objects.get(id=ngo_id)
    except NGO.DoesNotExist:
        return False, "NGO not found.", None

    if ngo.status != "Approved":
        return False, "Only approved NGOs can publish resource requirements.", None

    if not item_name or not item_name.strip():
        return False, "Item name is required.", None
    if required_quantity <= 0:
        return False, "Required quantity must be greater than 0.", None

    req = NGORequirement.objects.create(
        ngo=ngo,
        item_name=item_name.strip(),
        category=category,
        required_quantity=required_quantity,
        fulfilled_quantity=0,
        priority=priority,
        description=description.strip(),
        is_active=True,
    )
    return True, "Requirement added successfully!", req


def update_requirement(
    req_id: int,
    ngo_id: int,
    item_name: str,
    category: str,
    required_quantity: int,
    priority: str,
    description: str,
    is_active: bool,
) -> tuple[bool, str]:
    """Updates an existing NGO requirement."""
    try:
        req = NGORequirement.objects.get(id=req_id, ngo_id=ngo_id)
    except NGORequirement.DoesNotExist:
        return False, "Requirement not found."

    req.item_name = item_name.strip()
    req.category = category
    req.required_quantity = max(required_quantity, req.fulfilled_quantity)
    req.priority = priority
    req.description = description.strip()
    req.is_active = is_active
    req.save()
    return True, "Requirement updated successfully."


def delete_requirement(req_id: int, ngo_id: int) -> tuple[bool, str]:
    """Deletes an NGO requirement."""
    try:
        req = NGORequirement.objects.get(id=req_id, ngo_id=ngo_id)
        req.delete()
        return True, "Requirement deleted successfully."
    except NGORequirement.DoesNotExist:
        return False, "Requirement not found."


def accept_allocation(allocation_id: int, ngo_id: int) -> tuple[bool, str]:
    """
    Accepts an incoming donation allocation.
    Updates allocation status, donation status, requirement fulfilled quantity, and dispatches notifications.
    """
    try:
        allocation = (
            DonationAllocation.objects.select_related("donation__donor", "requirement", "ngo")
            .get(id=allocation_id, ngo_id=ngo_id)
        )
    except DonationAllocation.DoesNotExist:
        return False, "Allocation not found."

    if allocation.status == "Accepted":
        return True, "Allocation is already accepted."

    with transaction.atomic():
        allocation.status = "Accepted"
        allocation.save()

        donation = allocation.donation
        donation.status = "Accepted"
        donation.save()

        # Update requirement fulfilled quantity if linked
        if allocation.requirement:
            req = allocation.requirement
            req.fulfilled_quantity = min(
                req.required_quantity,
                req.fulfilled_quantity + allocation.allocated_quantity,
            )
            req.save()

        # Notify donor
        create_notification(
            recipient=donation.donor,
            title="Donation Accepted",
            message=f"{allocation.ngo.ngo_name} has accepted your donation of {allocation.allocated_quantity} {donation.item_name}.",
            notification_type="DONATION_APPROVED",
            event_key=f"allocation:{allocation.id}:approved",
        )

    return True, "Donation allocation accepted successfully!"


def reject_allocation(allocation_id: int, ngo_id: int, reason: str = "") -> tuple[bool, str]:
    """Rejects an incoming donation allocation."""
    try:
        allocation = (
            DonationAllocation.objects.select_related("donation__donor", "ngo")
            .get(id=allocation_id, ngo_id=ngo_id)
        )
    except DonationAllocation.DoesNotExist:
        return False, "Allocation not found."

    with transaction.atomic():
        allocation.status = "Rejected"
        allocation.save()

        donation = allocation.donation
        # Check if other active allocations exist
        other_active = DonationAllocation.objects.filter(donation=donation).exclude(status="Rejected").exists()
        if not other_active:
            donation.status = "Pending"
            donation.save()

        # Notify donor
        reason_text = f" Reason: {reason}" if reason else ""
        create_notification(
            recipient=donation.donor,
            title="Donation Allocation Declined",
            message=f"{allocation.ngo.ngo_name} could not accept the allocation for {donation.item_name}.{reason_text}",
            notification_type="DONATION_REJECTED",
            event_key=f"allocation:{allocation.id}:rejected",
        )

    return True, "Allocation rejected."


def update_pickup_status(pickup_id: int, ngo_id: int, new_status: str) -> tuple[bool, str]:
    """Updates pickup lifecycle status: Confirmed, Dispatched, Delivered, Cancelled."""
    try:
        pickup = (
            PickupRequest.objects.select_related("allocation__donation__donor", "allocation__ngo")
            .get(id=pickup_id, allocation__ngo_id=ngo_id)
        )
    except PickupRequest.DoesNotExist:
        return False, "Pickup request not found."

    valid_statuses = ["Pending", "Confirmed", "Dispatched", "Delivered", "Cancelled"]
    if new_status not in valid_statuses:
        return False, "Invalid pickup status."

    with transaction.atomic():
        pickup.status = new_status
        pickup.save()

        allocation = pickup.allocation
        donation = allocation.donation

        if new_status == "Confirmed":
            allocation.pickup_status = "Confirmed"
            donation.pickup_status = "Confirmed"
            msg = f"Pickup for {donation.item_name} has been confirmed by {allocation.ngo.ngo_name}."
            notif_type = "PICKUP_CONFIRMED"
        elif new_status == "Dispatched":
            allocation.pickup_status = "Dispatched"
            donation.pickup_status = "Dispatched"
            msg = f"Pickup vehicle for {donation.item_name} has been dispatched!"
            notif_type = "PICKUP_DISPATCHED"
        elif new_status == "Delivered":
            allocation.pickup_status = "Picked Up"
            allocation.status = "Collected"
            donation.pickup_status = "Picked Up"
            donation.status = "Collected"
            msg = f"Your donation of {donation.item_name} has been successfully collected and delivered to {allocation.ngo.ngo_name}. Thank you for your contribution!"
            notif_type = "DONATION_COLLECTED"
        elif new_status == "Cancelled":
            allocation.pickup_status = "Cancelled"
            donation.pickup_status = "Cancelled"
            msg = f"Pickup for {donation.item_name} has been cancelled."
            notif_type = "PICKUP_CANCELLED"
        else:
            msg = f"Pickup status updated to {new_status}."
            notif_type = "PICKUP_STATUS_CHANGED"

        allocation.save()
        donation.save()

        create_notification(
            recipient=donation.donor,
            title=f"Pickup Update: {new_status}",
            message=msg,
            notification_type=notif_type,
        )

    return True, f"Pickup status updated to '{new_status}' successfully!"
