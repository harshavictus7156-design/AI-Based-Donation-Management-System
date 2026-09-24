"""
Services package initialization.
"""

from src.services.ai_service import (
    analyze_image_with_gemini,
    find_matching_ngos,
    normalize_item_name,
    categories_match,
)
from src.services.donation_service import (
    create_donation,
    update_donation,
    allocate_donation,
    create_or_update_pickup_request,
    cancel_pickup_request,
)
from src.services.donor_service import (
    register_donor,
    update_donor_profile,
    get_donor_dashboard_stats,
    get_donor_donations,
    get_donor_leaderboard,
)
from src.services.ngo_service import (
    register_ngo,
    update_ngo_profile,
    get_approved_ngos,
    get_ngo_dashboard_stats,
    add_requirement,
    update_requirement,
    delete_requirement,
    accept_allocation,
    reject_allocation,
    update_pickup_status,
)
from src.services.admin_service import (
    get_admin_dashboard_stats,
    approve_ngo,
    reject_ngo,
    toggle_donor_status,
)
from src.services.notification_service import (
    create_notification,
    get_user_notifications,
    get_unread_count,
    mark_notification_read,
    mark_all_read,
    delete_notification,
)

__all__ = [
    "analyze_image_with_gemini",
    "find_matching_ngos",
    "normalize_item_name",
    "categories_match",
    "create_donation",
    "update_donation",
    "allocate_donation",
    "create_or_update_pickup_request",
    "cancel_pickup_request",
    "register_donor",
    "update_donor_profile",
    "get_donor_dashboard_stats",
    "get_donor_donations",
    "get_donor_leaderboard",
    "register_ngo",
    "update_ngo_profile",
    "get_approved_ngos",
    "get_ngo_dashboard_stats",
    "add_requirement",
    "update_requirement",
    "delete_requirement",
    "accept_allocation",
    "reject_allocation",
    "update_pickup_status",
    "get_admin_dashboard_stats",
    "approve_ngo",
    "reject_ngo",
    "toggle_donor_status",
    "create_notification",
    "get_user_notifications",
    "get_unread_count",
    "mark_notification_read",
    "mark_all_read",
    "delete_notification",
]
