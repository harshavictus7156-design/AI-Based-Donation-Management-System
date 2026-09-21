from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    recipient = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
        ]
        read_only_fields = fields

    def get_recipient(self, obj):
        recipient = obj.recipient
        recipient_type = "Donor" if obj.donor_id else "NGO"
        return {
            "id": recipient.pk,
            "type": recipient_type,
        }
