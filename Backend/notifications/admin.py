from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "recipient_display",
        "title",
        "notification_type",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "is_read")
    search_fields = ("title", "message", "event_key", "donor__name", "ngo__ngo_name")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    @admin.display(description="Recipient")
    def recipient_display(self, obj):
        return obj.recipient
