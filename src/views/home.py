"""
Home / Landing page view for the AI-Based Donation Management System.
"""

import streamlit as st
from src.models import Donor, NGO, Donation, NGORequirement
from src.components.cards import render_kpi_card, render_ngo_card
from src.services.ngo_service import get_approved_ngos


def render_home_view():
    """Renders the public landing page."""
    # Hero Section
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-badge">✨ Next-Gen Giving Platform</div>
            <h1 class="hero-title">Intelligent Donation Management<br>& Resource Allocation</h1>
            <p class="hero-desc">
                Connecting compassionate donors with verified NGOs through AI-assisted image analysis 
                and smart requirement matching. Direct, transparent, and high-impact.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Action buttons
    col_a1, col_a2, col_a3, col_a4 = st.columns([1, 1, 1, 1])
    with col_a1:
        if st.button("🎁 Donate Items Now", type="primary", use_container_width=True):
            if st.session_state.get("is_authenticated") and st.session_state.get("role") == "Donor":
                st.session_state.current_page = "Donate Items"
            else:
                st.session_state.current_page = "Login"
            st.rerun()
    with col_a2:
        if st.button("🏢 Register as NGO", use_container_width=True):
            st.session_state.current_page = "Register NGO"
            st.rerun()
    with col_a3:
        if st.button("🔍 Explore NGOs", use_container_width=True):
            st.session_state.current_page = "Explore NGOs"
            st.rerun()
    with col_a4:
        if st.button("🏆 Donor Leaderboard", use_container_width=True):
            st.session_state.current_page = "Leaderboard"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Platform Impact KPIs
    total_donors = Donor.objects.count()
    approved_ngos = NGO.objects.filter(status="Approved").count()
    total_donations = Donation.objects.count()
    active_reqs = NGORequirement.objects.filter(is_active=True).count()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Active Donors", f"{total_donors}+", "👥", "Generous community members", "#38bdf8")
    with col2:
        render_kpi_card("Verified NGOs", f"{approved_ngos}", "🏢", "Vetted partner organizations", "#10b981")
    with col3:
        render_kpi_card("Items Donated", f"{total_donations}+", "📦", "Resources matched & distributed", "#8b5cf6")
    with col4:
        render_kpi_card("Active Needs", f"{active_reqs}", "🎯", "Current NGO requirements", "#f59e0b")

    st.markdown("<br><hr style='border-color: rgba(148, 163, 184, 0.15);'><br>", unsafe_allow_html=True)

    # Feature Highlights Grid
    st.markdown("<h2 style='text-align: center; color: #f8fafc;'>⚡ How SmartDonate AI Works</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 30px;'>A transparent, AI-driven end-to-end workflow</p>", unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-icon">📸</div>
                <div class="feature-title">1. AI Image Analysis</div>
                <div class="feature-text">
                    Simply upload a photo of your donation items. Google Gemini AI automatically identifies items, categories, and estimated quantities.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_col2:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">2. Smart Matching Engine</div>
                <div class="feature-text">
                    Our algorithm matches donations against verified NGO urgent requirements, prioritizing organizations with the highest need.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_col3:
        st.markdown(
            """
            <div class="feature-box">
                <div class="feature-icon">🚚</div>
                <div class="feature-title">3. Tracked Pickup & Delivery</div>
                <div class="feature-text">
                    Coordinate doorstep pickups, receive live status notifications (Confirmed, Dispatched, Delivered), and earn community ranking points.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Featured Approved NGOs
    st.markdown("### 🏢 Featured Partner NGOs")
    ngos = get_approved_ngos()[:3]
    if ngos:
        for ngo in ngos:
            render_ngo_card(ngo)
    else:
        st.info("NGOs registering on the platform will appear here once approved by the administrator.")
