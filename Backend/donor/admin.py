from django.contrib import admin

from .models import (
    Donor,
    NGO,
    Donation,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
)


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
        "phone",
    )


@admin.register(NGO)
class NGOAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ngo_name",
        "email_id",
        "status",
    )


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
        "pickup_address",
        "allocation__donation__item_name",
        "allocation__ngo__ngo_name",
    )

    ordering = (
        "-scheduled_time",
    )