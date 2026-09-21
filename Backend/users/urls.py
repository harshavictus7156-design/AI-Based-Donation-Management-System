from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    register_page,
    login_page,
    donor_dashboard,
    AIScanView,
    ngo_dashboard,
    admin_dashboard_stats,
)


urlpatterns = [

    # ========================================================
    # FRONTEND PAGES
    # ========================================================

    path(
        "",
        register_page,
        name="register-page"
    ),

    path(
        "login-page/",
        login_page,
        name="login-page"
    ),

    path(
        "donor-dashboard/",
        donor_dashboard,
        name="donor-dashboard"
    ),

    path(
        "ngo-dashboard/",
        ngo_dashboard,
        name="ngo-dashboard"
    ),


    # ========================================================
    # AUTHENTICATION APIs
    # ========================================================

    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login"
    ),


    # ========================================================
    # PROFILE API
    # ========================================================

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),


    # ========================================================
    # GEMINI AI DONATION SCAN API
    # ========================================================

    # Existing endpoint
    path(
        "donations/scan/",
        AIScanView.as_view(),
        name="ai-scan"
    ),

    # Endpoint used by React donation page
    path(
        "donations/analyze-image/",
        AIScanView.as_view(),
        name="analyze-donation-image"
    ),


    # ========================================================
    # ADMIN DASHBOARD API
    # ========================================================

    path(
        "admin/dashboard-stats/",
        admin_dashboard_stats,
        name="admin-dashboard-stats"
    ),

]