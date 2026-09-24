"""
SmartDonate AI — Intelligent Donation Management System
Main Streamlit Application Entrypoint.
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Configure Streamlit Page
st.set_page_config(
    page_title="SmartDonate AI — Intelligent Donation Management",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Initialize Database & Session State
from src.database import init_database
from src.auth import init_session_state, get_current_user, get_current_role
from src.components.navbar import render_header

init_database()
init_session_state()

# Load Custom CSS
css_file = ROOT_DIR / "assets" / "styles.css"
if css_file.exists():
    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Import View Routers
from src.views.home import render_home_view
from src.views.auth_views import (
    render_login_view,
    render_donor_register_view,
    render_ngo_register_view,
)
from src.views.donor_views import render_donor_workspace, _render_explore_ngos, _render_donor_leaderboard, _render_donate_item
from src.views.ngo_views import render_ngo_workspace
from src.views.admin_views import render_admin_workspace


def main():
    """Main routing controller."""
    # Top Header
    render_header()

    is_auth = st.session_state.get("is_authenticated", False)
    role = get_current_role()
    user = get_current_user()
    current_page = st.session_state.get("current_page", "Home")

    # Routing logic
    if is_auth:
        if role == "Donor":
            render_donor_workspace(user, initial_tab=current_page)
        elif role == "NGO":
            render_ngo_workspace(user)
        elif role == "Admin":
            render_admin_workspace(user)
        else:
            st.warning("Unknown user role. Please sign in again.")
            st.session_state.is_authenticated = False
            st.rerun()
    else:
        # Public Navigation
        if current_page == "Login":
            render_login_view()
        elif current_page in ("Register", "Register Choice"):
            st.markdown(
                """
                <div style="text-align: center; max-width: 600px; margin: 0 auto 30px auto;">
                    <h2 style="color: #f8fafc;">Join the Giving Community</h2>
                    <p style="color: #94a3b8;">Choose how you want to contribute on SmartDonate AI</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    """
                    <div class="glass-card" style="text-align: center; height: 100%;">
                        <div style="font-size: 3rem; margin-bottom: 12px;">🎁</div>
                        <h3 style="color: #f8fafc; margin-bottom: 8px;">Community Donor</h3>
                        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5; margin-bottom: 20px;">
                            Donate items, utilize Gemini AI vision to identify donations, match with urgent NGO requirements, and earn leaderboard points.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Register as Donor →", type="primary", use_container_width=True):
                    st.session_state.current_page = "Register Donor"
                    st.rerun()
            with col2:
                st.markdown(
                    """
                    <div class="glass-card" style="text-align: center; height: 100%;">
                        <div style="font-size: 3rem; margin-bottom: 12px;">🏢</div>
                        <h3 style="color: #f8fafc; margin-bottom: 8px;">NGO Organization</h3>
                        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.5; margin-bottom: 20px;">
                            Publish resource requirements, review incoming donation allocations, coordinate pickups, and track impact.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Register as NGO →", type="primary", use_container_width=True):
                    st.session_state.current_page = "Register NGO"
                    st.rerun()
        elif current_page == "Register Donor":
            render_donor_register_view()
        elif current_page == "Register NGO":
            render_ngo_register_view()
        elif current_page == "Explore NGOs":
            st.markdown("### 🏢 Verified Non-Profit Organizations")
            _render_explore_ngos({})
        elif current_page == "Leaderboard":
            _render_donor_leaderboard({})
        elif current_page == "Donate Items":
            render_login_view()
        else:
            render_home_view()


if __name__ == "__main__":
    main()
