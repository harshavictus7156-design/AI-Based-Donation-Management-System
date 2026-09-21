from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import (
    CustomUser,
    Profile,
    NGOProfile
)


# =====================================================
# REGISTER SERIALIZER
# =====================================================

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )

    email = serializers.EmailField(
        required=True
    )

    first_name = serializers.CharField(
        required=True
    )

    last_name = serializers.CharField(
        required=True
    )

    class Meta:

        model = CustomUser

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "phone",
            "role"
        ]

    # =================================================
    # EMAIL VALIDATION
    # =================================================

    def validate_email(self, value):

        if CustomUser.objects.filter(
            email__iexact=value
        ).exists():

            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    # =================================================
    # PHONE VALIDATION
    # =================================================

    def validate_phone(self, value):

        if not value.isdigit():

            raise serializers.ValidationError(
                "Phone number must contain only digits."
            )

        if len(value) != 10:

            raise serializers.ValidationError(
                "Phone number must contain exactly 10 digits."
            )

        return value

    # =================================================
    # CREATE USER
    # =================================================

    def create(self, validated_data):

        user = CustomUser.objects.create_user(

            username=validated_data["username"],

            first_name=validated_data["first_name"],

            last_name=validated_data["last_name"],

            email=validated_data["email"],

            password=validated_data["password"],

            phone=validated_data["phone"],

            role=validated_data["role"]

        )

        # =============================================
        # CREATE PROFILE ACCORDING TO ROLE
        # =============================================

        if user.role == "Donor":

            Profile.objects.create(
                user=user
            )

        elif user.role == "NGO":

            NGOProfile.objects.create(
                user=user
            )

        return user


# =====================================================
# DONOR PROFILE SERIALIZER
# =====================================================

class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    name = serializers.SerializerMethodField()

    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True
    )

    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True
    )

    class Meta:

        model = Profile

        fields = [
            "id",
            "name",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "role",
            "address",
            "city",
            "state",
            "pincode",
            "bio"
        ]

    # =================================================
    # DONOR DISPLAY NAME
    # =================================================

    def get_name(self, obj):

        full_name = (
            f"{obj.user.first_name} "
            f"{obj.user.last_name}"
        ).strip()

        if full_name:

            return full_name

        return obj.user.username


# =====================================================
# NGO PROFILE SERIALIZER
# =====================================================

class NGOProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    name = serializers.SerializerMethodField()

    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True
    )

    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True
    )

    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    role = serializers.CharField(
        source="user.role",
        read_only=True
    )

    class Meta:

        model = NGOProfile

        fields = [
            "id",
            "name",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone",
            "role",
            "ngo_name",
            "registration_number",
            "address",
            "city",
            "state",
            "pincode",
            "website",
            "description",
            "is_verified"
        ]

        read_only_fields = [
            "is_verified"
        ]

    # =================================================
    # NGO DISPLAY NAME
    # =================================================

    def get_name(self, obj):

        # First priority:
        # NGO's organization name

        if obj.ngo_name:

            return obj.ngo_name

        # Second priority:
        # Contact person's name

        full_name = (
            f"{obj.user.first_name} "
            f"{obj.user.last_name}"
        ).strip()

        if full_name:

            return full_name

        # Final fallback

        return obj.user.username


# =====================================================
# LOGIN / USER SERIALIZER
# =====================================================

class UserSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    ngo_name = serializers.SerializerMethodField()

    class Meta:

        model = CustomUser

        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "name",
            "ngo_name",
            "email",
            "phone",
            "role"
        ]

    # =================================================
    # DISPLAY NAME
    # =================================================

    def get_name(self, obj):

        # =============================================
        # NGO
        # =============================================

        if obj.role == "NGO":

            if hasattr(obj, "ngo_profile"):

                ngo_profile = obj.ngo_profile

                if ngo_profile.ngo_name:

                    return ngo_profile.ngo_name

        # =============================================
        # DONOR
        # =============================================

        full_name = (
            f"{obj.first_name} "
            f"{obj.last_name}"
        ).strip()

        if full_name:

            return full_name

        # =============================================
        # FALLBACK
        # =============================================

        return obj.username

    # =================================================
    # NGO NAME
    # =================================================

    def get_ngo_name(self, obj):

        if obj.role == "NGO":

            if hasattr(obj, "ngo_profile"):

                return obj.ngo_profile.ngo_name

        return None