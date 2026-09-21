from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import (
    Donor,
    NGO,
    Donation,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
    normalize_requirement_item_name,
    normalize_requirement_category,
)


# =========================================================
# DONOR SERIALIZER
# =========================================================

class DonorSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = Donor
        fields = "__all__"

    def validate_email(self, value):

        if Donor.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "This email is already registered."
            )

        return value

    def validate_password(self, value):

        if len(value) < 6:

            raise serializers.ValidationError(
                "Password must contain at least 6 characters."
            )

        return value

    def create(self, validated_data):

        validated_data["password"] = make_password(
            validated_data["password"]
        )

        return Donor.objects.create(
            **validated_data
        )


# =========================================================
# NGO SERIALIZER
# =========================================================

class NGOSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = NGO
        fields = "__all__"

    def validate_email_id(self, value):

        if NGO.objects.filter(
            email_id=value
        ).exists():

            raise serializers.ValidationError(
                "This email is already registered."
            )

        return value

    def validate_password(self, value):

        if len(value) < 6:

            raise serializers.ValidationError(
                "Password must contain at least 6 characters."
            )

        return value

    def create(self, validated_data):

        validated_data["password"] = make_password(
            validated_data["password"]
        )

        return NGO.objects.create(
            **validated_data
        )


# =========================================================
# NGO REQUIREMENT SERIALIZER
# =========================================================

class NGORequirementSerializer(
    serializers.ModelSerializer
):

    # -----------------------------------------------------
    # NGO NAME
    # -----------------------------------------------------

    ngo_name = serializers.CharField(
        source="ngo.ngo_name",
        read_only=True
    )

    # -----------------------------------------------------
    # REMAINING QUANTITY
    # -----------------------------------------------------

    remaining_quantity = serializers.IntegerField(
        read_only=True
    )

    # -----------------------------------------------------
    # FULFILLED STATUS
    # -----------------------------------------------------

    is_fulfilled = serializers.BooleanField(
        read_only=True
    )

    def validate_item_name(self, value):
        normalized = normalize_requirement_item_name(value)

        if not normalized:
            raise serializers.ValidationError(
                "Item name is required."
            )

        # Store a clean, human-readable value while keeping the original
        # item meaning intact for backend matching.
        return " ".join(
            word.capitalize()
            for word in normalized.split()
        )

    def validate_category(self, value):
        return normalize_requirement_category(value)

    class Meta:

        model = NGORequirement

        fields = [
            "id",

            # ---------------- NGO ----------------
            "ngo",
            "ngo_name",

            # ---------------- ITEM ----------------
            "item_name",
            "category",

            # ---------------- QUANTITY ----------------
            "required_quantity",
            "fulfilled_quantity",
            "remaining_quantity",

            # ---------------- PRIORITY ----------------
            "priority",

            # ---------------- DESCRIPTION ----------------
            "description",

            # ---------------- STATUS ----------------
            "is_active",
            "is_fulfilled",

            # ---------------- DATE ----------------
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",

            # NGO is assigned automatically
            # from the logged-in NGO account.
            "ngo",

            "ngo_name",

            "fulfilled_quantity",

            "remaining_quantity",

            "is_fulfilled",

            "created_at",

            "updated_at",
        ]


# =========================================================
# DONATION SERIALIZER
# =========================================================

class DonationSerializer(
    serializers.ModelSerializer
):

    # -----------------------------------------------------
    # DONOR DETAILS
    # -----------------------------------------------------

    donor_name = serializers.CharField(
        source="donor.name",
        read_only=True
    )

    donor_email = serializers.EmailField(
        source="donor.email",
        read_only=True
    )

    donor_phone = serializers.CharField(
        source="donor.phone",
        read_only=True
    )

    # -----------------------------------------------------
    # NGO DETAILS
    # -----------------------------------------------------

    ngo_name = serializers.CharField(
        source="ngo.ngo_name",
        read_only=True
    )

    # -----------------------------------------------------
    # ALLOCATION DETAILS
    # -----------------------------------------------------

    allocated_quantity = serializers.SerializerMethodField()

    allocated_ngos = serializers.SerializerMethodField()

    remaining_quantity = serializers.SerializerMethodField()

    # -----------------------------------------------------
    # PICKUP DETAILS
    # -----------------------------------------------------

    pickup_date = serializers.SerializerMethodField()
    pickup_time = serializers.SerializerMethodField()
    pickup_status = serializers.SerializerMethodField()

    def _get_donation_pickup(self, obj):
        """
        Find the pickup request belonging to this donation.
        Prefer the allocation connected to the donation's selected NGO.
        """
        allocations = obj.allocations.select_related(
            "pickup_request",
            "ngo",
        )

        allocation = (
            allocations.filter(ngo=obj.ngo).first()
            if obj.ngo_id
            else allocations.first()
        )

        if not allocation:
            return None

        try:
            return allocation.pickup_request
        except Exception:
            return None

    def get_pickup_date(self, obj):
        pickup = self._get_donation_pickup(obj)
        return pickup.scheduled_time if pickup else None

    def get_pickup_time(self, obj):
        pickup = self._get_donation_pickup(obj)
        return pickup.scheduled_time if pickup else None

    def get_pickup_status(self, obj):
        pickup = self._get_donation_pickup(obj)
        return pickup.status if pickup else "Not Scheduled"

    def validate_item_name(self, value):
        normalized = normalize_requirement_item_name(value)

        if not normalized:
            raise serializers.ValidationError(
                "Item name is required."
            )

        return " ".join(
            word.capitalize()
            for word in normalized.split()
        )

    def validate_category(self, value):
        return normalize_requirement_category(value)

    class Meta:

        model = Donation

        fields = [
            "id",

            # ---------------- DONOR ----------------
            "donor",
            "donor_name",
            "donor_email",
            "donor_phone",

            # ---------------- OLD NGO FIELD ----------------
            "ngo",
            "ngo_name",

            # ---------------- ITEM ----------------
            "item_name",
            "category",
            "quantity",
            "condition",
            "description",
            "location",
            "item_image",

            # ---------------- STATUS ----------------
            "status",

            # ---------------- ALLOCATION ----------------
            "allocated_quantity",
            "allocated_ngos",
            "remaining_quantity",

            # ---------------- DATE ----------------
            "donation_date",

            # ---------------- PICKUP ----------------
            "pickup_date",
            "pickup_time",
            "pickup_status",
        ]

        read_only_fields = [
            "id",

            "donor",
            "donor_name",
            "donor_email",
            "donor_phone",

            "ngo_name",

            "status",

            "allocated_quantity",
            "allocated_ngos",
            "remaining_quantity",

            "donation_date",

            "pickup_date",
            "pickup_time",
            "pickup_status",
        ]

    # =====================================================
    # TOTAL ALLOCATED QUANTITY
    # =====================================================

    def get_allocated_quantity(self, obj):

        total = sum(
            allocation.allocated_quantity
            for allocation in obj.allocations.all()
            if allocation.status != "Rejected"
        )

        return total

    # =====================================================
    # REMAINING DONATION QUANTITY
    # =====================================================

    def get_remaining_quantity(self, obj):

        allocated = self.get_allocated_quantity(obj)

        remaining = obj.quantity - allocated

        return max(
            remaining,
            0
        )

    # =====================================================
    # ALLOCATED NGO DETAILS
    # =====================================================

    def get_allocated_ngos(self, obj):

        allocations = obj.allocations.select_related(
            "ngo",
            "requirement",
            "pickup_request",
        ).all()

        result = []

        for allocation in allocations:

            if allocation.status == "Rejected":
                continue

            try:
                pickup = allocation.pickup_request
            except Exception:
                pickup = None

            result.append({
                "allocation_id": allocation.id,

                "ngo_id": allocation.ngo.id,

                "ngo_name": allocation.ngo.ngo_name,

                "allocated_quantity":
                    allocation.allocated_quantity,

                "status":
                    allocation.status,

                "requirement_id":
                    allocation.requirement.id
                    if allocation.requirement
                    else None,

                "pickup": {
                    "id": pickup.id,
                    "pickup_address": pickup.pickup_address,
                    "scheduled_time": pickup.scheduled_time,
                    "status": pickup.status,
                } if pickup else None,
            })

        return result


# =========================================================
# DONATION ALLOCATION SERIALIZER
# =========================================================

class DonationAllocationSerializer(
    serializers.ModelSerializer
):

    # -----------------------------------------------------
    # DONOR
    # -----------------------------------------------------

    donor_name = serializers.CharField(
        source="donation.donor.name",
        read_only=True
    )

    # -----------------------------------------------------
    # DONATION
    # -----------------------------------------------------

    item_name = serializers.CharField(
        source="donation.item_name",
        read_only=True
    )

    category = serializers.CharField(
        source="donation.category",
        read_only=True
    )

    donation_quantity = serializers.IntegerField(
        source="donation.quantity",
        read_only=True
    )

    # -----------------------------------------------------
    # NGO
    # -----------------------------------------------------

    ngo_name = serializers.CharField(
        source="ngo.ngo_name",
        read_only=True
    )

    # -----------------------------------------------------
    # REQUIREMENT
    # -----------------------------------------------------

    required_quantity = serializers.IntegerField(
        source="requirement.required_quantity",
        read_only=True
    )

    remaining_requirement = serializers.SerializerMethodField()

    # -----------------------------------------------------
    # PICKUP DETAILS
    # -----------------------------------------------------
    #
    # PickupRequest is the source of truth for:
    #   - pickup_address
    #   - scheduled_time
    #   - pickup_status
    #
    # The legacy pickup_date/pickup_time fields on Donation and
    # DonationAllocation are not used for scheduling.
    #

    pickup_address = serializers.SerializerMethodField()
    scheduled_time = serializers.SerializerMethodField()
    pickup_status = serializers.SerializerMethodField()

    def get_pickup_request(self, obj):
        try:
            return obj.pickup_request
        except Exception:
            return None

    def get_pickup_address(self, obj):
        pickup = self.get_pickup_request(obj)
        return pickup.pickup_address if pickup else None

    def get_scheduled_time(self, obj):
        pickup = self.get_pickup_request(obj)
        return pickup.scheduled_time if pickup else None

    def get_pickup_status(self, obj):
        pickup = self.get_pickup_request(obj)
        return pickup.status if pickup else "Not Scheduled"

    class Meta:

        model = DonationAllocation

        fields = [
            "id",

            # ---------------- DONATION ----------------
            "donation",
            "donor_name",
            "item_name",
            "category",
            "donation_quantity",

            # ---------------- NGO ----------------
            "ngo",
            "ngo_name",

            # ---------------- REQUIREMENT ----------------
            "requirement",
            "required_quantity",
            "remaining_requirement",

            # ---------------- ALLOCATION ----------------
            "allocated_quantity",

            # ---------------- STATUS ----------------
            "status",

            # ---------------- DATE ----------------
            "allocated_at",

            # ---------------- PICKUP ----------------
            "pickup_address",
            "scheduled_time",
            "pickup_status",
        ]

        read_only_fields = [
            "id",

            "donor_name",
            "item_name",
            "category",
            "donation_quantity",

            "ngo_name",

            "required_quantity",
            "remaining_requirement",

            "allocated_at",

            "pickup_address",
            "scheduled_time",
            "pickup_status",
        ]

    # =====================================================
    # REMAINING NGO REQUIREMENT
    # =====================================================

    def get_remaining_requirement(self, obj):

        if not obj.requirement:
            return 0

        return obj.requirement.remaining_quantity


# =========================================================
# LOGIN SERIALIZER
# =========================================================

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )


# =========================================================
# SINGLE REGISTRATION SERIALIZER
# =========================================================

class SingleRegistrationSerializer(
    serializers.Serializer
):

    user_type = serializers.ChoiceField(
        choices=[
            ("donor", "Donor"),
            ("ngo", "NGO"),
        ]
    )

    data = serializers.DictField()


# =========================================================
# PICKUP REQUEST SERIALIZER
# =========================================================

class PickupRequestSerializer(
    serializers.ModelSerializer
):

    # -----------------------------------------------------
    # DERIVED FIELDS (read-only)
    # -----------------------------------------------------

    donor_name = serializers.CharField(
        source="allocation.donation.donor.name",
        read_only=True
    )

    donor_phone = serializers.CharField(
        source="allocation.donation.donor.phone",
        read_only=True
    )

    donor_email = serializers.EmailField(
        source="allocation.donation.donor.email",
        read_only=True
    )

    item_name = serializers.CharField(
        source="allocation.donation.item_name",
        read_only=True
    )

    category = serializers.CharField(
        source="allocation.donation.category",
        read_only=True
    )

    allocated_quantity = serializers.IntegerField(
        source="allocation.allocated_quantity",
        read_only=True
    )

    ngo_name = serializers.CharField(
        source="allocation.ngo.ngo_name",
        read_only=True
    )

    donation_id = serializers.IntegerField(
        source="allocation.donation.id",
        read_only=True
    )

    allocation_id = serializers.IntegerField(
        source="allocation.id",
        read_only=True
    )

    class Meta:

        model = PickupRequest

        fields = [
            "id",

            # ------- ALLOCATION -------
            "allocation",
            "allocation_id",
            "donation_id",

            # ------- DONOR INFO -------
            "donor_name",
            "donor_phone",
            "donor_email",

            # ------- ITEM INFO -------
            "item_name",
            "category",
            "allocated_quantity",

            # ------- NGO INFO -------
            "ngo_name",

            # ------- PICKUP DETAILS -------
            "pickup_address",
            "scheduled_time",
            "notes",

            # ------- STATUS -------
            "status",

            # ------- DATES -------
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "allocation_id",
            "donation_id",
            "donor_name",
            "donor_phone",
            "donor_email",
            "item_name",
            "category",
            "allocated_quantity",
            "ngo_name",
            "status",
            "created_at",
            "updated_at",
        ]