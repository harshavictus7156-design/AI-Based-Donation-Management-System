from django.contrib import admin
from django.urls import path, include

from users.views import admin_dashboard_stats


urlpatterns = [

    # ========================================================
    # DJANGO ADMIN
    # ========================================================

    path(
        "admin/",
        admin.site.urls
    ),


    # ========================================================
    # FRONTEND
    # ========================================================

    path(
        "",
        include("users.urls")
    ),


    # ========================================================
    # APIs
    # ========================================================

    path(
        "api/",
        include("users.urls")
    ),


    # ========================================================
    # ADMIN DASHBOARD API
    # ========================================================

    path(
        "api/admin/dashboard-stats/",
        admin_dashboard_stats,
        name="admin-dashboard-stats"
    ),

]