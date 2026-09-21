from datetime import timedelta

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from donor.models import (
    Donation,
    DonationAllocation,
    Donor,
    NGO,
    NGORequirement,
    PickupRequest,
)

from .models import Notification
from .services import create_notification, notify_donation_submitted


class NotificationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def create_donor(self, label="donor"):
        return Donor.objects.create(
            name=f"{label.title()} Name",
            email=f"{label}@example.com",
            phone="9876543210",
            password="not-used-in-tests",
            language_preference="English",
            address="1 Donor Street",
            city="Pune",
            state="Maharashtra",
            pincode="411001",
        )

    def create_ngo(self, label="ngo", status="Approved"):
        return NGO.objects.create(
            ngo_name=f"{label.title()} Foundation",
            description="Test NGO",
            registration_no=f"REG-{label}",
            email_id=f"{label}@example.com",
            phone_no="9876543211",
            address="2 NGO Street",
            state="Maharashtra",
            city="Pune",
            pincode="411002",
            language="English",
            password="not-used-in-tests",
            status=status,
        )

    def create_donation(self, donor, label="donation"):
        return Donation.objects.create(
            donor=donor,
            item_name="Blankets",
            category="Clothing",
            quantity=5,
            condition="Good",
            description=f"{label} description",
            location="Pune",
        )

    def create_requirement(self, ngo, label="requirement"):
        return NGORequirement.objects.create(
            ngo=ngo,
            item_name="Blankets",
            category="Clothing",
            required_quantity=5,
            priority="High",
            description=f"{label} description",
        )

    def authenticate_as(self, recipient):
        user_type = "Donor" if isinstance(recipient, Donor) else "NGO"
        self.client.force_authenticate(
            user=recipient,
            token={"user_id": recipient.id, "user_type": user_type},
        )


class NotificationAPITests(NotificationTestCase):
    def setUp(self):
        super().setUp()
        self.donor = self.create_donor("primary-donor")
        self.other_donor = self.create_donor("other-donor")
        self.authenticate_as(self.donor)

    def create_for_donor(self, donor, title):
        return create_notification(
            recipient=donor,
            title=title,
            message=f"{title} message",
            notification_type=Notification.NotificationType.DONATION_SUBMITTED,
        )

    def test_notification_apis_only_return_the_authenticated_recipients_data(self):
        first = self.create_for_donor(self.donor, "First")
        second = self.create_for_donor(self.donor, "Second")
        other = self.create_for_donor(self.other_donor, "Private")

        response = self.client.get(
            reverse("notification-list"),
            {"donor_id": self.other_donor.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["id"] for item in response.data}, {first.id, second.id})

        response = self.client.get(reverse("notification-unread-count"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"unread_count": 2})

        response = self.client.patch(reverse("notification-mark-read", args=[first.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_read"])

        response = self.client.patch(reverse("notification-read-all"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"updated_count": 1})

        response = self.client.delete(reverse("notification-delete", args=[second.id]))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Notification.objects.filter(id=second.id).exists())

        response = self.client.patch(reverse("notification-mark-read", args=[other.id]))
        self.assertEqual(response.status_code, 404)

    def test_notification_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("notification-list"))
        self.assertEqual(response.status_code, 401)

    def test_notification_recipient_constraint_and_event_deduplication(self):
        ngo = self.create_ngo()

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Notification.objects.create(
                    title="Invalid",
                    message="A notification requires exactly one recipient.",
                    notification_type=Notification.NotificationType.DONATION_SUBMITTED,
                )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Notification.objects.create(
                    donor=self.donor,
                    ngo=ngo,
                    title="Invalid",
                    message="A notification cannot target two recipients.",
                    notification_type=Notification.NotificationType.DONATION_SUBMITTED,
                )

        donation = self.create_donation(self.donor)
        notify_donation_submitted(donation)
        notify_donation_submitted(donation)

        self.assertEqual(
            Notification.objects.for_recipient(self.donor)
            .filter(event_key=f"donation:{donation.id}:submitted")
            .count(),
            1,
        )


class WorkflowNotificationTriggerTests(NotificationTestCase):
    def test_donation_submission_and_lifecycle_notifications(self):
        donor = self.create_donor()
        ngo = self.create_ngo()
        self.authenticate_as(donor)

        response = self.client.post(
            reverse("donation-create"),
            {
                "item_name": "Blankets",
                "category": "Clothing",
                "quantity": 5,
                "condition": "Good",
                "description": "Warm blankets",
                "location": "Pune",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        donation = Donation.objects.get(id=response.data["id"])
        self.assertTrue(
            Notification.objects.for_recipient(donor).filter(
                notification_type=Notification.NotificationType.DONATION_SUBMITTED
            ).exists()
        )

        requirement = self.create_requirement(ngo)
        DonationAllocation.objects.create(
            donation=donation,
            ngo=ngo,
            requirement=requirement,
            allocated_quantity=5,
        )
        self.authenticate_as(ngo)
        response = self.client.patch(
            reverse("donation-status", args=[donation.id]),
            {"status": "Accepted"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Notification.objects.for_recipient(donor).filter(
                notification_type=Notification.NotificationType.DONATION_APPROVED
            ).exists()
        )

        rejected_donation = self.create_donation(donor, "rejected")
        rejected_requirement = self.create_requirement(ngo, "rejected")
        DonationAllocation.objects.create(
            donation=rejected_donation,
            ngo=ngo,
            requirement=rejected_requirement,
            allocated_quantity=5,
        )
        response = self.client.patch(
            reverse("donation-status", args=[rejected_donation.id]),
            {"status": "Rejected"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Notification.objects.for_recipient(donor).filter(
                notification_type=Notification.NotificationType.DONATION_REJECTED
            ).exists()
        )

        collected_donation = self.create_donation(donor, "collected")
        collected_donation.status = "Collected"
        collected_donation.save(update_fields=["status"])
        self.assertTrue(
            Notification.objects.for_recipient(donor).filter(
                notification_type=Notification.NotificationType.DONATION_COLLECTED
            ).exists()
        )

    def test_ai_matching_and_allocation_notify_both_parties(self):
        donor = self.create_donor()
        ngo = self.create_ngo()
        donation = self.create_donation(donor)
        requirement = self.create_requirement(ngo)
        self.authenticate_as(donor)

        response = self.client.get(reverse("ai-matching", args=[donation.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Notification.objects.for_recipient(donor).filter(
                notification_type=Notification.NotificationType.DONATION_MATCHED
            ).exists()
        )
        self.assertTrue(
            Notification.objects.for_recipient(ngo).filter(
                notification_type=Notification.NotificationType.REQUEST_MATCHED
            ).exists()
        )

        response = self.client.post(
            reverse("donation-allocation", args=[donation.id]),
            {"allocations": [{"requirement_id": requirement.id, "quantity": 5}]},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Notification.objects.for_recipient(donor).filter(
                notification_type=Notification.NotificationType.RESOURCE_ALLOCATED
            ).exists()
        )
        self.assertTrue(
            Notification.objects.for_recipient(ngo).filter(
                notification_type=Notification.NotificationType.RESOURCE_ALLOCATED
            ).exists()
        )

    def test_pickup_creation_and_status_changes_notify_the_other_party(self):
        donor = self.create_donor()
        ngo = self.create_ngo()
        donation = self.create_donation(donor)
        requirement = self.create_requirement(ngo)
        allocation = DonationAllocation.objects.create(
            donation=donation,
            ngo=ngo,
            requirement=requirement,
            allocated_quantity=5,
        )
        self.authenticate_as(donor)
        response = self.client.post(
            reverse("pickup-create"),
            {
                "allocation_id": allocation.id,
                "pickup_address": "1 Donor Street, Pune",
                "scheduled_time": (timezone.now() + timedelta(days=1)).isoformat(),
                "notes": "Ring the bell",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        pickup = PickupRequest.objects.get(id=response.data["pickup"]["id"])
        self.assertTrue(
            Notification.objects.for_recipient(ngo).filter(
                notification_type=Notification.NotificationType.PICKUP_CREATED
            ).exists()
        )

        self.authenticate_as(ngo)
        for new_status, notification_type in (
            ("Confirmed", Notification.NotificationType.PICKUP_CONFIRMED),
            ("Dispatched", Notification.NotificationType.PICKUP_DISPATCHED),
            ("Delivered", Notification.NotificationType.DONATION_DELIVERED),
        ):
            response = self.client.patch(
                reverse("pickup-status-update", args=[pickup.id]),
                {"status": new_status},
                format="json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                Notification.objects.for_recipient(donor).filter(
                    notification_type=notification_type
                ).exists()
            )

        cancellation_donation = self.create_donation(donor, "cancelled pickup")
        cancellation_requirement = self.create_requirement(ngo, "cancelled pickup")
        cancellation_allocation = DonationAllocation.objects.create(
            donation=cancellation_donation,
            ngo=ngo,
            requirement=cancellation_requirement,
            allocated_quantity=5,
        )
        cancellation_pickup = PickupRequest.objects.create(
            allocation=cancellation_allocation,
            pickup_address="1 Donor Street, Pune",
            scheduled_time=timezone.now() + timedelta(days=2),
        )
        self.authenticate_as(donor)
        response = self.client.patch(
            reverse("pickup-cancel", args=[cancellation_pickup.id]),
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Notification.objects.for_recipient(ngo).filter(
                notification_type=Notification.NotificationType.PICKUP_CANCELLED
            ).exists()
        )
