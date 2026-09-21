import tempfile
from pathlib import Path

from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import F

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.parsers import (
    MultiPartParser,
    FormParser
)

from rest_framework_simplejwt.tokens import RefreshToken

from ai.gemini_detector import analyze_donation_image

from .models import (
    CustomUser,
    Profile,
    NGOProfile,
    Donor,
    NGO,
    NGORequirement,
    Donation,
    DonationAllocation,
    PickupRequest,
)

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    ProfileSerializer,
    NGOProfileSerializer
)


# ============================================================
# FRONTEND PAGE VIEWS
# ============================================================

def register_page(request):
    """
    Opens the registration page.
    """
    return render(
        request,
        "register.html"
    )


def login_page(request):
    """
    Opens the common login page
    for both Donor and NGO.
    """
    return render(
        request,
        "login.html"
    )


def donor_dashboard(request):
    """
    Opens the Donor dashboard page.
    """
    return render(
        request,
        "donor_dashboard.html"
    )


def ngo_dashboard(request):
    """
    Opens the NGO dashboard page.
    """
    return render(
        request,
        "ngo_dashboard.html"
    )


# ============================================================
# REGISTRATION API
# ============================================================

class RegisterView(generics.CreateAPIView):
    """
    Common registration API.

    Handles:
    - Donor registration
    - NGO registration

    Endpoint:
        POST /api/register/
    """

    serializer_class = RegisterSerializer

    permission_classes = [
        AllowAny
    ]


# ============================================================
# LOGIN API
# ============================================================

class LoginView(APIView):
    """
    Common login API for Donor and NGO.

    Endpoint:
        POST /api/login/
    """

    permission_classes = [
        AllowAny
    ]

    def post(self, request):

        # ====================================================
        # GET LOGIN DATA
        # ====================================================

        username = request.data.get(
            "username"
        )

        password = request.data.get(
            "password"
        )

        # ====================================================
        # VALIDATE INPUT
        # ====================================================

        if not username or not password:

            return Response(
                {
                    "message":
                    "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # AUTHENTICATE USER
        # ====================================================

        user = authenticate(
            username=username,
            password=password
        )

        # ====================================================
        # INVALID LOGIN
        # ====================================================

        if user is None:

            return Response(
                {
                    "message":
                    "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ====================================================
        # CHECK USER ACTIVE STATUS
        # ====================================================

        if not user.is_active:

            return Response(
                {
                    "message":
                    "This account has been disabled."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ====================================================
        # CREATE JWT TOKENS
        # ====================================================

        refresh = RefreshToken.for_user(
            user
        )

        access_token = refresh.access_token

        # ====================================================
        # RETURN USER + TOKENS
        # ====================================================

        return Response(
            {
                "access": str(
                    access_token
                ),

                "refresh": str(
                    refresh
                ),

                "user": UserSerializer(
                    user
                ).data
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# COMMON PROFILE API
# ============================================================

class ProfileView(APIView):
    """
    Common profile API for Donor and NGO.

    JWT determines the logged-in user.

    GET:
        /api/profile/

    PUT:
        /api/profile/
    """

    permission_classes = [
        IsAuthenticated
    ]

    # ========================================================
    # GET PROFILE
    # ========================================================

    def get(self, request):

        user = request.user

        # ====================================================
        # DONOR PROFILE
        # ====================================================

        if user.role == "Donor":

            profile, created = (
                Profile.objects.get_or_create(
                    user=user
                )
            )

            serializer = ProfileSerializer(
                profile
            )

            return Response(
                {
                    "user_type": "Donor",

                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,

                        "name": (
                            f"{user.first_name} "
                            f"{user.last_name}"
                        ).strip(),

                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role
                    },

                    "profile": serializer.data
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # NGO PROFILE
        # ====================================================

        elif user.role == "NGO":

            profile, created = (
                NGOProfile.objects.get_or_create(
                    user=user
                )
            )

            serializer = NGOProfileSerializer(
                profile
            )

            display_name = (
                profile.ngo_name
                if profile.ngo_name
                else (
                    f"{user.first_name} "
                    f"{user.last_name}"
                ).strip()
            )

            return Response(
                {
                    "user_type": "NGO",

                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,

                        "name": (
                            display_name
                            if display_name
                            else user.username
                        ),

                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role
                    },

                    "profile": serializer.data
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # INVALID ROLE
        # ====================================================

        return Response(
            {
                "message":
                "Invalid user role."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    def put(self, request):

        user = request.user

        # ====================================================
        # GET NAME FIELDS
        # ====================================================

        first_name = request.data.get(
            "first_name"
        )

        last_name = request.data.get(
            "last_name"
        )

        # ====================================================
        # UPDATE USER NAME
        # ====================================================

        if first_name is not None:

            user.first_name = str(
                first_name
            ).strip()

        if last_name is not None:

            user.last_name = str(
                last_name
            ).strip()

        user.save()

        # ====================================================
        # DONOR PROFILE
        # ====================================================

        if user.role == "Donor":

            profile, created = (
                Profile.objects.get_or_create(
                    user=user
                )
            )

            serializer = ProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():

                serializer.save()

            else:

                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            display_name = (
                f"{user.first_name} "
                f"{user.last_name}"
            ).strip()

            if not display_name:

                display_name = user.username

            return Response(
                {
                    "message":
                    "Profile updated successfully.",

                    "user_type":
                    "Donor",

                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "name": display_name,
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role
                    },

                    "profile":
                    serializer.data
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # NGO PROFILE
        # ====================================================

        elif user.role == "NGO":

            profile, created = (
                NGOProfile.objects.get_or_create(
                    user=user
                )
            )

            serializer = NGOProfileSerializer(
                profile,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():

                serializer.save()

            else:

                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )

            if profile.ngo_name:

                display_name = profile.ngo_name

            else:

                display_name = (
                    f"{user.first_name} "
                    f"{user.last_name}"
                ).strip()

            if not display_name:

                display_name = user.username

            return Response(
                {
                    "message":
                    "Profile updated successfully.",

                    "user_type":
                    "NGO",

                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "name": display_name,
                        "ngo_name": profile.ngo_name,
                        "email": user.email,
                        "phone": user.phone,
                        "role": user.role
                    },

                    "profile":
                    serializer.data
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # INVALID ROLE
        # ====================================================

        return Response(
            {
                "message":
                "Invalid user role."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================================
# GEMINI AI DONATION IMAGE SCAN
# ============================================================

class AIScanView(APIView):
    """
    AI Donation Image Analysis API.

    Uses Gemini Vision to detect multiple donation items
    from a single uploaded image.

    Endpoints:

        POST /api/donations/scan/

        POST /api/donations/analyze-image/

    Request:

        multipart/form-data

        image = donation.jpg

    Authentication:

        JWT required
    """

    permission_classes = [
        IsAuthenticated
    ]

    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    def post(self, request):

        # ====================================================
        # CHECK USER ROLE
        # ====================================================

        if request.user.role != "Donor":

            return Response(
                {
                    "success": False,
                    "message":
                    "Only donors can scan donation images."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ====================================================
        # GET IMAGE
        # ====================================================

        image = request.FILES.get(
            "image"
        )

        if not image:

            return Response(
                {
                    "success": False,
                    "message":
                    "Image is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # IMAGE TYPE VALIDATION
        # ====================================================

        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp"
        ]

        if image.content_type not in allowed_types:

            return Response(
                {
                    "success": False,
                    "message":
                    "Only JPG, JPEG, PNG and WEBP images are allowed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # IMAGE SIZE VALIDATION
        # ====================================================

        max_size = 10 * 1024 * 1024

        if image.size > max_size:

            return Response(
                {
                    "success": False,
                    "message":
                    "Image size must be less than 10 MB."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ====================================================
        # TEMPORARY FILE
        # ====================================================

        temp_path = None

        try:

            # ------------------------------------------------
            # GET FILE EXTENSION
            # ------------------------------------------------

            suffix = Path(
                image.name
            ).suffix

            # ------------------------------------------------
            # CREATE TEMPORARY FILE
            # ------------------------------------------------

            with tempfile.NamedTemporaryFile(
                suffix=suffix,
                delete=False
            ) as temp_file:

                for chunk in image.chunks():

                    temp_file.write(
                        chunk
                    )

                temp_path = temp_file.name

            # =================================================
            # SEND IMAGE TO GEMINI
            # =================================================

            result = analyze_donation_image(
                temp_path
            )

            # =================================================
            # GEMINI ERROR
            # =================================================

            if not result.get(
                "success",
                False
            ):

                return Response(
                    {
                        "success": False,
                        "message":
                        result.get(
                            "message",
                            "Gemini image analysis failed."
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # =================================================
            # GET DETECTED ITEMS
            # =================================================

            items = result.get(
                "items",
                []
            )

            # =================================================
            # RETURN RESULT TO REACT
            # =================================================

            return Response(
                {
                    "success": True,

                    "message":
                    "Image analyzed successfully.",

                    "items": items,

                    "total_item_types":
                    len(items),

                    "verification_required":
                    True
                },
                status=status.HTTP_200_OK
            )

        # ====================================================
        # GENERAL ERROR
        # ====================================================

        except Exception as e:

            print(
                "GEMINI AI SCANNING ERROR:",
                str(e)
            )

            return Response(
                {
                    "success": False,

                    "message":
                    "AI image scanning failed.",

                    "details":
                    str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # ====================================================
        # CLEANUP TEMPORARY FILE
        # ====================================================

        finally:

            if temp_path:

                try:

                    Path(
                        temp_path
                    ).unlink(
                        missing_ok=True
                    )

                except Exception as cleanup_error:

                    print(
                        "Temporary file cleanup error:",
                        str(cleanup_error)
                    )


# ============================================================
# ADMIN DASHBOARD STATISTICS API
# ============================================================

def admin_dashboard_stats(request):
    """
    Returns statistics for the React Admin Dashboard.

    Endpoint:

        GET /api/admin/dashboard-stats/
    """

    # ========================================================
    # BASIC COUNTS
    # ========================================================

    total_donors = Donor.objects.count()

    total_ngos = NGO.objects.count()

    total_donations = Donation.objects.count()

    total_requirements = NGORequirement.objects.count()

    total_allocations = DonationAllocation.objects.count()

    total_pickups = PickupRequest.objects.count()


    # ========================================================
    # PENDING COUNTS
    # ========================================================

    pending_ngos = NGO.objects.filter(
        status="Pending"
    ).count()

    pending_donations = Donation.objects.filter(
        status="Pending"
    ).count()

    pending_requirements = NGORequirement.objects.filter(
        is_active=True,
        fulfilled_quantity__lt=F(
            "required_quantity"
        )
    ).count()

    pending_pickups = PickupRequest.objects.filter(
        status="Pending"
    ).count()


    # ========================================================
    # DONATION STATUS
    # ========================================================

    accepted_donations = Donation.objects.filter(
        status="Accepted"
    ).count()

    collected_donations = Donation.objects.filter(
        status="Collected"
    ).count()

    rejected_donations = Donation.objects.filter(
        status="Rejected"
    ).count()


    # ========================================================
    # PICKUP STATUS
    # ========================================================

    confirmed_pickups = PickupRequest.objects.filter(
        status="Confirmed"
    ).count()

    delivered_pickups = PickupRequest.objects.filter(
        status="Delivered"
    ).count()


    # ========================================================
    # ALLOCATION STATUS
    # ========================================================

    matched_donations = DonationAllocation.objects.count()

    completed_allocations = DonationAllocation.objects.filter(
        status="Collected"
    ).count()


    # ========================================================
    # RECENT DONATIONS
    # ========================================================

    recent_donations = Donation.objects.select_related(
        "donor",
        "ngo"
    ).order_by(
        "-donation_date"
    )[:10]


    recent_data = []

    for donation in recent_donations:

        recent_data.append({

            "id":
                donation.id,

            "item_name":
                donation.item_name,

            "category":
                donation.category,

            "quantity":
                donation.quantity,

            "condition":
                donation.condition,

            "status":
                donation.status,

            "donor":
                donation.donor.name
                if donation.donor
                else "Unknown",

            "ngo":
                donation.ngo.ngo_name
                if donation.ngo
                else None,

            "donation_date":
                donation.donation_date.isoformat(),
        })


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return JsonResponse({

        "success": True,

        "stats": {

            "total_donors":
                total_donors,

            "total_ngos":
                total_ngos,

            "total_donations":
                total_donations,

            "total_requirements":
                total_requirements,

            "total_allocations":
                total_allocations,

            "total_pickups":
                total_pickups,

            "pending_ngos":
                pending_ngos,

            "pending_donations":
                pending_donations,

            "pending_requirements":
                pending_requirements,

            "pending_pickups":
                pending_pickups,

            "accepted_donations":
                accepted_donations,

            "collected_donations":
                collected_donations,

            "rejected_donations":
                rejected_donations,

            "matched_donations":
                matched_donations,

            "completed_allocations":
                completed_allocations,

            "confirmed_pickups":
                confirmed_pickups,

            "delivered_pickups":
                delivered_pickups,
        },

        "recent_donations":
            recent_data,
    })