"""
Views package initialization.
"""

from src.views.home import render_home_view
from src.views.auth_views import (
    render_login_view,
    render_donor_register_view,
    render_ngo_register_view,
)
from src.views.donor_views import render_donor_workspace
from src.views.ngo_views import render_ngo_workspace
from src.views.admin_views import render_admin_workspace

__all__ = [
    "render_home_view",
    "render_login_view",
    "render_donor_register_view",
    "render_ngo_register_view",
    "render_donor_workspace",
    "render_ngo_workspace",
    "render_admin_workspace",
]
