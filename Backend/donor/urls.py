from django.urls import path

from .views import (
    # =====================================================
    # REGISTRATION
    # =====================================================
    RegistrationView,
    DonorDetailView,

    # =====================================================
    # DONATION
    # =====================================================
    DonationCreateView,
    DonationDetailView,
    DonationStatusUpdateView,
    DonationImageAnalysisView,

    # =====================================================
    # NGO
    # =====================================================
    NGOCreateView,
    NGODetailView,
    ApprovedNGOListView,
    NGODonationListView,

    # =====================================================
    # NGO REQUIREMENTS
    # =====================================================
    NGORequirementListCreateView,
    NGORequirementDetailView,

    # =====================================================
    # DONATION MATCHING / ALLOCATION
    # =====================================================
    MatchingNGOView,
    AIMatchView,
    DonationAllocationView,
    NGODonationAllocationListView,

    # =====================================================
    # DONOR
    # =====================================================
    DonorDonationListView,
    DonorRankingView,

    # =====================================================
    # LOGIN
    # =====================================================
    LoginView,

    # =====================================================
    # DASHBOARD
    # =====================================================
    dashboard,

    # =====================================================
    # PROFILE
    # =====================================================
    profile,
    upload_profile_image,
    upload_ngo_certificate,

    # =====================================================
    # PICKUP
    # =====================================================
    PickupCreateView,
    DonorPickupListView,
    NGOPickupListView,
    PickupStatusUpdateView,
    DonorPickupCancelView,

    #admin
        admin_dashboard_stats,
        admin_ngos,
        admin_ngo_detail,
        admin_approve_ngo,
        admin_reject_ngo,
        admin_donors,
        admin_management_data,
    )



urlpatterns = [

    # =====================================================
    # REGISTRATION
    # =====================================================

    path(
        "register/",
        RegistrationView.as_view(),
        name="register"
    ),

    path(
        "register/<int:pk>/",
        DonorDetailView.as_view(),
        name="donor-detail"
    ),


    # =====================================================
    # DONATION
    # =====================================================

    path(
        "donation/",
        DonationCreateView.as_view(),
        name="donation-create"
    ),

    path(
        "donation/<int:pk>/",
        DonationDetailView.as_view(),
        name="donation-detail"
    ),

    path(
        "donation/<int:pk>/status/",
        DonationStatusUpdateView.as_view(),
        name="donation-status"
    ),


    # =====================================================
    # AI IMAGE ANALYSIS
    # =====================================================

    path(
        "donation/analyze/",
        DonationImageAnalysisView.as_view(),
        name="donation-image-analysis"
    ),


    # =====================================================
    # NGO
    # =====================================================

    path(
        "ngo/<int:pk>/",
        NGODetailView.as_view(),
        name="ngo-detail"
    ),

    path(
        "ngos/all/",
        NGOCreateView.as_view(),
        name="ngo-list"
    ),

    path(
        "ngos/",
        ApprovedNGOListView.as_view(),
        name="approved-ngos"
    ),


    # =====================================================
    # NGO DONATION REQUESTS
    # =====================================================

    path(
        "ngo/donations/",
        NGODonationListView.as_view(),
        name="ngo-donations"
    ),


    # =====================================================
    # NGO REQUIREMENTS
    # =====================================================

    path(
        "ngo/requirements/",
        NGORequirementListCreateView.as_view(),
        name="ngo-requirements"
    ),

    path(
        "ngo/requirements/<int:pk>/",
        NGORequirementDetailView.as_view(),
        name="ngo-requirement-detail"
    ),


    # =====================================================
    # DONATION MATCHING
    # =====================================================

    # -----------------------------------------------------
    # DONOR MATCHING
    # -----------------------------------------------------
    #
    # Finds NGOs that actually need the donated item.
    #
    # Example:
    #
    # Donation:
    # Books = 5
    #
    # NGO A:
    # Books = 10
    #
    # NGO B:
    # Rice = 20
    #
    # Result:
    # NGO A only
    #
    # NGO A can receive:
    # min(5, 10) = 5

    path(
        "donation/<int:pk>/matching-ngos/",
        MatchingNGOView.as_view(),
        name="matching-ngos"
    ),


    # -----------------------------------------------------
    # AI MATCHING
    # -----------------------------------------------------
    #
    # AI recommends the best NGO based on:
    #
    # 1. Item match
    # 2. Category
    # 3. Remaining requirement
    # 4. Priority / urgency
    # 5. Quantity compatibility
    #
    # Example:
    #
    # Donor:
    # Books = 5
    #
    # NGO A:
    # Books = 10
    # Priority = Normal
    #
    # NGO B:
    # Books = 5
    # Priority = Urgent
    #
    # AI recommends:
    # NGO B
    #
    # Recommended quantity:
    # min(5, 5) = 5

    path(
        "donation/<int:pk>/ai-matching/",
        AIMatchView.as_view(),
        name="ai-matching"
    ),


    # =====================================================
    # DONATION ALLOCATION
    # =====================================================

    # Allocate donation quantity to NGO requirements.

    path(
        "donation/<int:pk>/allocate/",
        DonationAllocationView.as_view(),
        name="donation-allocation"
    ),


    # =====================================================
    # NGO ALLOCATED DONATIONS
    # =====================================================

    path(
        "ngo/allocations/",
        NGODonationAllocationListView.as_view(),
        name="ngo-allocations"
    ),


    # =====================================================
    # LOGIN
    # =====================================================

    path(
        "login/",
        LoginView.as_view(),
        name="login"
    ),


    # =====================================================
    # DASHBOARD
    # =====================================================

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),


    # =====================================================
    # PROFILE
    # =====================================================

    path(
        "profile/",
        profile,
        name="profile"
    ),


    # =====================================================
    # PROFILE IMAGE
    # =====================================================

    path(
        "profile/upload/",
        upload_profile_image,
        name="profile-upload"
    ),


    # =====================================================
    # NGO CERTIFICATE
    # =====================================================

    path(
        "ngo/certificate/upload/",
        upload_ngo_certificate,
        name="upload-ngo-certificate"
    ),


    # =====================================================
    # DONOR MY DONATIONS
    # =====================================================

    path(
        "my-donations/",
        DonorDonationListView.as_view(),
        name="my-donations"
    ),

    path(
        "donors/ranking/",
        DonorRankingView.as_view(),
        name="donor-ranking"
    ),

    # =====================================================
    # PICKUP REQUESTS
    # =====================================================

    # Donor creates a pickup request after allocation
    path(
        "pickup/",
        PickupCreateView.as_view(),
        name="pickup-create"
    ),

    # Donor views all their pickup requests
    path(
        "pickup/my/",
        DonorPickupListView.as_view(),
        name="pickup-my"
    ),

    # Donor cancels a pickup request
    path(
        "pickup/<int:pk>/cancel/",
        DonorPickupCancelView.as_view(),
        name="pickup-cancel"
    ),

    # NGO views all pickup requests for their allocations
    path(
        "pickup/ngo/",
        NGOPickupListView.as_view(),
        name="pickup-ngo-list"
    ),

    # NGO updates pickup status (Confirmed/Dispatched/Delivered/Cancelled)
    path(
        "pickup/<int:pk>/status/",
        PickupStatusUpdateView.as_view(),
        name="pickup-status-update"
    ),


        # =====================================================
    # ADMIN DASHBOARD
    # =====================================================

    path(
        "admin/dashboard-stats/",
        admin_dashboard_stats,
        name="admin-dashboard-stats"
    ),
    
    
    # =====================================================
# ADMIN
# =====================================================

path(
    "admin/dashboard-stats/",
    admin_dashboard_stats,
    name="admin-dashboard-stats"
),

path(
    "admin/ngos/",
    admin_ngos,
    name="admin-ngos"
),

path(
    "admin/ngos/<int:pk>/",
    admin_ngo_detail,
    name="admin-ngo-detail"
),

path(
    "admin/ngos/<int:pk>/approve/",
    admin_approve_ngo,
    name="admin-ngo-approve"
),

path(
    "admin/ngos/<int:pk>/reject/",
    admin_reject_ngo,
    name="admin-ngo-reject"
),

# =====================================================
# ADMIN DONORS
# =====================================================

path(
    "admin/donors/",
    admin_donors,
    name="admin-donors"
),

path(
    "admin/management-data/",
    admin_management_data,
    name="admin-management-data"
),
]
