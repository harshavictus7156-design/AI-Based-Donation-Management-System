from django.db import models


# =========================================================
# DONOR
# =========================================================

class Donor(models.Model):

    name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=10)

    password = models.CharField(max_length=128)

    picture = models.ImageField(
        upload_to="donor_pictures/",
        null=True,
        blank=True
    )

    language_preference = models.CharField(max_length=50)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=6)

    status_active = models.BooleanField(default=True)

    registered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


# =========================================================
# NGO
# =========================================================

class NGO(models.Model):

    ngo_name = models.CharField(max_length=200)

    picture = models.ImageField(
        upload_to="ngo_pictures/",
        null=True,
        blank=True
    )

    description = models.TextField()

    registration_no = models.CharField(
        max_length=100,
        unique=True
    )

    email_id = models.EmailField(unique=True)

    phone_no = models.CharField(max_length=10)

    website_link = models.URLField(blank=True)

    address = models.TextField()

    state = models.CharField(max_length=100)

    city = models.CharField(max_length=100)

    pincode = models.CharField(max_length=6)

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    language = models.CharField(max_length=50)

    certificate_files = models.FileField(
        upload_to="ngo_certificates/",
        null=True,
        blank=True
    )

    registered_at = models.DateTimeField(
        auto_now_add=True
    )

    password = models.CharField(max_length=128)

    def __str__(self):
        return self.ngo_name

    @property
    def is_authenticated(self):
        return True


# =========================================================
# NGO REQUIREMENT
# =========================================================

def normalize_requirement_item_name(value):
    """
    Normalize item names for requirement/donation matching without
    hard-coding individual donation items.
    """
    if not value:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )


def normalize_requirement_category(value):
    """
    Normalize category values while keeping the model's existing
    CATEGORY_CHOICES unchanged.
    """
    if not value:
        return "Other"

    value = (
        str(value)
        .strip()
        .lower()
        .replace("-", " ")
        .replace("_", " ")
    )

    category_aliases = {
        "clothes": "Clothing",
        "cloth": "Clothing",
        "dress": "Clothing",
        "books": "Books",
        "book": "Books",
        "food": "Food",
        "groceries": "Food",
        "grocery": "Food",
        "electronics": "Electronics",
        "electronic": "Electronics",
        "furniture": "Furniture",
        "medical": "Medical Supplies",
        "medicine": "Medical Supplies",
        "medicines": "Medical Supplies",
        "medical supplies": "Medical Supplies",
        "school": "School Supplies",
        "school supplies": "School Supplies",
        "stationery": "School Supplies",
        "education": "School Supplies",
    }

    return category_aliases.get(value, str(value).strip())


class NGORequirement(models.Model):

    CATEGORY_CHOICES = [
        ("Clothing", "Clothing"),
        ("Books", "Books"),
        ("Food", "Food"),
        ("Electronics", "Electronics"),
        ("Furniture", "Furniture"),
        ("Medical Supplies", "Medical Supplies"),
        ("School Supplies", "School Supplies"),
        ("Other", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Urgent", "Urgent"),
    ]

    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE,
        related_name="requirements"
    )

    item_name = models.CharField(max_length=200)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    required_quantity = models.PositiveIntegerField()

    fulfilled_quantity = models.PositiveIntegerField(
        default=0
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="Medium"
    )

    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    @property
    def remaining_quantity(self):

        remaining = (
            self.required_quantity
            - self.fulfilled_quantity
        )

        return max(remaining, 0)

    @property
    def is_fulfilled(self):

        return (
            self.fulfilled_quantity
            >= self.required_quantity
        )

    def __str__(self):

        return (
            f"{self.ngo.ngo_name} - "
            f"{self.item_name} - "
            f"{self.remaining_quantity} needed"
        )


# =========================================================
# DONATION
# =========================================================

class Donation(models.Model):

    CATEGORY_CHOICES = [
        ("Clothing", "Clothing"),
        ("Books", "Books"),
        ("Food", "Food"),
        ("Electronics", "Electronics"),
        ("Furniture", "Furniture"),
        ("Medical Supplies", "Medical Supplies"),
        ("School Supplies", "School Supplies"),
        ("Other", "Other"),
    ]

    CONDITION_CHOICES = [
        ("New", "New"),
        ("Like New", "Like New"),
        ("Good", "Good"),
        ("Used", "Used"),
    ]

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Collected", "Collected"),
    ]

    # -----------------------------------------------------
    # DONOR
    # -----------------------------------------------------

    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,
        related_name="donations"
    )

    # -----------------------------------------------------
    # NGO
    # -----------------------------------------------------

    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE,
        related_name="donations",
        null=True,
        blank=True
    )

    # -----------------------------------------------------
    # ITEM DETAILS
    # -----------------------------------------------------

    item_name = models.CharField(max_length=200)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES
    )

    quantity = models.PositiveIntegerField()

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES
    )

    description = models.TextField()

    # -----------------------------------------------------
    # PICKUP LOCATION
    # -----------------------------------------------------

    location = models.CharField(max_length=500)

    # -----------------------------------------------------
    # ITEM IMAGE
    # -----------------------------------------------------

    item_image = models.ImageField(
        upload_to="donation_items/",
        null=True,
        blank=True
    )

    # -----------------------------------------------------
    # DONATION STATUS
    # -----------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    # =====================================================
    # DONATION PICKUP
    # =====================================================

    PICKUP_STATUS_CHOICES = [
        ("Not Scheduled", "Not Scheduled"),
        ("Scheduled", "Scheduled"),
        ("Accepted", "Accepted"),
        ("Picked Up", "Picked Up"),
        ("Cancelled", "Cancelled"),
    ]

    pickup_date = models.DateField(
        null=True,
        blank=True
    )

    pickup_time = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    pickup_status = models.CharField(
        max_length=20,
        choices=PICKUP_STATUS_CHOICES,
        default="Not Scheduled",
        blank=True
    )

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    donation_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.item_name} - "
            f"{self.donor.name}"
        )


# =========================================================
# DONATION ALLOCATION
# =========================================================

class DonationAllocation(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Collected", "Collected"),
    ]

    # -----------------------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------------------

    donation = models.ForeignKey(
        Donation,
        on_delete=models.CASCADE,
        related_name="allocations"
    )

    ngo = models.ForeignKey(
        NGO,
        on_delete=models.CASCADE,
        related_name="donation_allocations"
    )

    requirement = models.ForeignKey(
        NGORequirement,
        on_delete=models.SET_NULL,
        related_name="allocations",
        null=True,
        blank=True
    )

    # -----------------------------------------------------
    # ALLOCATION
    # -----------------------------------------------------

    allocated_quantity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    # =====================================================
    # PICKUP STATUS
    # =====================================================

    PICKUP_STATUS_CHOICES = [
        ("Not Scheduled", "Not Scheduled"),
        ("Scheduled", "Scheduled"),
        ("Accepted", "Accepted"),
        ("Picked Up", "Picked Up"),
        ("Cancelled", "Cancelled"),
    ]

    pickup_date = models.DateField(
        null=True,
        blank=True
    )

    pickup_time = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    pickup_status = models.CharField(
        max_length=20,
        choices=PICKUP_STATUS_CHOICES,
        default="Not Scheduled",
        blank=True
    )

    # -----------------------------------------------------
    # DATE
    # -----------------------------------------------------

    allocated_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):

        return (
            f"{self.donation.item_name} → "
            f"{self.ngo.ngo_name} "
            f"({self.allocated_quantity})"
        )


# =========================================================
# PICKUP REQUEST
# =========================================================

class PickupRequest(models.Model):

    PICKUP_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Dispatched", "Dispatched"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    allocation = models.OneToOneField(
        DonationAllocation,
        on_delete=models.CASCADE,
        related_name="pickup_request"
    )

    pickup_address = models.TextField()

    scheduled_time = models.DateTimeField()

    notes = models.TextField(
        blank=True,
        default=""
    )

    status = models.CharField(
        max_length=20,
        choices=PICKUP_STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"Pickup #{self.id} — "
            f"{self.allocation.donation.item_name} — "
            f"{self.status}"
        )