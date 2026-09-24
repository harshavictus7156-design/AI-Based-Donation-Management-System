"""
Donor Service for donor registration, profile management, stats, ranking, and activity.
"""

from django.db.models import Count, Sum, Q
from src.models import (
    Donor,
    Donation,
    DonationAllocation,
    PickupRequest,
    Notification,
)
from src.auth import hash_password
from src.utils import get_rank_badge


def register_donor(data: dict) -> tuple[bool, str, Donor]:
    """Registers a new donor account."""
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    phone = str(data.get("phone", "")).strip()
    password = str(data.get("password", "")).strip()
    address = str(data.get("address", "")).strip()
    city = str(data.get("city", "")).strip()
    state = str(data.get("state", "")).strip()
    pincode = str(data.get("pincode", "")).strip()
    language = str(data.get("language_preference", "English")).strip()
    picture_path = data.get("picture")

    if not name or not email or not password:
        return False, "Name, email, and password are required.", None

    if Donor.objects.filter(email__iexact=email).exists():
        return False, "A donor account with this email already exists.", None

    try:
        donor = Donor.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=hash_password(password),
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            language_preference=language,
            picture=picture_path if picture_path else None,
            status_active=True,
        )
        return True, "Registration successful! You can now log in.", donor
    except Exception as e:
        return False, f"Registration failed: {e}", None


def update_donor_profile(donor_id: int, data: dict) -> tuple[bool, str]:
    """Updates donor profile information."""
    try:
        donor = Donor.objects.get(id=donor_id)
    except Donor.DoesNotExist:
        return False, "Donor not found."

    donor.name = str(data.get("name", donor.name)).strip()
    donor.phone = str(data.get("phone", donor.phone)).strip()
    donor.address = str(data.get("address", donor.address)).strip()
    donor.city = str(data.get("city", donor.city)).strip()
    donor.state = str(data.get("state", donor.state)).strip()
    donor.pincode = str(data.get("pincode", donor.pincode)).strip()
    donor.language_preference = str(data.get("language_preference", donor.language_preference)).strip()
    
    if data.get("picture"):
        donor.picture = data.get("picture")

    donor.save()
    return True, "Profile updated successfully."


def get_donor_dashboard_stats(donor_id: int) -> dict:
    """Calculates summary KPIs and metrics for donor dashboard."""
    donations = Donation.objects.filter(donor_id=donor_id)
    total_donations = donations.count()
    total_items = donations.aggregate(sum_qty=Sum("quantity"))["sum_qty"] or 0
    pending = donations.filter(status="Pending").count()
    accepted = donations.filter(status="Accepted").count()
    collected = donations.filter(status="Collected").count()
    
    # Impact points: 10 pts per donation + 2 pts per item + 50 pts per collected
    impact_points = (total_donations * 10) + (total_items * 2) + (collected * 50)

    # Calculate ranking position
    all_donors = (
        Donor.objects.filter(status_active=True)
        .annotate(
            donations_count=Count("donations"),
            items_sum=Sum("donations__quantity"),
        )
        .order_by("-items_sum", "-donations_count")
    )
    
    rank = 1
    for idx, d in enumerate(all_donors, start=1):
        if d.id == donor_id:
            rank = idx
            break

    tier, badge_color, icon = get_rank_badge(rank)

    return {
        "total_donations": total_donations,
        "total_items": total_items,
        "pending": pending,
        "accepted": accepted,
        "collected": collected,
        "impact_points": impact_points,
        "rank": rank,
        "rank_tier": tier,
        "rank_color": badge_color,
        "rank_icon": icon,
    }


def get_donor_donations(
    donor_id: int,
    search_query: str = "",
    status_filter: str = "All",
    category_filter: str = "All",
) -> list[Donation]:
    """Fetches and filters donations for a donor."""
    qs = Donation.objects.filter(donor_id=donor_id).select_related("ngo").prefetch_related("allocations__ngo", "allocations__pickup_request")

    if status_filter and status_filter != "All":
        qs = qs.filter(status=status_filter)
    if category_filter and category_filter != "All":
        qs = qs.filter(category=category_filter)
    if search_query and search_query.strip():
        q = search_query.strip()
        qs = qs.filter(
            Q(item_name__icontains=q)
            | Q(description__icontains=q)
            | Q(location__icontains=q)
            | Q(ngo__ngo_name__icontains=q)
        )

    return list(qs.order_by("-donation_date"))


def get_donor_leaderboard(current_donor_id: int = None) -> list[dict]:
    """Generates the community donor leaderboard with ranks and badges."""
    donors = (
        Donor.objects.filter(status_active=True)
        .annotate(
            total_donations=Count("donations"),
            total_items=Sum("donations__quantity"),
            collected_count=Count("donations", filter=Q(donations__status="Collected")),
        )
        .order_by("-total_items", "-total_donations")
    )

    leaderboard = []
    for idx, d in enumerate(donors, start=1):
        total_don = d.total_donations or 0
        total_itms = d.total_items or 0
        coll_cnt = d.collected_count or 0
        points = (total_don * 10) + (total_itms * 2) + (coll_cnt * 50)
        tier, color, icon = get_rank_badge(idx)

        leaderboard.append({
            "rank": idx,
            "id": d.id,
            "name": d.name,
            "city": d.city,
            "state": d.state,
            "total_donations": total_don,
            "total_items": total_itms,
            "points": points,
            "tier": tier,
            "badge_color": color,
            "icon": icon,
            "is_current_user": (d.id == current_donor_id),
            "picture": d.picture.url if d.picture else None,
        })

    return leaderboard
