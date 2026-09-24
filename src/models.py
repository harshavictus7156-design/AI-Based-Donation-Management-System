"""
Database models re-export for easy importing across the Streamlit application.
"""

from src.database import init_database

init_database()

from donor.models import (
    Donor,
    NGO,
    Donation,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
    normalize_requirement_item_name,
    normalize_requirement_category,
)
from notifications.models import Notification
from users.models import CustomUser, Profile, NGOProfile

__all__ = [
    "Donor",
    "NGO",
    "Donation",
    "NGORequirement",
    "DonationAllocation",
    "PickupRequest",
    "Notification",
    "CustomUser",
    "Profile",
    "NGOProfile",
    "normalize_requirement_item_name",
    "normalize_requirement_category",
]
