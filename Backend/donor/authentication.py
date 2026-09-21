from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth.models import User

from .models import Donor, NGO


class CustomJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):

        user_id = validated_token.get("user_id")
        user_type = str(validated_token.get("user_type", "")).strip().lower()

        if user_id is None:
            raise AuthenticationFailed("Token contains no user_id")

        if user_type == "admin":
            try:
                return User.objects.get(
                    id=user_id,
                    is_active=True,
                    is_staff=True,
                )
            except User.DoesNotExist:
                raise AuthenticationFailed("Admin user not found")

        # Check Donor
        try:
            return Donor.objects.get(id=user_id)
        except Donor.DoesNotExist:
            pass

        # Check NGO
        try:
            return NGO.objects.get(id=user_id)
        except NGO.DoesNotExist:
            pass

        raise AuthenticationFailed("User not found")
