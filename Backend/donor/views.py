from rest_framework.permissions import BasePermission
import os
import tempfile
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.http import JsonResponse


# =========================================================
# ADMIN PERMISSION
# =========================================================

class IsAdminUser(BasePermission):
    """Allows access only to authenticated JWTs issued for admins."""

    message = "Admin access required."

    def has_permission(self, request, view):
        return bool(
            request.auth
            and str(request.auth.get("user_type", "")).strip().lower()
            == "admin"
        )
from django.db import transaction
from django.db.models import Count, Sum, F
from django.contrib.auth.hashers import check_password

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated,BasePermission
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

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

from .serializers import (
    DonorSerializer,
    NGOSerializer,
    DonationSerializer,
    LoginSerializer,
    SingleRegistrationSerializer,
    NGORequirementSerializer,
    DonationAllocationSerializer,
    PickupRequestSerializer,
)
from notifications.services import (
    notify_ai_match,
    notify_allocation_created,
    notify_donation_approved,
    notify_donation_rejected,
    notify_donation_submitted,
    notify_pickup_created,
    notify_pickup_status_changed,
)

from django.http import JsonResponse

# =========================================================
# AI DONATION IMAGE ANALYSIS API
# =========================================================

class DonationImageAnalysisView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        # =================================================
        # GET IMAGE
        # =================================================

        image = request.FILES.get("image")

        if not image:
            return Response(
                {
                    "success": False,
                    "message": "Donation image is required.",
                    "items": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # VALIDATE IMAGE TYPE
        # =================================================

        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
        ]

        if image.content_type not in allowed_types:
            return Response(
                {
                    "success": False,
                    "message":
                        "Only JPG, JPEG, PNG and WEBP images are allowed.",
                    "items": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # VALIDATE IMAGE SIZE
        # =================================================

        max_size = 10 * 1024 * 1024  # 10 MB

        if image.size > max_size:
            return Response(
                {
                    "success": False,
                    "message":
                        "Image size must be less than 10 MB.",
                    "items": []
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        temporary_file = None

        try:

            # =================================================
            # CREATE TEMPORARY FILE
            # =================================================

            extension = os.path.splitext(
                image.name
            )[1]

            temporary_file = tempfile.NamedTemporaryFile(
                suffix=extension,
                delete=False
            )

            for chunk in image.chunks():
                temporary_file.write(chunk)

            temporary_file.close()

            # =================================================
            # IMPORT AI SCANNER
            # =================================================

            from ai.image_scanner import scan_image

            # =================================================
            # SEND IMAGE TO AI
            # =================================================

            result = scan_image(
                temporary_file.name
            )

            print(
                "========== AI RESULT =========="
            )
            print(result)
            print(
                "==============================="
            )

            # =================================================
            # CHECK AI RESULT
            # =================================================

            if not result.get("success"):
                return Response(
                    {
                        "success": False,
                        "message":
                            result.get(
                                "message",
                                "AI could not analyze the image."
                            ),
                        "items": []
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # =================================================
            # RETURN AI RESULT
            # =================================================

            return Response(
                {
                    "success": True,
                    "items":
                        result.get(
                            "items",
                            []
                        )
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            print(
                "========== AI API ERROR =========="
            )

            print(str(e))

            print(
                "=================================="
            )

            return Response(
                {
                    "success": False,
                    "message":
                        "AI image analysis failed.",
                    "items": []
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        finally:

            # =================================================
            # DELETE TEMPORARY FILE
            # =================================================

            if (
                temporary_file
                and os.path.exists(
                    temporary_file.name
                )
            ):
                os.remove(
                    temporary_file.name
                )


# =========================================================
# DASHBOARD API
# =========================================================

def dashboard(request):

    total_quantity = (
        Donation.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    data = {
        "total_donors":
            Donor.objects.count(),

        "total_ngos":
            NGO.objects.count(),

        "total_donations":
            Donation.objects.count(),

        "pending_donations":
            Donation.objects.filter(
                status="Pending"
            ).count(),

        "accepted_donations":
            Donation.objects.filter(
                status="Accepted"
            ).count(),

        "rejected_donations":
            Donation.objects.filter(
                status="Rejected"
            ).count(),

        "collected_donations":
            Donation.objects.filter(
                status="Collected"
            ).count(),

        "total_items":
            total_quantity,
    }

    return JsonResponse(data)


# =========================================================
# SINGLE REGISTRATION API
# =========================================================

class RegistrationView(APIView):

    def post(self, request):

        # =================================================
        # DEBUG
        # =================================================

        print(
            "========== REGISTER REQUEST =========="
        )

        print(
            "DATA:",
            request.data
        )

        print(
            "FILES:",
            request.FILES
        )

        print(
            "======================================"
        )

        # =================================================
        # USER TYPE
        # =================================================

        user_type = request.data.get(
            "user_type"
        )

        if not user_type:

            return Response(
                {
                    "message":
                        "User type is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # DONOR REGISTRATION
        # =================================================

        if user_type == "donor":

            # -------------------------------------------------
            # Donor registration normally uses JSON
            # -------------------------------------------------

            data = request.data.get(
                "data"
            )

            if not data:

                return Response(
                    {
                        "message":
                            "Donor registration data is required."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            donor_serializer = DonorSerializer(
                data=data
            )

            if donor_serializer.is_valid():

                donor = donor_serializer.save()

                return Response(
                    {
                        "message":
                            "Donor Registered Successfully",

                        "user_type":
                            "Donor",

                        "id":
                            donor.id,

                        "name":
                            donor.name,

                        "email":
                            donor.email,
                    },
                    status=status.HTTP_201_CREATED
                )

            print(
                "DONOR SERIALIZER ERRORS:",
                donor_serializer.errors
            )

            return Response(
                donor_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # NGO REGISTRATION
        # =================================================

        elif user_type == "ngo":

            # -------------------------------------------------
            # NGO uses multipart/form-data.
            #
            # request.data contains normal fields.
            # request.FILES contains uploaded files.
            # -------------------------------------------------

            data = request.data.copy()

            # -------------------------------------------------
            # Remove user_type because it is not an NGO model
            # field.
            # -------------------------------------------------

            data.pop(
                "user_type",
                None
            )

            # =================================================
            # NGO LOGO
            # =================================================

            if "picture" in request.FILES:

                data["picture"] = request.FILES[
                    "picture"
                ]

            # =================================================
            # NGO CERTIFICATE
            # =================================================

            if "certificate_files" in request.FILES:

                data["certificate_files"] = request.FILES[
                    "certificate_files"
                ]

            # =================================================
            # DEBUG NGO DATA
            # =================================================

            print(
                "========== NGO DATA =========="
            )

            print(
                "NGO DATA:",
                data
            )

            print(
                "NGO FILES:",
                request.FILES
            )

            print(
                "=============================="
            )

            # =================================================
            # NGO SERIALIZER
            # =================================================

            ngo_serializer = NGOSerializer(
                data=data
            )

            # =================================================
            # VALIDATE AND SAVE
            # =================================================

            if ngo_serializer.is_valid():

                ngo = ngo_serializer.save()

                return Response(
                    {
                        "message":
                            "NGO Registered Successfully",

                        "user_type":
                            "NGO",

                        "id":
                            ngo.id,

                        "name":
                            ngo.ngo_name,

                        "email":
                            ngo.email_id,

                        "status":
                            ngo.status,

                        "certificate":
                            (
                                ngo.certificate_files.url
                                if ngo.certificate_files
                                else None
                            ),

                        "picture":
                            (
                                ngo.picture.url
                                if ngo.picture
                                else None
                            ),
                    },
                    status=status.HTTP_201_CREATED
                )

            # =================================================
            # NGO VALIDATION ERRORS
            # =================================================

            print(
                "========== NGO SERIALIZER ERRORS =========="
            )

            print(
                ngo_serializer.errors
            )

            print(
                "==========================================="
            )

            return Response(
                ngo_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # =================================================
        # INVALID USER TYPE
        # =================================================

        return Response(
            {
                "message":
                    "Invalid user type."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# DONOR API
# =========================================================

class DonorDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Donor.objects.all()

    serializer_class = DonorSerializer


# =========================================================
# APPROVED NGO LIST API
# =========================================================

class ApprovedNGOListView(APIView):

    permission_classes = [
        AllowAny
    ]

    def get(self, request):

        ngos = NGO.objects.filter(
            status="Approved"
        ).order_by(
            "ngo_name"
        )

        serializer = NGOSerializer(
            ngos,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =========================================================
# NGO CREATE API
# =========================================================

class NGOCreateView(
    generics.ListCreateAPIView
):

    queryset = NGO.objects.all()

    serializer_class = NGOSerializer


# =========================================================
# NGO DETAIL API
# =========================================================

class NGODetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = NGO.objects.all()

    serializer_class = NGOSerializer


# =========================================================
# ITEM DONATION API
# =========================================================

class DonationCreateView(
    generics.ListCreateAPIView
):

    queryset = Donation.objects.select_related(
        "donor",
        "ngo"
    ).all()

    serializer_class = DonationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def perform_create(
        self,
        serializer
    ):

        user_id = self.request.auth.get(
            "user_id"
        )

        user_type = self.request.auth.get(
            "user_type"
        )

        # -------------------------------------------------
        # ONLY DONORS CAN CREATE DONATIONS
        # -------------------------------------------------

        if user_type != "Donor":

            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied(
                "Only donors can donate items."
            )

        # -------------------------------------------------
        # FIND LOGGED-IN DONOR
        # -------------------------------------------------

        try:

            donor = Donor.objects.get(
                id=user_id
            )

        except Donor.DoesNotExist:

            from rest_framework.exceptions import NotFound

            raise NotFound(
                "Donor not found."
            )

        # -------------------------------------------------
        # SAVE DONATION
        # -------------------------------------------------

        donation = serializer.save(
            donor=donor
        )
        notify_donation_submitted(donation)


# =========================================================
# DONATION DETAIL API
# =========================================================

class DonationDetailView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Donation.objects.select_related(
        "donor",
        "ngo"
    ).all()

    serializer_class = DonationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    # -----------------------------------------------------
    # DONOR OWNERSHIP
    # -----------------------------------------------------

    def get_queryset(self):
        user_id = self.request.auth.get("user_id")
        user_type = self.request.auth.get("user_type")

        if user_type == "Donor":
            return self.queryset.filter(
                donor_id=user_id
            )

        return self.queryset.none()

    # -----------------------------------------------------
    # DELETE DONATION
    # -----------------------------------------------------
    #
    # A donor can delete only Pending/Rejected donations.
    #
    # IMPORTANT:
    # Deleting the Donation must also remove everything that
    # was created for that donation on the NGO side:
    #
    #   Donation
    #       ↓
    #   DonationAllocation(s)
    #       ↓
    #   PickupRequest(s)
    #
    # Accepted/Collected donations are locked and cannot be
    # deleted because the NGO may already have fulfilled the
    # requirement and started the pickup process.
    # -----------------------------------------------------

    def destroy(self, request, *args, **kwargs):

        donation = self.get_object()

        if donation.status in [
            "Accepted",
            "Collected"
        ]:
            return Response(
                {
                    "message":
                        "Accepted or collected donations cannot be deleted."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():

            # -------------------------------------------------
            # GET ALL ALLOCATIONS FOR THIS DONATION
            # -------------------------------------------------
            #
            # Do this explicitly instead of relying only on
            # database CASCADE so that all related pickup
            # requests are removed first and no orphaned NGO
            # pickup data can remain.
            # -------------------------------------------------

            allocations = list(
                DonationAllocation.objects.filter(
                    donation=donation
                ).only("id")
            )

            allocation_ids = [
                allocation.id
                for allocation in allocations
            ]

            # -------------------------------------------------
            # DELETE PICKUP REQUESTS
            # -------------------------------------------------
            #
            # Pickup belongs to an allocation. If the donor
            # deletes the donation, its pickup must disappear
            # from both donor and NGO pickup screens.
            # -------------------------------------------------

            if allocation_ids:
                PickupRequest.objects.filter(
                    allocation_id__in=allocation_ids
                ).delete()

            # -------------------------------------------------
            # DELETE DONATION ALLOCATIONS
            # -------------------------------------------------
            #
            # This removes the NGO-side donation request.
            # The NGO itself is NOT deleted.
            # -------------------------------------------------

            DonationAllocation.objects.filter(
                donation=donation
            ).delete()

            # -------------------------------------------------
            # DELETE DONATION
            # -------------------------------------------------

            donation.delete()

        return Response(
            {
                "message":
                    "Donation deleted successfully. "
                    "Related NGO allocation and pickup request were also removed."
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# PROFILE API
# =========================================================

@api_view(["GET"])
@permission_classes([
    IsAuthenticated
])
def profile(request):

    user_id = request.auth.get(
        "user_id"
    )

    user_type = request.auth.get(
        "user_type"
    )

    # =====================================================
    # DONOR PROFILE
    # =====================================================

    if user_type == "Donor":

        try:

            donor = Donor.objects.get(
                id=user_id
            )

            return Response(
                {
                    "message":
                        "Profile API Working Successfully",

                    "user_type":
                        "Donor",

                    "id":
                        donor.id,

                    "name":
                        donor.name,

                    "email":
                        donor.email,

                    "phone":
                        donor.phone,

                    "address":
                        donor.address,

                    "city":
                        donor.city,

                    "state":
                        donor.state,

                    "pincode":
                        donor.pincode,

                    "language":
                        donor.language_preference,

                    "status_active":
                        donor.status_active,

                    "picture":
                        (
                            request.build_absolute_uri(
                                donor.picture.url
                            )
                            if donor.picture
                            else None
                        ),
                }
            )

        except Donor.DoesNotExist:

            return Response(
                {
                    "message":
                        "Donor not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    # =====================================================
    # NGO PROFILE
    # =====================================================

    elif user_type == "NGO":

        try:

            ngo = NGO.objects.get(
                id=user_id
            )

            return Response(
                {
                    "message":
                        "Profile API Working Successfully",

                    "user_type":
                        "NGO",

                    "id":
                        ngo.id,

                    "ngo_name":
                        ngo.ngo_name,

                    "description":
                        ngo.description,

                    "registration_no":
                        ngo.registration_no,

                    "email_id":
                        ngo.email_id,

                    "phone_no":
                        ngo.phone_no,

                    "website_link":
                        ngo.website_link,

                    "address":
                        ngo.address,

                    "city":
                        ngo.city,

                    "state":
                        ngo.state,

                    "pincode":
                        ngo.pincode,

                    "language":
                        ngo.language,

                    "status":
                        ngo.status,

                    "picture":
                        (
                            request.build_absolute_uri(
                                ngo.picture.url
                            )
                            if ngo.picture
                            else None
                        ),

                    "certificate_files":
                        (
                            request.build_absolute_uri(
                                ngo.certificate_files.url
                            )
                            if ngo.certificate_files
                            else None
                        ),
                }
            )

        except NGO.DoesNotExist:

            return Response(
                {
                    "message":
                        "NGO not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    # =====================================================
    # INVALID USER TYPE
    # =====================================================

    return Response(
        {
            "message":
                "Invalid user type"
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# PROFILE IMAGE UPLOAD API
# =========================================================

@api_view(["POST"])
@permission_classes([
    IsAuthenticated
])
def upload_profile_image(request):

    user_id = request.auth.get(
        "user_id"
    )

    user_type = request.auth.get(
        "user_type"
    )

    # -----------------------------------------------------
    # CHECK FILE
    # -----------------------------------------------------

    if "picture" not in request.FILES:

        return Response(
            {
                "message":
                    "Please select an image."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # =====================================================
    # DONOR
    # =====================================================

    if user_type == "Donor":

        try:

            donor = Donor.objects.get(
                id=user_id
            )

            donor.picture = request.FILES[
                "picture"
            ]

            donor.save()

            return Response(
                {
                    "message":
                        "Profile image uploaded successfully",

                    "image":
                        donor.picture.url
                }
            )

        except Donor.DoesNotExist:

            return Response(
                {
                    "message":
                        "Donor not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    # =====================================================
    # NGO
    # =====================================================

    elif user_type == "NGO":

        try:

            ngo = NGO.objects.get(
                id=user_id
            )

            ngo.picture = request.FILES[
                "picture"
            ]

            ngo.save()

            return Response(
                {
                    "message":
                        "Profile image uploaded successfully",

                    "image":
                        ngo.picture.url
                }
            )

        except NGO.DoesNotExist:

            return Response(
                {
                    "message":
                        "NGO not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )

    # =====================================================
    # INVALID USER TYPE
    # =====================================================

    return Response(
        {
            "message":
                "Invalid user type"
        },
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# NGO CERTIFICATE UPLOAD API
# =========================================================

@api_view(["POST"])
@permission_classes([
    IsAuthenticated
])
def upload_ngo_certificate(request):

    user_id = request.auth.get(
        "user_id"
    )

    user_type = request.auth.get(
        "user_type"
    )

    # -----------------------------------------------------
    # ONLY NGO
    # -----------------------------------------------------

    if user_type != "NGO":

        return Response(
            {
                "message":
                    "Only NGOs can upload certificates."
            },
            status=status.HTTP_403_FORBIDDEN
        )

    try:

        ngo = NGO.objects.get(
            id=user_id
        )

        # -------------------------------------------------
        # CHECK CERTIFICATE
        # -------------------------------------------------

        if "certificate_files" not in request.FILES:

            return Response(
                {
                    "message":
                        "Please select a certificate file."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------
        # SAVE CERTIFICATE
        # -------------------------------------------------

        ngo.certificate_files = request.FILES[
            "certificate_files"
        ]

        ngo.save()

        return Response(
            {
                "message":
                    "Certificate uploaded successfully",

                "certificate":
                    ngo.certificate_files.url
            }
        )

    except NGO.DoesNotExist:

        return Response(
            {
                "message":
                    "NGO not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )


# =========================================================
# LOGIN API WITH JWT
# =========================================================

class LoginView(APIView):

    def get_tokens_for_user(
        self,
        user_id,
        user_type
    ):

        refresh = RefreshToken()

        refresh["user_id"] = user_id

        refresh["user_type"] = user_type

        return {
            "refresh":
                str(refresh),

            "access":
                str(
                    refresh.access_token
                )
        }

    def post(self, request):

        serializer = LoginSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data[
            "email"
        ]

        password = serializer.validated_data[
            "password"
        ]

        # =================================================
        # ADMIN LOGIN
        # =================================================
        #
        # Admin uses Django's built-in User table.
        #
        # A Django superuser/staff user created using:
        #
        # python manage.py createsuperuser
        #
        # can login through the React Admin Login.
        # =================================================

        try:

            admin_user = User.objects.filter(
                email__iexact=email,
                is_active=True
            ).first()

            if (
                admin_user
                and (
                    admin_user.is_staff
                    or admin_user.is_superuser
                )
                and admin_user.check_password(
                    password
                )
            ):

                tokens = self.get_tokens_for_user(
                    admin_user.id,
                    "Admin"
                )

                return Response(
                    {
                        "message":
                            "Admin Login Successful",

                        "user_type":
                            "Admin",

                        "user_id":
                            admin_user.id,

                        "name":
                            admin_user.get_full_name()
                            or admin_user.username,

                        "email":
                            admin_user.email,

                        "tokens":
                            tokens
                    },
                    status=status.HTTP_200_OK
                )

        except Exception as e:

            print(
                "ADMIN LOGIN ERROR:",
                str(e)
            )

        # =================================================
        # DONOR LOGIN
        # =================================================

        try:

            donor = Donor.objects.get(
                email=email
            )

            if check_password(
                password,
                donor.password
            ):

                tokens = self.get_tokens_for_user(
                    donor.id,
                    "Donor"
                )

                return Response(
                    {
                        "message":
                            "Login Successful",

                        "user_type":
                            "Donor",

                        "user_id":
                            donor.id,

                        "name":
                            donor.name,

                        "email":
                            donor.email,

                        "tokens":
                            tokens
                    },
                    status=status.HTTP_200_OK
                )

        except Donor.DoesNotExist:

            pass

        # =================================================
        # NGO LOGIN
        # =================================================

        try:

            ngo = NGO.objects.get(
                email_id=email
            )

            if check_password(
                password,
                ngo.password
            ):

                tokens = self.get_tokens_for_user(
                    ngo.id,
                    "NGO"
                )

                return Response(
                    {
                        "message":
                            "Login Successful",

                        "user_type":
                            "NGO",

                        "user_id":
                            ngo.id,

                        "name":
                            ngo.ngo_name,

                        "email":
                            ngo.email_id,

                        "tokens":
                            tokens
                    },
                    status=status.HTTP_200_OK
                )

        except NGO.DoesNotExist:

            pass

        # =================================================
        # INVALID LOGIN
        # =================================================

        return Response(
            {
                "message":
                    "Invalid Email or Password"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
# =========================================================
# NGO DONATION REQUESTS
# =========================================================

class NGODonationListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_id = request.auth.get(
            "user_id"
        )

        user_type = request.auth.get(
            "user_type"
        )

        # -------------------------------------------------
        # ONLY NGO
        # -------------------------------------------------

        if user_type != "NGO":

            return Response(
                {
                    "message":
                        "Only NGOs can view donation requests."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # FIND NGO
        # -------------------------------------------------

        try:

            ngo = NGO.objects.get(
                id=user_id
            )

        except NGO.DoesNotExist:

            return Response(
                {
                    "message":
                        "NGO not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # GET NGO DONATIONS
        # -------------------------------------------------

        donations = Donation.objects.filter(
            ngo=ngo
        ).select_related(
            "donor",
            "ngo"
        ).order_by(
            "-donation_date"
        )

        serializer = DonationSerializer(
            donations,
            many=True
        )

        return Response(
            serializer.data
        )


# =========================================================
# NGO DONATION STATUS UPDATE
# =========================================================
#
# Allowed donation status flow:
#
# Pending  -> Accepted
# Pending  -> Rejected
# Accepted -> Collected
#
# =========================================================

class DonationStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def patch(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        # -------------------------------------------------
        # ONLY NGO
        # -------------------------------------------------

        if user_type != "NGO":

            return Response(
                {
                    "message":
                        "Only NGOs can update donation status."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # FIND NGO
        # -------------------------------------------------

        try:

            ngo = NGO.objects.get(
                id=user_id
            )

        except NGO.DoesNotExist:

            return Response(
                {
                    "message":
                        "NGO not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # GET NEW STATUS
        # -------------------------------------------------

        new_status = str(
            request.data.get(
                "status",
                ""
            )
        ).strip()

        # -------------------------------------------------
        # ALLOWED STATUSES
        # -------------------------------------------------

        if new_status not in [
            "Accepted",
            "Rejected",
            "Collected"
        ]:

            return Response(
                {
                    "message":
                        "Only Accepted, Rejected or Collected is allowed here."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------
        # FIND DONATION
        # -------------------------------------------------

        try:

            donation = Donation.objects.get(
                id=pk
            )

        except Donation.DoesNotExist:

            return Response(
                {
                    "message":
                        "Donation not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # NGO OWNERSHIP
        # -------------------------------------------------
        #
        # The donation can be connected to the NGO through:
        #
        # 1. Donation.ngo
        # 2. DonationAllocation
        #
        # The allocation is important for the new
        # donation-matching system.
        # -------------------------------------------------

        if (
            donation.ngo_id is not None
            and donation.ngo_id != ngo.id
        ):

            return Response(
                {
                    "message":
                        "You are not authorized to update this donation."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # ACCEPT / REJECT
        # -------------------------------------------------

        if new_status in [
            "Accepted",
            "Rejected"
        ]:

            # Donation must currently be Pending.

            if donation.status != "Pending":

                return Response(
                    {
                        "message":
                            f"Donation is already "
                            f"'{donation.status}' "
                            "and cannot be changed."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # -------------------------------------------------
            # FIND THIS NGO'S PENDING ALLOCATION
            # -------------------------------------------------

            allocations = list(
                DonationAllocation.objects.filter(
                    donation=donation,
                    ngo=ngo,
                    status="Pending"
                )
            )

            if not allocations:

                return Response(
                    {
                        "message":
                            "No pending donation allocation exists for this NGO."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # -------------------------------------------------
            # REJECT
            # -------------------------------------------------

            if new_status == "Rejected":

                pending_allocations = list(
                    DonationAllocation.objects.filter(
                        donation=donation,
                        status="Pending"
                    )
                )

                pending_allocation_ids = [
                    allocation.id
                    for allocation in pending_allocations
                ]

                # Cancel related pending pickups.

                cancelled_pickups = []

                if pending_allocation_ids:
                    cancelled_pickups = list(
                        PickupRequest.objects.select_related(
                            "allocation",
                            "allocation__donation",
                            "allocation__ngo",
                        ).filter(
                            allocation_id__in=pending_allocation_ids,
                            status="Pending",
                        )
                    )

                    PickupRequest.objects.filter(
                        id__in=[
                            pickup.id
                            for pickup in cancelled_pickups
                        ]
                    ).update(
                        status="Cancelled"
                    )



                # Reject all pending allocations.

                DonationAllocation.objects.filter(
                    donation=donation,
                    status="Pending"
                ).update(
                    status="Rejected"
                )

                donation.status = "Rejected"

                donation.save(
                    update_fields=[
                        "status"
                    ]
                )

                notify_donation_rejected(donation)
                for pickup in cancelled_pickups:
                    pickup.status = "Cancelled"
                    notify_pickup_status_changed(pickup, changed_by="NGO")

                return Response(
                    {
                        "message":
                            "Donation rejected successfully.",

                        "donation_id":
                            donation.id,

                        "status":
                            donation.status
                    },
                    status=status.HTTP_200_OK
                )

            # -------------------------------------------------
            # ACCEPT
            # -------------------------------------------------

            with transaction.atomic():

                for allocation in allocations:

                    try:

                        requirement = NGORequirement.objects.get(
                            id=allocation.requirement_id
                        )

                    except NGORequirement.DoesNotExist:

                        return Response(
                            {
                                "message":
                                    "The selected NGO requirement "
                                    "no longer exists."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # -------------------------------------------------
                    # CHECK REMAINING REQUIREMENT
                    # -------------------------------------------------

                    remaining_need = (
                        requirement.required_quantity
                        - requirement.fulfilled_quantity
                    )

                    if remaining_need <= 0:

                        return Response(
                            {
                                "message":
                                    f"The requirement for "
                                    f"{requirement.item_name} "
                                    "is already fulfilled."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if (
                        allocation.allocated_quantity
                        > remaining_need
                    ):

                        return Response(
                            {
                                "message":
                                    f"The NGO currently needs only "
                                    f"{remaining_need} units of "
                                    f"{requirement.item_name}."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # -------------------------------------------------
                    # UPDATE REQUIREMENT
                    # -------------------------------------------------

                    requirement.fulfilled_quantity += (
                        allocation.allocated_quantity
                    )

                    requirement.save(
                        update_fields=[
                            "fulfilled_quantity",
                            "updated_at"
                        ]
                    )

                    # -------------------------------------------------
                    # ACCEPT ALLOCATION
                    # -------------------------------------------------

                    allocation.status = "Accepted"

                    allocation.save(
                        update_fields=[
                            "status"
                        ]
                    )

                # -------------------------------------------------
                # REJECT OTHER NGO ALLOCATIONS
                # -------------------------------------------------

                other_pending_allocations = list(
                    DonationAllocation.objects.filter(
                        donation=donation,
                        status="Pending"
                    ).exclude(
                        ngo=ngo
                    )
                )

                other_pending_allocation_ids = [
                    allocation.id
                    for allocation
                    in other_pending_allocations
                ]

                if other_pending_allocation_ids:

                    PickupRequest.objects.filter(
                        allocation_id__in=(
                            other_pending_allocation_ids
                        ),
                        status="Pending"
                    ).update(
                        status="Cancelled"
                    )

                DonationAllocation.objects.filter(
                    donation=donation,
                    status="Pending"
                ).exclude(
                    ngo=ngo
                ).update(
                    status="Rejected"
                )

                # -------------------------------------------------
                # UPDATE DONATION
                # -------------------------------------------------

                donation.ngo = ngo

                donation.status = "Accepted"

                donation.save(
                    update_fields=[
                        "ngo",
                        "status"
                    ]
                )

            return Response(
                {
                    "message":
                        "Donation accepted successfully. "
                        "Requirement quantity has been updated.",

                    "donation_id":
                        donation.id,

                    "status":
                        donation.status
                },
                status=status.HTTP_200_OK
            )

        # =================================================
        # MARK COLLECTED
        # =================================================

        if new_status == "Collected":

            # -------------------------------------------------
            # ONLY ACCEPTED DONATIONS CAN BE COLLECTED
            # -------------------------------------------------

            if donation.status != "Accepted":

                return Response(
                    {
                        "message":
                            f"Only an Accepted donation can be "
                            f"marked as Collected. "
                            f"Current status: '{donation.status}'."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # -------------------------------------------------
            # MAKE SURE THIS NGO OWNS THE ACCEPTED DONATION
            # -------------------------------------------------

            accepted_allocation = (
                DonationAllocation.objects.filter(
                    donation=donation,
                    ngo=ngo,
                    status="Accepted"
                ).exists()
            )

            if not accepted_allocation:

                return Response(
                    {
                        "message":
                            "You are not authorized to collect this donation."
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            # -------------------------------------------------
            # MARK DONATION COLLECTED
            # -------------------------------------------------

            donation.status = "Collected"

            donation.save(
                update_fields=[
                    "status"
                ]
            )

            return Response(
                {
                    "message":
                        "Donation marked as collected successfully.",

                    "donation_id":
                        donation.id,

                    "status":
                        donation.status
                },
                status=status.HTTP_200_OK
            )

# =========================================================
# DONOR MY DONATIONS
# =========================================================

# =========================================================
# DONOR LEADERBOARD
# =========================================================

class DonorRankingView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_type = str(
            request.auth.get("user_type", "")
        ).strip().lower()

        if user_type not in ["donor", "ngo", "admin"]:

            return Response(
                {
                    "message": "Only donors, NGOs and admins can view donor rankings."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        ranked_donors = (
            Donor.objects.filter(
                donations__status="Collected"
            )
            .annotate(
                total_donation=Sum("donations__quantity"),
                donation_count=Count("donations")
            )
            .order_by(
                "-total_donation",
                "-donation_count",
                "name",
                "id"
            )
        )

        rankings = []
        current_donor = None
        current_donor_id = request.auth.get("user_id")

        for rank, donor in enumerate(ranked_donors, start=1):

            ranking = {
                "rank": rank,
                "donor_id": donor.id,
                "donor_name": donor.name,
                "total_donation": donor.total_donation,
                "total_quantity": donor.total_donation,
                "donation_count": donor.donation_count,
                "status": "Active" if donor.status_active else "Inactive",
            }

            rankings.append(ranking)

            if (
                user_type == "donor"
                and donor.id == current_donor_id
            ):
                current_donor = ranking

        return Response(
            {
                "rankings": rankings,
                "current_donor": current_donor,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# DONOR MY DONATIONS
# =========================================================

class DonorDonationListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_id = request.auth.get(
            "user_id"
        )

        user_type = request.auth.get(
            "user_type"
        )

        # -------------------------------------------------
        # ONLY DONORS
        # -------------------------------------------------

        if user_type != "Donor":

            return Response(
                {
                    "message":
                        "Only donors can view their donations."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # FIND DONOR
        # -------------------------------------------------

        try:

            donor = Donor.objects.get(
                id=user_id
            )

        except Donor.DoesNotExist:

            return Response(
                {
                    "message":
                        "Donor not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # GET DONATIONS
        # -------------------------------------------------

        donations = Donation.objects.filter(
            donor=donor
        ).select_related(
            "donor",
            "ngo"
        ).order_by(
            "-donation_date"
        )

        serializer = DonationSerializer(
            donations,
            many=True
        )

        return Response(
            serializer.data
        )


# =========================================================
# NGO REQUIREMENT API
# =========================================================

class NGORequirementListCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # -----------------------------------------------------
    # GET NGO REQUIREMENTS
    # -----------------------------------------------------

    def get(self, request):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {
                    "message":
                        "Only NGOs can view requirements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            ngo = NGO.objects.get(id=user_id)
        except NGO.DoesNotExist:
            return Response(
                {
                    "message": "NGO not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        requirements = NGORequirement.objects.filter(
            ngo=ngo
        ).order_by("-created_at")

        serializer = NGORequirementSerializer(
            requirements,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # -----------------------------------------------------
    # CREATE REQUIREMENT
    # -----------------------------------------------------

    def post(self, request):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {
                    "message":
                        "Only NGOs can create requirements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            ngo = NGO.objects.get(id=user_id)
        except NGO.DoesNotExist:
            return Response(
                {
                    "message": "NGO not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if ngo.status != "Approved":
            return Response(
                {
                    "message":
                        "Only approved NGOs can create requirements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        data.pop("ngo", None)

        serializer = NGORequirementSerializer(
            data=data
        )

        if serializer.is_valid():
            requirement = serializer.save(
                ngo=ngo
            )

            return Response(
                NGORequirementSerializer(
                    requirement
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# NGO REQUIREMENT DETAIL API
# =========================================================

class NGORequirementDetailView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # -----------------------------------------------------
    # GET
    # -----------------------------------------------------

    def get(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {
                    "message":
                        "Only NGOs can view requirements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            requirement = NGORequirement.objects.get(
                id=pk,
                ngo_id=user_id
            )
        except NGORequirement.DoesNotExist:
            return Response(
                {
                    "message":
                        "Requirement not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NGORequirementSerializer(
            requirement
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    # -----------------------------------------------------
    # UPDATE
    # -----------------------------------------------------

    def put(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {
                    "message":
                        "Only NGOs can update requirements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            requirement = NGORequirement.objects.get(
                id=pk,
                ngo_id=user_id
            )
        except NGORequirement.DoesNotExist:
            return Response(
                {
                    "message":
                        "Requirement not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NGORequirementSerializer(
            requirement,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    def delete(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {
                    "message":
                        "Only NGOs can delete requirements."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            requirement = NGORequirement.objects.get(
                id=pk,
                ngo_id=user_id
            )
        except NGORequirement.DoesNotExist:
            return Response(
                {
                    "message":
                        "Requirement not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        requirement.delete()

        return Response(
            {
                "message":
                    "Requirement deleted successfully."
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# ITEM / PRIORITY MATCHING HELPERS
# =========================================================

def normalize_item_name(name):
    """
    Normalize an item name for requirement matching.

    This is intentionally item-agnostic. It does not contain a list of
    donation items. It only removes formatting differences such as:
        "Blankets" -> "blanket"
        "BOOKS"    -> "book"
        "Rice Bag" -> "rice bag"
    """
    value = normalize_requirement_item_name(name)

    if not value:
        return ""

    # Remove punctuation that commonly appears in AI-generated names.
    value = "".join(
        char if char.isalnum() or char.isspace() else " "
        for char in value
    )

    value = " ".join(value.split())

    # Generic singular/plural normalization.
    if value.endswith("ies") and len(value) > 3:
        value = value[:-3] + "y"
    elif (
        value.endswith("s")
        and not value.endswith(("ss", "us", "is"))
        and len(value) > 3
    ):
        value = value[:-1]

    return value


def item_names_match(donation_name, requirement_name):
    """
    Match a requirement against any item detected in a donation.

    Donation item_name may contain multiple comma-separated AI detections.
    """
    requirement_item = normalize_item_name(requirement_name)

    if not requirement_item:
        return False

    donation_items = [
        normalize_item_name(item)
        for item in str(donation_name or "").split(",")
    ]

    donation_items = [
        item for item in donation_items
        if item
    ]

    return any(
        item == requirement_item
        or item.startswith(requirement_item + " ")
        or requirement_item.startswith(item + " ")
        for item in donation_items
    )


def normalize_category(category):
    """
    Normalize category labels without changing the stored database value.
    """
    return normalize_requirement_category(category).lower()


def categories_match(
    donation_category,
    requirement_category,
    donation_name=""
):
    """
    Category is a secondary check.

    If both sides have a meaningful category, they must agree.
    If either side is Other/blank, item-name matching is allowed to decide
    the match. This prevents valid new donation items from disappearing
    merely because the frontend/AI does not know a category yet.
    """
    donation = normalize_category(donation_category)
    requirement = normalize_category(requirement_category)

    if not donation or donation == "other":
        return True

    if not requirement or requirement == "other":
        return True

    return donation == requirement


# User-requested AI priority order:
# High > Medium > Low
#
# Urgent is kept as a valid database value, but because the
# requested order explicitly starts with High, it is placed
# after Low unless the requirement is changed later.
AI_PRIORITY_SCORES = {
    "high": 100,
    "medium": 80,
    "low": 60,
    "urgent": 40,
}


# =========================================================
# MATCHING NGO API
# =========================================================

class MatchingNGOView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "Donor":
            return Response(
                {
                    "message":
                        "Only donors can find matching NGOs."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            donation = Donation.objects.get(
                id=pk,
                donor_id=user_id
            )
        except Donation.DoesNotExist:
            return Response(
                {
                    "message":
                        "Donation not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # CATEGORY + ACTIVE + APPROVED NGO
        # -------------------------------------------------

        requirements = (
            NGORequirement.objects
            .filter(
                is_active=True,
                ngo__status="Approved"
            )
            .select_related("ngo")
        )

        matches = []

        print(
            "========== DONATION REQUIREMENT MATCHING =========="
        )
        print("Donation item:", donation.item_name)
        print("Donation category:", donation.category)

        for requirement in requirements:

            print(
                "Checking requirement:",
                requirement.id,
                requirement.item_name,
                requirement.category,
            )

            # Generic item-name matching
            if not item_names_match(
                donation.item_name,
                requirement.item_name
            ):
                continue

            if not categories_match(
                donation.category,
                requirement.category,
                donation.item_name
            ):
                continue

            remaining_need = (
                requirement.required_quantity
                - requirement.fulfilled_quantity
            )

            if remaining_need <= 0:
                continue

            matches.append(
                {
                    "requirement_id":
                        requirement.id,

                    "ngo_id":
                        requirement.ngo.id,

                    "ngo_name":
                        requirement.ngo.ngo_name,

                    "city":
                        requirement.ngo.city,

                    "state":
                        requirement.ngo.state,

                    "item_name":
                        requirement.item_name,

                    "category":
                        requirement.category,

                    "required_quantity":
                        requirement.required_quantity,

                    "fulfilled_quantity":
                        requirement.fulfilled_quantity,

                    "remaining_need":
                        remaining_need,

                    "can_receive":
                        min(
                            donation.quantity,
                            remaining_need
                        ),

                    "priority":
                        requirement.priority,
                }
            )

        # High > Medium > Low > Urgent
        matches.sort(
            key=lambda x: (
                AI_PRIORITY_SCORES.get(
                    str(x["priority"]).strip().lower(),
                    0
                ),
                x["remaining_need"]
            ),
            reverse=True
        )

        return Response(
            {
                "donation_id":
                    donation.id,

                "item_name":
                    donation.item_name,

                "category":
                    donation.category,

                "donation_quantity":
                    donation.quantity,

                "matching_ngos":
                    matches
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# AI MATCHING NGO API
# =========================================================

class AIMatchView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        # -------------------------------------------------
        # ONLY DONORS
        # -------------------------------------------------

        if user_type != "Donor":
            return Response(
                {
                    "message":
                        "Only donors can use AI matching."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # FIND DONATION
        # -------------------------------------------------

        try:
            donation = Donation.objects.get(
                id=pk,
                donor_id=user_id
            )
        except Donation.DoesNotExist:
            return Response(
                {
                    "message":
                        "Donation not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # FIND ACTIVE NGO REQUIREMENTS
        # -------------------------------------------------

        requirements = (
            NGORequirement.objects
            .filter(
                is_active=True,
                ngo__status="Approved"
            )
            .select_related("ngo")
        )

        matches = []

        print(
            "========== AI DONATION MATCHING =========="
        )
        print("Donation item:", donation.item_name)
        print("Donation category:", donation.category)

        # -------------------------------------------------
        # CHECK NGO REQUIREMENTS
        # -------------------------------------------------

        for requirement in requirements:

            print(
                "Checking requirement:",
                requirement.id,
                requirement.item_name,
                requirement.category,
            )

            # Generic item-name matching
            if not item_names_match(
                donation.item_name,
                requirement.item_name
            ):
                continue

            if not categories_match(
                donation.category,
                requirement.category,
                donation.item_name
            ):
                continue

            remaining_need = (
                requirement.required_quantity
                - requirement.fulfilled_quantity
            )

            if remaining_need <= 0:
                continue

            recommended_quantity = min(
                donation.quantity,
                remaining_need
            )

            priority = str(
                requirement.priority
            ).strip().lower()

            priority_score = AI_PRIORITY_SCORES.get(
                priority,
                0
            )

            # -------------------------------------------------
            # QUANTITY COMPATIBILITY
            # -------------------------------------------------

            if donation.quantity == remaining_need:
                quantity_score = 30
            elif donation.quantity < remaining_need:
                quantity_score = 20
            else:
                quantity_score = 15

            # Priority is intentionally weighted much more
            # strongly than quantity.
            ai_score = (
                priority_score * 100
                + quantity_score
            )

            # -------------------------------------------------
            # AI REASON
            # -------------------------------------------------

            if priority == "high":

                reason = (
                    f"{requirement.ngo.ngo_name} has a "
                    f"HIGH priority requirement for "
                    f"{requirement.item_name}. "
                    f"The NGO currently needs "
                    f"{remaining_need} units."
                )

            elif priority == "medium":

                reason = (
                    f"{requirement.ngo.ngo_name} has a "
                    f"MEDIUM priority requirement for "
                    f"{requirement.item_name}. "
                    f"The NGO currently needs "
                    f"{remaining_need} units."
                )

            elif priority == "low":

                reason = (
                    f"{requirement.ngo.ngo_name} has a "
                    f"LOW priority requirement for "
                    f"{requirement.item_name}. "
                    f"The NGO currently needs "
                    f"{remaining_need} units."
                )

            elif priority == "urgent":

                reason = (
                    f"{requirement.ngo.ngo_name} has an "
                    f"URGENT requirement for "
                    f"{requirement.item_name}. "
                    f"The NGO currently needs "
                    f"{remaining_need} units."
                )

            elif donation.quantity == remaining_need:

                reason = (
                    f"Your donation exactly matches the "
                    f"remaining requirement of "
                    f"{requirement.ngo.ngo_name}."
                )

            else:

                reason = (
                    f"{requirement.ngo.ngo_name} needs "
                    f"{remaining_need} units of "
                    f"{requirement.item_name}."
                )

            matches.append(
                {
                    "requirement_id":
                        requirement.id,

                    "ngo_id":
                        requirement.ngo.id,

                    "ngo_name":
                        requirement.ngo.ngo_name,

                    "city":
                        requirement.ngo.city,

                    "state":
                        requirement.ngo.state,

                    "item_name":
                        requirement.item_name,

                    "category":
                        requirement.category,

                    "required_quantity":
                        requirement.required_quantity,

                    "fulfilled_quantity":
                        requirement.fulfilled_quantity,

                    "remaining_need":
                        remaining_need,

                    "donation_quantity":
                        donation.quantity,

                    "recommended_quantity":
                        recommended_quantity,

                    "priority":
                        requirement.priority,

                    "priority_score":
                        priority_score,

                    "ai_score":
                        ai_score,

                    "ai_reason":
                        reason,
                }
            )

        # -------------------------------------------------
        # NO MATCH FOUND
        # -------------------------------------------------

        if not matches:

            return Response(
                {
                    "success": True,

                    "donation_id":
                        donation.id,

                    "item_name":
                        donation.item_name,

                    "category":
                        donation.category,

                    "donation_quantity":
                        donation.quantity,

                    "ai_recommendation":
                        None,

                    "other_matching_ngos":
                        [],

                    "message":
                        "No approved NGO currently needs this item."
                },
                status=status.HTTP_200_OK
            )

        # -------------------------------------------------
        # SORT
        # -------------------------------------------------
        # IMPORTANT:
        # Priority is the FIRST sorting factor.
        #
        # High   -> first
        # Medium -> second
        # Low    -> third
        # Urgent -> fourth (as requested)
        #
        # Quantity compatibility is only used after priority.
        # -------------------------------------------------

        matches.sort(
            key=lambda x: (
                x["priority_score"],
                x["ai_score"],
                x["remaining_need"]
            ),
            reverse=True
        )

        best_match = matches[0]
        matched_requirement = NGORequirement.objects.select_related("ngo").get(
            id=best_match["requirement_id"]
        )
        notify_ai_match(donation, matched_requirement)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return Response(
            {
                "success": True,

                "donation_id":
                    donation.id,

                "item_name":
                    donation.item_name,

                "category":
                    donation.category,

                "donation_quantity":
                    donation.quantity,

                "ai_recommendation":
                    best_match,

                "other_matching_ngos":
                    matches[1:],

                "message":
                    (
                        f"AI recommends "
                        f"{best_match['ngo_name']} "
                        f"because it has the highest "
                        f"priority among matching requirements."
                    )
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# DONATION ALLOCATION API
# =========================================================

class DonationAllocationView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "Donor":
            return Response(
                {
                    "message":
                        "Only donors can allocate donations."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            donation = Donation.objects.get(
                id=pk,
                donor_id=user_id
            )
        except Donation.DoesNotExist:
            return Response(
                {
                    "message":
                        "Donation not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if donation.status != "Pending":

            return Response(
                {
                    "message":
                        f"Cannot allocate a donation that is already "
                        f"'{donation.status}'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        allocations = request.data.get(
            "allocations"
        )

        if not isinstance(
            allocations,
            list
        ) or not allocations:

            return Response(
                {
                    "message":
                        "allocations must be a non-empty list."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            requested_total = sum(
                int(item.get("quantity", 0))
                for item in allocations
            )
        except (TypeError, ValueError):

            return Response(
                {
                    "message":
                        "Quantity must be a valid number."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if requested_total <= 0:
            return Response(
                {
                    "message":
                        "Allocation quantity must be greater than 0."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if requested_total > donation.quantity:
            return Response(
                {
                    "message":
                        "Allocated quantity cannot exceed donated quantity."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        created_allocations = []

        # -------------------------------------------------
        # Validate and create each allocation.
        # -------------------------------------------------

        for item in allocations:

            requirement_id = item.get(
                "requirement_id"
            )

            try:
                quantity = int(
                    item.get(
                        "quantity",
                        0
                    )
                )
            except (TypeError, ValueError):

                return Response(
                    {
                        "message":
                            "Invalid allocation quantity."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if quantity <= 0:
                return Response(
                    {
                        "message":
                            "Allocation quantity must be greater than 0."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                requirement = (
                    NGORequirement.objects
                    .select_related("ngo")
                    .get(
                        id=requirement_id,
                        is_active=True,
                        ngo__status="Approved"
                    )
                )
            except NGORequirement.DoesNotExist:

                return Response(
                    {
                        "message":
                            "NGO requirement not found."
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            # -------------------------------------------------
            # NORMALIZED ITEM + CATEGORY MATCHING
            # -------------------------------------------------

            if (
                not item_names_match(
                    donation.item_name,
                    requirement.item_name
                )
                or
                not categories_match(
                    requirement.category,
                    donation.category,
                    donation.item_name
                )
            ):

                return Response(
                    {
                        "message":
                            f"{requirement.ngo.ngo_name} "
                            "does not require this item."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            remaining_need = (
                requirement.required_quantity
                - requirement.fulfilled_quantity
            )

            if remaining_need <= 0:
                return Response(
                    {
                        "message":
                            f"{requirement.ngo.ngo_name} "
                            "requirement is already fulfilled."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if quantity > remaining_need:
                return Response(
                    {
                        "message":
                            f"{requirement.ngo.ngo_name} needs only "
                            f"{remaining_need}."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            allocation = DonationAllocation.objects.create(
                donation=donation,
                ngo=requirement.ngo,
                requirement=requirement,
                allocated_quantity=quantity,
                status="Pending"
            )

            # IMPORTANT:
            # Do NOT update fulfilled_quantity here.
            # The requirement is fulfilled only after the NGO
            # explicitly accepts the donation.

            created_allocations.append(
                allocation
            )

        # -------------------------------------------------
        # Keep old Donation.ngo field compatible.
        #
        # The donation remains Pending until the NGO accepts.
        # This NGO link lets the NGO see the pending request.
        # -------------------------------------------------

        if len(created_allocations) == 1:

            donation.ngo = (
                created_allocations[0].ngo
            )

            donation.save(
                update_fields=["ngo"]
            )

        for allocation in created_allocations:
            notify_allocation_created(allocation)

        serializer = DonationAllocationSerializer(
            created_allocations,
            many=True
        )

        return Response(
            {
                "message":
                    "Donation allocated successfully.",

                "donation_id":
                    donation.id,

                "donated_quantity":
                    donation.quantity,

                "allocated_quantity":
                    requested_total,

                "remaining_quantity":
                    donation.quantity - requested_total,

                "allocations":
                    serializer.data
            },
            status=status.HTTP_201_CREATED
        )


# =========================================================
# NGO ALLOCATED DONATIONS API
# =========================================================

class NGODonationAllocationListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {
                    "message":
                        "Only NGOs can view allocated donations."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            NGO.objects.get(
                id=user_id
            )
        except NGO.DoesNotExist:
            return Response(
                {
                    "message":
                        "NGO not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        allocations = (
            DonationAllocation.objects
            .filter(
                ngo_id=user_id
            )
            .select_related(
                "donation",
                "donation__donor",
                "ngo",
                "requirement"
            )
            .order_by(
                "-allocated_at"
            )
        )

        serializer = DonationAllocationSerializer(
            allocations,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =========================================================
# SCHEDULE PICKUP — DONOR CREATES PICKUP REQUEST
# =========================================================
#
# POST /api/pickup/
#
# Body:
#   allocation_id   int       required
#   pickup_address  string    required
#   scheduled_time  datetime  required  (ISO 8601)
#   notes           string    optional
#
# Only the donor who owns the allocation can create.
# The donor can schedule the pickup before NGO acceptance.
# The pickup remains Pending until the NGO accepts.
# One allocation can only have one pickup request.
# =========================================================

class PickupCreateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        # -------------------------------------------------
        # ONLY DONORS
        # -------------------------------------------------

        if user_type != "Donor":
            return Response(
                {
                    "message":
                        "Only donors can schedule a pickup."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # VALIDATE FIELDS
        # -------------------------------------------------

        allocation_id  = request.data.get("allocation_id")
        pickup_address = request.data.get("pickup_address", "").strip()
        scheduled_time = request.data.get("scheduled_time")
        notes          = request.data.get("notes", "").strip()

        if not allocation_id:
            return Response(
                {"message": "allocation_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not pickup_address:
            return Response(
                {"message": "pickup_address is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not scheduled_time:
            return Response(
                {"message": "scheduled_time is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------
        # FIND ALLOCATION — must belong to this donor
        # -------------------------------------------------

        try:
            allocation = (
                DonationAllocation.objects
                .select_related(
                    "donation",
                    "donation__donor",
                    "ngo"
                )
                .get(
                    id=allocation_id,
                    donation__donor_id=user_id
                )
            )
        except DonationAllocation.DoesNotExist:
            return Response(
                {"message": "Allocation not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # -------------------------------------------------
        # PICKUP CAN BE SCHEDULED BEFORE NGO ACCEPTS
        # -------------------------------------------------
        #
        # The donor selects the pickup date/time while creating
        # the donation. The pickup request stays Pending until
        # the selected NGO accepts the donation.
        #
        # Valid flow:
        #
        # Donation Pending
        # Allocation Pending
        # Pickup Pending
        #       ↓
        # NGO accepts
        #       ↓
        # Donation Accepted
        # Allocation Accepted
        # Pickup Pending
        #
        # We intentionally do NOT require the allocation or
        # donation to be Accepted at this stage.
        # -------------------------------------------------

        if allocation.status not in ["Pending", "Accepted"]:
            return Response(
                {
                    "message":
                        f"Pickup cannot be scheduled for an allocation with status "
                        f"'{allocation.status}'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if allocation.donation.status not in ["Pending", "Accepted"]:
            return Response(
                {
                    "message":
                        f"Pickup cannot be scheduled for a donation with status "
                        f"'{allocation.donation.status}'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------
        # NO DUPLICATE PICKUP FOR SAME ALLOCATION
        # -------------------------------------------------

        if hasattr(allocation, "pickup_request"):
            return Response(
                {"message": "A pickup request already exists for this allocation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------
        # PARSE DATETIME
        # -------------------------------------------------

        from django.utils.dateparse import parse_datetime
        from django.utils import timezone as tz

        parsed_time = parse_datetime(str(scheduled_time))

        if parsed_time is None:
            return Response(
                {"message": "Invalid scheduled_time format. Use ISO 8601 (e.g. 2026-09-01T10:00:00)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Make timezone-aware if naive
        if tz.is_naive(parsed_time):
            parsed_time = tz.make_aware(parsed_time)

        # Must be in the future
        if parsed_time <= tz.now():
            return Response(
                {"message": "Scheduled pickup time must be in the future."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # -------------------------------------------------
        # CREATE PICKUP REQUEST
        # -------------------------------------------------

        pickup = PickupRequest.objects.create(
            allocation=allocation,
            pickup_address=pickup_address,
            scheduled_time=parsed_time,
            notes=notes,
            status="Pending"
        )
        notify_pickup_created(pickup)

        serializer = PickupRequestSerializer(pickup)

        return Response(
            {
                "message": "Pickup scheduled successfully.",
                "pickup": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


# =========================================================
# DONOR — MY PICKUP REQUESTS
# =========================================================
#
# GET /api/pickup/my/
#
# Returns all pickup requests created by the logged-in donor,
# ordered newest first.
# =========================================================

class DonorPickupListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "Donor":
            return Response(
                {"message": "Only donors can view their pickup requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        pickups = (
            PickupRequest.objects
            .filter(
                allocation__donation__donor_id=user_id
            )
            .select_related(
                "allocation",
                "allocation__donation",
                "allocation__donation__donor",
                "allocation__ngo"
            )
            .order_by("-created_at")
        )

        serializer = PickupRequestSerializer(
            pickups,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =========================================================
# NGO — VIEW INCOMING PICKUP REQUESTS
# =========================================================
#
# GET  /api/pickup/ngo/         → list all pickup requests for this NGO
# POST /api/pickup/ngo/{id}/status/  → update status
#
# Status transitions allowed by NGO:
#   Pending    → Confirmed  (NGO accepts)
#   Pending    → Cancelled  (NGO rejects)
#   Confirmed  → Dispatched (NGO dispatches)
#   Dispatched → Delivered  (NGO marks delivered)
#   Any        → Cancelled  (NGO cancels)
# =========================================================

class NGOPickupListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {"message": "Only NGOs can view pickup requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        pickups = (
            PickupRequest.objects
            .filter(
                allocation__ngo_id=user_id,
                allocation__status="Accepted",
                allocation__donation__status="Accepted",
            )
            .select_related(
                "allocation",
                "allocation__donation",
                "allocation__donation__donor",
                "allocation__ngo"
            )
            .order_by("-created_at")
        )

        serializer = PickupRequestSerializer(
            pickups,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# =========================================================
# NGO — UPDATE PICKUP STATUS
# =========================================================
#
# PATCH /api/pickup/{id}/status/
#
# Body:  { "status": "Confirmed" | "Dispatched" | "Delivered" | "Cancelled" }
# =========================================================

class PickupStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    # Valid NGO-initiated transitions
    VALID_TRANSITIONS = {
        "Pending":    ["Confirmed", "Cancelled"],
        "Confirmed":  ["Dispatched", "Cancelled"],
        "Dispatched": ["Delivered",  "Cancelled"],
        "Delivered":  [],
        "Cancelled":  [],
    }

    def patch(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "NGO":
            return Response(
                {"message": "Only NGOs can update pickup status."},
                status=status.HTTP_403_FORBIDDEN
            )

        # -------------------------------------------------
        # FIND PICKUP — must belong to this NGO
        # -------------------------------------------------

        try:
            pickup = (
                PickupRequest.objects
                .select_related(
                    "allocation",
                    "allocation__donation",
                    "allocation__donation__donor",
                    "allocation__ngo"
                )
                .get(
                    id=pk,
                    allocation__ngo_id=user_id
                )
            )
        except PickupRequest.DoesNotExist:
            return Response(
                {"message": "Pickup request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get("status", "").strip()

        allowed = self.VALID_TRANSITIONS.get(
            pickup.status,
            []
        )

        if new_status not in allowed:
            return Response(
                {
                    "message":
                        f"Cannot transition from '{pickup.status}' to '{new_status}'. "
                        f"Allowed: {allowed or 'none (terminal state)'}."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        pickup.status = new_status
        pickup.save(update_fields=["status", "updated_at"])
        notify_pickup_status_changed(pickup, changed_by="NGO")

        # -------------------------------------------------
        # IMPORTANT:
        # Pickup status is independent from donation/allocation
        # acceptance status.
        #
        # Donation/Allocation become Accepted when the NGO accepts
        # the donation. A pickup can then move independently through:
        #
        # Pending -> Confirmed -> Dispatched -> Delivered
        #
        # If a pickup is cancelled, the donation/allocation must NOT
        # be changed to Rejected. The donation was already accepted.
        # -------------------------------------------------

        serializer = PickupRequestSerializer(pickup)

        return Response(
            {
                "message": f"Pickup status updated to '{new_status}'.",
                "pickup": serializer.data
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# DONOR — CANCEL PICKUP REQUEST
# =========================================================
#
# DELETE /api/pickup/{id}/cancel/
#
# Donor can cancel a Pending pickup.
# =========================================================

class DonorPickupCancelView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def patch(self, request, pk):

        user_id = request.auth.get("user_id")
        user_type = request.auth.get("user_type")

        if user_type != "Donor":
            return Response(
                {"message": "Only donors can cancel pickup requests."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            pickup = (
                PickupRequest.objects
                .select_related("allocation")
                .get(
                    id=pk,
                    allocation__donation__donor_id=user_id
                )
            )
        except PickupRequest.DoesNotExist:
            return Response(
                {"message": "Pickup request not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if pickup.status not in ["Pending"]:
            return Response(
                {
                    "message":
                        f"Cannot cancel a pickup that is already '{pickup.status}'."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cancel only the pickup request.
        # The donation/allocation remains Accepted because the NGO has
        # already accepted the donation.
        pickup.status = "Cancelled"
        pickup.save(update_fields=["status", "updated_at"])
        notify_pickup_status_changed(pickup, changed_by="Donor")

        return Response(
            {"message": "Pickup request cancelled."},
            status=status.HTTP_200_OK
        )
# =========================================================
# ADMIN DASHBOARD STATISTICS API
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_dashboard_stats(request):

    # =====================================================
    # BASIC COUNTS
    # =====================================================

    total_donors = Donor.objects.count()

    total_ngos = NGO.objects.count()

    total_donations = Donation.objects.count()

    total_requirements = NGORequirement.objects.count()

    total_allocations = DonationAllocation.objects.count()

    total_pickups = PickupRequest.objects.count()


    # =====================================================
    # PENDING COUNTS
    # =====================================================

    pending_ngos = NGO.objects.filter(
        status="Pending"
    ).count()

    pending_donations = Donation.objects.filter(
        status="Pending"
    ).count()

    pending_requirements = NGORequirement.objects.filter(
        is_active=True,
        fulfilled_quantity__lt=F("required_quantity")
    ).count()

    pending_pickups = PickupRequest.objects.filter(
        status="Pending"
    ).count()


    # =====================================================
    # DONATION STATUS
    # =====================================================

    accepted_donations = Donation.objects.filter(
        status="Accepted"
    ).count()

    collected_donations = Donation.objects.filter(
        status="Collected"
    ).count()

    rejected_donations = Donation.objects.filter(
        status="Rejected"
    ).count()


    # =====================================================
    # PICKUP STATUS
    # =====================================================

    confirmed_pickups = PickupRequest.objects.filter(
        status="Confirmed"
    ).count()

    delivered_pickups = PickupRequest.objects.filter(
        status="Delivered"
    ).count()

    cancelled_pickups = PickupRequest.objects.filter(
        status="Cancelled"
    ).count()


    # =====================================================
    # ALLOCATION STATUS
    # =====================================================

    matched_donations = DonationAllocation.objects.count()

    accepted_allocations = DonationAllocation.objects.filter(
        status="Accepted"
    ).count()

    pending_allocations = DonationAllocation.objects.filter(
        status="Pending"
    ).count()


    # =====================================================
    # RECENT DONATIONS
    # =====================================================

    recent_donations = (
        Donation.objects
        .select_related(
            "donor",
            "ngo"
        )
        .order_by(
            "-donation_date"
        )[:10]
    )


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
                (
                    donation.donor.name
                    if donation.donor
                    else "Unknown"
                ),

            "ngo":
                (
                    donation.ngo.ngo_name
                    if donation.ngo
                    else None
                ),

            "donation_date":
                (
                    donation.donation_date.isoformat()
                ),

        })


    # =====================================================
    # RETURN DATA
    # =====================================================

    return Response(

        {
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

                "confirmed_pickups":
                    confirmed_pickups,

                "delivered_pickups":
                    delivered_pickups,

                "cancelled_pickups":
                    cancelled_pickups,

                "matched_donations":
                    matched_donations,

                "accepted_allocations":
                    accepted_allocations,

                "pending_allocations":
                    pending_allocations,

            },

            "recent_donations":
                recent_data,
        },

        status=status.HTTP_200_OK
    )

# ADMIN NGO MANAGEMENT
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_ngos(request):
    """
    Admin API to view all NGOs.

    Optional query parameter:

        ?status=Pending
        ?status=Approved
        ?status=Rejected

    Example:
        /api/admin/ngos/
        /api/admin/ngos/?status=Pending
    """

    status_filter = request.GET.get("status")

    ngos = NGO.objects.all().order_by("-registered_at")

    # -----------------------------------------------------
    # FILTER BY STATUS
    # -----------------------------------------------------

    if status_filter:
        ngos = ngos.filter(
            status=status_filter
        )

    # -----------------------------------------------------
    # CREATE RESPONSE
    # -----------------------------------------------------

    data = []

    for ngo in ngos:

        data.append({

            "id":
                ngo.id,

            "ngo_name":
                ngo.ngo_name,

            "description":
                ngo.description,

            "registration_no":
                ngo.registration_no,

            "email_id":
                ngo.email_id,

            "phone_no":
                ngo.phone_no,

            "website_link":
                ngo.website_link,

            "address":
                ngo.address,

            "city":
                ngo.city,

            "state":
                ngo.state,

            "pincode":
                ngo.pincode,

            "language":
                ngo.language,

            "status":
                ngo.status,

            "picture":
                (
                    request.build_absolute_uri(
                        ngo.picture.url
                    )
                    if ngo.picture
                    else None
                ),

            "certificate":
                (
                    request.build_absolute_uri(
                        ngo.certificate_files.url
                    )
                    if ngo.certificate_files
                    else None
                ),

            "registered_at":
                (
                    ngo.registered_at.isoformat()
                ),

        })

    return Response(
        {
            "success": True,

            "count":
                len(data),

            "ngos":
                data,
        },

        status=status.HTTP_200_OK
    )


# =========================================================
# ADMIN NGO DETAIL
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_ngo_detail(request, pk):
    """
    Admin API to view complete details of one NGO.
    """

    try:

        ngo = NGO.objects.get(
            id=pk
        )

    except NGO.DoesNotExist:

        return Response(
            {
                "success": False,

                "message":
                    "NGO not found."
            },

            status=status.HTTP_404_NOT_FOUND
        )

    return Response(

        {
            "success": True,

            "ngo": {

                "id":
                    ngo.id,

                "ngo_name":
                    ngo.ngo_name,

                "description":
                    ngo.description,

                "registration_no":
                    ngo.registration_no,

                "email_id":
                    ngo.email_id,

                "phone_no":
                    ngo.phone_no,

                "website_link":
                    ngo.website_link,

                "address":
                    ngo.address,

                "city":
                    ngo.city,

                "state":
                    ngo.state,

                "pincode":
                    ngo.pincode,

                "language":
                    ngo.language,

                "status":
                    ngo.status,

                "picture":
                    (
                        request.build_absolute_uri(
                            ngo.picture.url
                        )
                        if ngo.picture
                        else None
                    ),

                "certificate":
                    (
                        request.build_absolute_uri(
                            ngo.certificate_files.url
                        )
                        if ngo.certificate_files
                        else None
                    ),

                "registered_at":
                    (
                        ngo.registered_at.isoformat()
                    ),

            }
        },

        status=status.HTTP_200_OK
    )


# =========================================================
# ADMIN APPROVE NGO
# =========================================================

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_approve_ngo(request, pk):
    """
    Approve a pending NGO.
    """

    try:

        ngo = NGO.objects.get(
            id=pk
        )

    except NGO.DoesNotExist:

        return Response(
            {
                "success": False,

                "message":
                    "NGO not found."
            },

            status=status.HTTP_404_NOT_FOUND
        )

    # -----------------------------------------------------
    # ALREADY APPROVED
    # -----------------------------------------------------

    if ngo.status == "Approved":

        return Response(
            {
                "success": False,

                "message":
                    "NGO is already approved."
            },

            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # APPROVE NGO
    # -----------------------------------------------------

    ngo.status = "Approved"

    ngo.save(
        update_fields=["status"]
    )

    return Response(

        {
            "success": True,

            "message":
                "NGO approved successfully.",

            "ngo": {

                "id":
                    ngo.id,

                "ngo_name":
                    ngo.ngo_name,

                "status":
                    ngo.status,

            }
        },

        status=status.HTTP_200_OK
    )


# =========================================================
# ADMIN REJECT NGO
# =========================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_reject_ngo(request, pk):
    """
    Reject an NGO.
    """

    try:

        ngo = NGO.objects.get(
            id=pk
        )

    except NGO.DoesNotExist:

        return Response(
            {
                "success": False,

                "message":
                    "NGO not found."
            },

            status=status.HTTP_404_NOT_FOUND
        )

    # -----------------------------------------------------
    # ALREADY REJECTED
    # -----------------------------------------------------

    if ngo.status == "Rejected":

        return Response(
            {
                "success": False,

                "message":
                    "NGO is already rejected."
            },

            status=status.HTTP_400_BAD_REQUEST
        )

    # -----------------------------------------------------
    # REJECT NGO
    # -----------------------------------------------------

    ngo.status = "Rejected"

    ngo.save(
        update_fields=["status"]
    )

    return Response(

        {
            "success": True,

            "message":
                "NGO rejected successfully.",

            "ngo": {

                "id":
                    ngo.id,

                "ngo_name":
                    ngo.ngo_name,

                "status":
                    ngo.status,

            }
        },

        status=status.HTTP_200_OK
             )

# =========================================================
# ADMIN DONOR MANAGEMENT
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_donors(request):
    """
    Admin API to view all registered donors.

    Optional:
        ?status=active
        ?status=inactive

    Example:
        /api/admin/donors/
    """

    status_filter = request.GET.get("status")

    donors = Donor.objects.all().order_by("-registered_date")

    # -----------------------------------------------------
    # FILTER ACTIVE / INACTIVE
    # -----------------------------------------------------

    if status_filter == "active":
        donors = donors.filter(
            status_active=True
        )

    elif status_filter == "inactive":
        donors = donors.filter(
            status_active=False
        )

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    data = []

    for donor in donors:

        data.append({

            "id":
                donor.id,

            "name":
                donor.name,

            "email":
                donor.email,

            "phone":
                donor.phone,

            "language":
                donor.language_preference,

            "address":
                donor.address,

            "city":
                donor.city,

            "state":
                donor.state,

            "pincode":
                donor.pincode,

            "status_active":
                donor.status_active,

            "registered_date":
                donor.registered_date.isoformat(),

            "picture":
                (
                    request.build_absolute_uri(
                        donor.picture.url
                    )
                    if donor.picture
                    else None
                ),

            # Number of donations made by this donor
            "total_donations":
                donor.donations.count(),
        })

    return Response(
        {
            "success": True,

            "count":
                len(data),

            "donors":
                data,
        },

        status=status.HTTP_200_OK
    )

# =========================================================
# ADMIN COMPLETE DATA API
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_management_data(request):

    data_type = request.GET.get(
        "type",
        "donors"
    ).lower()


    # =====================================================
    # DONORS
    # =====================================================

    if data_type == "donors":

        donors = (
            Donor.objects
            .all()
            .order_by("-registered_date")
        )

        data = []

        for donor in donors:

            data.append({

                "id": donor.id,

                "name": donor.name,

                "email": donor.email,

                "phone": donor.phone,

                "city": donor.city,

                "state": donor.state,

                "pincode": donor.pincode,

                "language":
                    donor.language_preference,

                "status":
                    "Active"
                    if donor.status_active
                    else "Inactive",

                "donations":
                    donor.donations.count(),

                "registered_date":
                    donor.registered_date.isoformat(),

                "picture":
                    (
                        request.build_absolute_uri(
                            donor.picture.url
                        )
                        if donor.picture
                        else None
                    ),
            })

        return Response({

            "success": True,

            "type": "donors",

            "count": len(data),

            "data": data

        })


    # =====================================================
    # NGOS
    # =====================================================

    if data_type == "ngos":

        ngos = (
            NGO.objects
            .all()
            .order_by("-registered_at")
        )

        data = []

        for ngo in ngos:

            data.append({

                "id": ngo.id,

                "name": ngo.ngo_name,

                "registration_no":
                    ngo.registration_no,

                "email":
                    ngo.email_id,

                "phone":
                    ngo.phone_no,

                "city":
                    ngo.city,

                "state":
                    ngo.state,

                "status":
                    ngo.status,

                "language":
                    ngo.language,

                "registered_at":
                    ngo.registered_at.isoformat(),

                "picture":
                    (
                        request.build_absolute_uri(
                            ngo.picture.url
                        )
                        if ngo.picture
                        else None
                    ),

            })

        return Response({

            "success": True,

            "type": "ngos",

            "count": len(data),

            "data": data

        })


    # =====================================================
    # DONATIONS
    # =====================================================

    if data_type == "donations":

        donations = (
            Donation.objects
            .select_related(
                "donor",
                "ngo"
            )
            .all()
            .order_by("-donation_date")
        )

        data = []

        for donation in donations:

            data.append({

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
                    (
                        donation.donor.name
                        if donation.donor
                        else "Unknown"
                    ),

                "donor_email":
                    (
                        donation.donor.email
                        if donation.donor
                        else ""
                    ),

                "ngo":
                    (
                        donation.ngo.ngo_name
                        if donation.ngo
                        else "Not allocated"
                    ),

                "location":
                    donation.location,

                "donation_date":
                    donation.donation_date.isoformat(),

            })

        return Response({

            "success": True,

            "type": "donations",

            "count": len(data),

            "data": data

        })


    # =====================================================
    # REQUIREMENTS
    # =====================================================

    if data_type == "requirements":

        requirements = (
            NGORequirement.objects
            .select_related("ngo")
            .all()
            .order_by("-created_at")
        )

        data = []

        for requirement in requirements:

            remaining = max(
                requirement.required_quantity
                - requirement.fulfilled_quantity,
                0
            )

            data.append({

                "id":
                    requirement.id,

                "ngo":
                    requirement.ngo.ngo_name,

                "item_name":
                    requirement.item_name,

                "category":
                    requirement.category,

                "required_quantity":
                    requirement.required_quantity,

                "fulfilled_quantity":
                    requirement.fulfilled_quantity,

                "remaining_quantity":
                    remaining,

                "priority":
                    requirement.priority,

                "description":
                    requirement.description,

                "is_active":
                    requirement.is_active,

                "created_at":
                    requirement.created_at.isoformat(),

            })

        return Response({

            "success": True,

            "type": "requirements",

            "count": len(data),

            "data": data

        })


    # =====================================================
    # ALLOCATIONS
    # =====================================================

    if data_type == "allocations":

        allocations = (
            DonationAllocation.objects
            .select_related(
                "donation",
                "donation__donor",
                "ngo",
                "requirement"
            )
            .all()
            .order_by("-allocated_at")
        )

        data = []

        for allocation in allocations:

            data.append({

                "id":
                    allocation.id,

                "donation":
                    allocation.donation.item_name,

                "donor":
                    allocation.donation.donor.name,

                "ngo":
                    allocation.ngo.ngo_name,

                "requirement":
                    (
                        allocation.requirement.item_name
                        if allocation.requirement
                        else "N/A"
                    ),

                "quantity":
                    allocation.allocated_quantity,

                "status":
                    allocation.status,

                "allocated_at":
                    allocation.allocated_at.isoformat(),

            })

        return Response({

            "success": True,

            "type": "allocations",

            "count": len(data),

            "data": data

        })


    # =====================================================
    # PICKUPS
    # =====================================================

    if data_type == "pickups":

        pickups = (
            PickupRequest.objects
            .select_related(
                "allocation",
                "allocation__donation",
                "allocation__donation__donor",
                "allocation__ngo"
            )
            .all()
            .order_by("-created_at")
        )

        data = []

        for pickup in pickups:

            allocation = pickup.allocation

            data.append({

                "id":
                    pickup.id,

                "item":
                    allocation.donation.item_name,

                "donor":
                    allocation.donation.donor.name,

                "ngo":
                    allocation.ngo.ngo_name,

                "address":
                    pickup.pickup_address,

                "scheduled_time":
                    pickup.scheduled_time.isoformat(),

                "status":
                    pickup.status,

                "notes":
                    pickup.notes,

                "created_at":
                    pickup.created_at.isoformat(),

            })

        return Response({

            "success": True,

            "type": "pickups",

            "count": len(data),

            "data": data

        })


    # =====================================================
    # INVALID TYPE
    # =====================================================

    return Response(

        {
            "success": False,

            "message":
                "Invalid admin data type."

        },

        status=status.HTTP_400_BAD_REQUEST
    )


# =========================================================
# ADMIN MANAGEMENT DATA
# =========================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_management_data(request):

    data_type = request.GET.get(
        "type",
        "donors"
    ).lower()


    # =====================================================
    # DONORS
    # =====================================================

    if data_type == "donors":

        donors = Donor.objects.all().order_by(
            "-registered_date"
        )

        data = []

        for donor in donors:

            data.append({

                "id": donor.id,

                "name": donor.name,

                "email": donor.email,

                "phone": donor.phone,

                "city": donor.city,

                "state": donor.state,

                "pincode": donor.pincode,

                "status":
                    "Active"
                    if donor.status_active
                    else "Inactive",

                "donations":
                    donor.donations.count(),

                "registered_date":
                    donor.registered_date.isoformat(),

            })

        return Response({
            "success": True,
            "type": "donors",
            "count": len(data),
            "data": data
        })


    # =====================================================
    # DONATIONS
    # =====================================================

    if data_type == "donations":

        donations = Donation.objects.select_related(
            "donor",
            "ngo"
        ).all().order_by(
            "-donation_date"
        )

        data = []

        for donation in donations:

            data.append({

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
                    (
                        donation.donor.name
                        if donation.donor
                        else "Unknown"
                    ),

                "ngo":
                    (
                        donation.ngo.ngo_name
                        if donation.ngo
                        else "Not allocated"
                    ),

                "location":
                    donation.location,

                "donation_date":
                    donation.donation_date.isoformat(),

            })

        return Response({
            "success": True,
            "type": "donations",
            "count": len(data),
            "data": data
        })


    # =====================================================
    # REQUIREMENTS
    # =====================================================

    if data_type == "requirements":

        requirements = NGORequirement.objects.select_related(
            "ngo"
        ).all().order_by(
            "-created_at"
        )

        data = []

        for requirement in requirements:

            remaining = max(
                requirement.required_quantity
                - requirement.fulfilled_quantity,
                0
            )

            data.append({

                "id":
                    requirement.id,

                "ngo":
                    requirement.ngo.ngo_name,

                "item_name":
                    requirement.item_name,

                "category":
                    requirement.category,

                "required_quantity":
                    requirement.required_quantity,

                "fulfilled_quantity":
                    requirement.fulfilled_quantity,

                "remaining_quantity":
                    remaining,

                "priority":
                    requirement.priority,

                "is_active":
                    requirement.is_active,

                "created_at":
                    requirement.created_at.isoformat(),

            })

        return Response({
            "success": True,
            "type": "requirements",
            "count": len(data),
            "data": data
        })


    # =====================================================
    # ALLOCATIONS
    # =====================================================

    if data_type == "allocations":

        allocations = DonationAllocation.objects.select_related(
            "donation",
            "donation__donor",
            "ngo",
            "requirement"
        ).all().order_by(
            "-allocated_at"
        )

        data = []

        for allocation in allocations:

            data.append({

                "id":
                    allocation.id,

                "donation":
                    allocation.donation.item_name,

                "donor":
                    allocation.donation.donor.name,

                "ngo":
                    allocation.ngo.ngo_name,

                "requirement":
                    (
                        allocation.requirement.item_name
                        if allocation.requirement
                        else "N/A"
                    ),

                "quantity":
                    allocation.allocated_quantity,

                "status":
                    allocation.status,

                "allocated_at":
                    allocation.allocated_at.isoformat(),

            })

        return Response({
            "success": True,
            "type": "allocations",
            "count": len(data),
            "data": data
        })


    # =====================================================
    # PICKUPS
    # =====================================================

    if data_type == "pickups":

        pickups = PickupRequest.objects.select_related(
            "allocation",
            "allocation__donation",
            "allocation__donation__donor",
            "allocation__ngo"
        ).all().order_by(
            "-created_at"
        )

        data = []

        for pickup in pickups:

            allocation = pickup.allocation

            data.append({

                "id":
                    pickup.id,

                "item":
                    allocation.donation.item_name,

                "donor":
                    allocation.donation.donor.name,

                "ngo":
                    allocation.ngo.ngo_name,

                "address":
                    pickup.pickup_address,

                "scheduled_time":
                    pickup.scheduled_time.isoformat(),

                "status":
                    pickup.status,

                "notes":
                    pickup.notes,

                "created_at":
                    pickup.created_at.isoformat(),

            })

        return Response({
            "success": True,
            "type": "pickups",
            "count": len(data),
            "data": data
        })


    return Response(
        {
            "success": False,
            "message": "Invalid admin data type."
        },
        status=status.HTTP_400_BAD_REQUEST
    )

