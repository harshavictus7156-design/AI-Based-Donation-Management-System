from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from donor.models import Donor, NGO

from .models import Notification
from .serializers import NotificationSerializer


def get_authenticated_recipient(request):
    """Resolve the recipient exclusively from the signed existing JWT claims."""
    user_id = request.auth.get("user_id")
    user_type = request.auth.get("user_type")

    if user_type == "Donor":
        return get_object_or_404(Donor, id=user_id)
    if user_type == "NGO":
        return get_object_or_404(NGO, id=user_id)

    # Existing tokens only carry Donor/NGO types. Treat malformed tokens as
    # unauthenticated instead of accepting an id supplied by a client body.
    raise AuthenticationFailed("Invalid authentication token.")


class RecipientNotificationMixin:
    permission_classes = [IsAuthenticated]

    def get_recipient(self, request):
        return get_authenticated_recipient(request)

    def get_queryset(self, request):
        recipient = self.get_recipient(request)
        return Notification.objects.for_recipient(recipient).select_related(
            "donor",
            "ngo",
        )


class NotificationListView(RecipientNotificationMixin, APIView):
    def get(self, request):
        serializer = NotificationSerializer(self.get_queryset(request), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationUnreadCountView(RecipientNotificationMixin, APIView):
    def get(self, request):
        return Response(
            {"unread_count": self.get_queryset(request).filter(is_read=False).count()},
            status=status.HTTP_200_OK,
        )


class NotificationMarkReadView(RecipientNotificationMixin, APIView):
    def patch(self, request, pk):
        notification = get_object_or_404(self.get_queryset(request), id=pk)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
        return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)


class NotificationReadAllView(RecipientNotificationMixin, APIView):
    def patch(self, request):
        updated_count = self.get_queryset(request).filter(is_read=False).update(is_read=True)
        return Response(
            {"updated_count": updated_count},
            status=status.HTTP_200_OK,
        )


class NotificationDeleteView(RecipientNotificationMixin, APIView):
    def delete(self, request, pk):
        notification = get_object_or_404(self.get_queryset(request), id=pk)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
