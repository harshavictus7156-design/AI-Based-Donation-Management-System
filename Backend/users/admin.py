from django.contrib import admin

from .models import (
    Donor,
    NGO,
    Donation,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
)


# =========================================================
# DONOR
# =========================================================

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )


# =========================================================
# NGO
# =========================================================

@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ngo_name",
        "email_id",
        "status",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "ngo_name",
        "email_id",
    )


# =========================================================
# DONATION
# =========================================================

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "item_name",
        "category",
        "quantity",
        "donor",
        "ngo",
        "status",
        "donation_date",
    )

    list_filter = (
        "status",
        "category",
    )

    search_fields = (
        "item_name",
        "donor__name",
        "ngo__ngo_name",
    )


# =========================================================
# NGO REQUIREMENT
# =========================================================

@admin.register(NGORequirement)
class NGORequirementAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ngo",
        "item_name",
        "category",
        "required_quantity",
        "fulfilled_quantity",
        "remaining_quantity",
        "priority",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "priority",
        "is_active",
    )

    search_fields = (
        "item_name",
        "ngo__ngo_name",
    )


# =========================================================
# DONATION ALLOCATION
# =========================================================

@admin.register(DonationAllocation)
class DonationAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "donation",
        "ngo",
        "requirement",
        "allocated_quantity",
        "status",
        "allocated_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "donation__item_name",
        "ngo__ngo_name",
    )


# =========================================================
# PICKUP REQUEST
# =========================================================

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "allocation",
        "pickup_address",
        "scheduled_time",
        "status",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "status",
        "scheduled_time",
    )

    search_fields = (
        "allocation__donation__item_name",
        "allocation__ngo__ngo_name",
        "pickup_address",
    )

    ordering = (
        "-scheduled_time",
    )