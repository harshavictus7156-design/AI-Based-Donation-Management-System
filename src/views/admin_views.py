"""
Administrator Workspace views:
- Platform Dashboard KPIs & Analytics
- NGO Approvals, Verification & Management
- Donor Management (Active/Inactive Toggle)
- Platform-wide Donations & Allocations Oversight
- System Configuration & Secrets Audit
"""

import os
import streamlit as st
from src.models import (
    Donor,
    NGO,
    Donation,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
)
from src.services.admin_service import (
    get_admin_dashboard_stats,
    approve_ngo,
    reject_ngo,
    toggle_donor_status,
)
from src.services.donor_service import get_donor_leaderboard
from src.components.cards import render_kpi_card
from src.components.charts import render_category_pie_chart, render_status_bar_chart
from src.utils import get_status_badge, format_date, format_datetime
from src.config import (
    DB_ENGINE,
    DB_NAME,
    DB_HOST,
    GEMINI_API_KEY,
    ADMIN_EMAIL,
)


def render_admin_workspace(user: dict):
    """Main Administrator Workspace with sidebar navigation."""
    tabs = [
        "📊 Admin Dashboard",
        "🏢 NGO Approvals & Management",
        "👥 Donor Management",
        "📦 All Platform Donations",
        "🎯 NGO Requirements Oversight",
        "🚚 Pickups Tracker",
        "🏆 Platform Leaderboard",
        "⚙️ System Secrets & Settings",
    ]

    selected_tab = st.sidebar.radio("Admin Navigation", tabs, index=0)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="color: #f8fafc; margin: 0;">{selected_tab}</h2>
            <div style="color: #f59e0b; font-size: 0.9rem; font-weight: 700;">
                🛡️ Platform Administrator ({user.get('email', 'admin')})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "Admin Dashboard" in selected_tab:
        _render_admin_dashboard()
    elif "NGO Approvals" in selected_tab:
        _render_admin_ngos()
    elif "Donor Management" in selected_tab:
        _render_admin_donors()
    elif "All Platform Donations" in selected_tab:
        _render_admin_donations()
    elif "Requirements Oversight" in selected_tab:
        _render_admin_requirements()
    elif "Pickups Tracker" in selected_tab:
        _render_admin_pickups()
    elif "Leaderboard" in selected_tab:
        _render_admin_leaderboard()
    elif "System Secrets & Settings" in selected_tab:
        _render_admin_settings()


def _render_admin_dashboard():
    """Renders high-level platform statistics and KPIs."""
    stats = get_admin_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Donors", stats["total_donors"], "👥", f"{stats['active_donors']} active donors", "#38bdf8")
    with col2:
        render_kpi_card("NGO Organizations", stats["total_ngos"], "🏢", f"{stats['pending_ngos']} pending verification", "#f59e0b")
    with col3:
        render_kpi_card("Total Donations", stats["total_donations"], "📦", f"{stats['total_items']} items donated", "#8b5cf6")
    with col4:
        render_kpi_card("Allocations & Pickups", stats["total_allocations"], "🤝", f"{stats['completed_pickups']} completed pickups", "#10b981")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        # Category breakdown
        donations = Donation.objects.all()
        cats = {}
        for d in donations:
            cats[d.category] = cats.get(d.category, 0) + d.quantity
        render_category_pie_chart(cats, "Platform Resource Distribution by Category")
    with col_c2:
        # NGO verification status
        ngo_status = {
            "Approved": stats["approved_ngos"],
            "Pending": stats["pending_ngos"],
            "Rejected": stats["rejected_ngos"],
        }
        render_status_bar_chart(ngo_status, "NGO Partner Verification Status")

    st.markdown("<br>", unsafe_allow_html=True)

    # Pending Approvals Action Box
    pending_list = list(NGO.objects.filter(status="Pending").order_by("-registered_at"))
    if pending_list:
        st.markdown(f"### ⚠️ Pending NGO Applications Requiring Approval ({len(pending_list)})")
        for ngo in pending_list:
            with st.container():
                st.markdown(
                    f"""
                    <div class="glass-card" style="padding: 16px; margin-bottom: 12px; border-color: rgba(245, 158, 11, 0.4);">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <h4 style="margin: 0; color: #f8fafc;">🏢 {ngo.ngo_name}</h4>
                                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                                    Reg #{ngo.registration_no} • 📍 {ngo.city}, {ngo.state} • ✉️ {ngo.email_id}
                                </div>
                            </div>
                            <div>{get_status_badge(ngo.status)}</div>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.88rem; margin: 8px 0;">{ngo.description}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                col_app, col_rej, _ = st.columns([1, 1, 3])
                with col_app:
                    if st.button("✅ Approve NGO", key=f"dash_app_{ngo.id}", type="primary", use_container_width=True):
                        success, msg = approve_ngo(ngo.id)
                        st.success(msg)
                        st.rerun()
                with col_rej:
                    if st.button("❌ Reject NGO", key=f"dash_rej_{ngo.id}", use_container_width=True):
                        success, msg = reject_ngo(ngo.id)
                        st.warning(msg)
                        st.rerun()


def _render_admin_ngos():
    """Renders the comprehensive NGO Management interface."""
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        search = st.text_input("🔍 Search NGOs by name, registration #, city...", placeholder="Search organizations...")
    with col_f2:
        status_filter = st.selectbox("Status Filter", ["All", "Pending", "Approved", "Rejected"])

    qs = NGO.objects.all().order_by("-registered_at")
    if status_filter != "All":
        qs = qs.filter(status=status_filter)
    if search.strip():
        qs = qs.filter(ngo_name__icontains=search.strip()) | qs.filter(registration_no__icontains=search.strip()) | qs.filter(city__icontains=search.strip())

    ngos = list(qs)
    st.markdown(f"**Showing {len(ngos)} organization(s)**")

    for ngo in ngos:
        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="margin: 0; color: #f8fafc; font-size: 1.2rem;">🏢 {ngo.ngo_name}</h3>
                            <div style="color: #38bdf8; font-size: 0.85rem; margin-top: 4px;">
                                Registration #{ngo.registration_no} • 📍 {ngo.city}, {ngo.state} ({ngo.pincode})
                            </div>
                        </div>
                        <div>{get_status_badge(ngo.status)}</div>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.9rem; margin: 10px 0;">{ngo.description}</div>
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; font-size: 0.82rem; color: #94a3b8;">
                        <div>📞 <strong>Phone:</strong> {ngo.phone_no} | ✉️ <strong>Email:</strong> {ngo.email_id}</div>
                        <div>📍 <strong>Address:</strong> {ngo.address}</div>
                        <div>📅 <strong>Registered Date:</strong> {format_date(ngo.registered_at)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_a1, col_a2, col_a3 = st.columns([1, 1, 3])
            with col_a1:
                if ngo.status != "Approved":
                    if st.button("✅ Approve", key=f"app_{ngo.id}", type="primary", use_container_width=True):
                        success, msg = approve_ngo(ngo.id)
                        st.success(msg)
                        st.rerun()
            with col_a2:
                if ngo.status != "Rejected":
                    if st.button("❌ Reject", key=f"rej_{ngo.id}", use_container_width=True):
                        success, msg = reject_ngo(ngo.id)
                        st.warning(msg)
                        st.rerun()


def _render_admin_donors():
    """Renders Donor Management and Account Status controls."""
    search = st.text_input("🔍 Search donors by name, email, or city...", placeholder="Search community donors...")

    qs = Donor.objects.all().order_by("-registered_date")
    if search.strip():
        qs = qs.filter(name__icontains=search.strip()) | qs.filter(email__icontains=search.strip()) | qs.filter(city__icontains=search.strip())

    donors = list(qs)
    st.markdown(f"**Total Donors: {len(donors)}**")

    for donor in donors:
        donations_count = donor.donations.count()
        status_label = "Active" if donor.status_active else "Inactive"
        status_color = "#10b981" if donor.status_active else "#ef4444"

        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h4 style="margin: 0; color: #f8fafc;">👤 {donor.name}</h4>
                            <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                                ✉️ {donor.email} • 📞 {donor.phone} • 📍 {donor.city}, {donor.state}
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: {status_color}; font-weight: 700; font-size: 0.85rem;">● {status_label}</span>
                            <div style="color: #cbd5e1; font-size: 0.8rem; margin-top: 2px;">{donations_count} donations made</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_btn, _ = st.columns([2, 3])
            with col_btn:
                btn_label = "Deactivate Donor Account" if donor.status_active else "Reactivate Donor Account"
                if st.button(btn_label, key=f"tog_{donor.id}"):
                    success, msg, new_st = toggle_donor_status(donor.id)
                    st.info(msg)
                    st.rerun()


def _render_admin_donations():
    """Renders platform-wide donations list."""
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("🔍 Search donations by item or donor...", placeholder="Search all donations...")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Pending", "Accepted", "Rejected", "Collected"], key="admin_don_status")

    qs = Donation.objects.all().select_related("donor", "ngo").order_by("-donation_date")
    if status_filter != "All":
        qs = qs.filter(status=status_filter)
    if search.strip():
        qs = qs.filter(item_name__icontains=search.strip()) | qs.filter(donor__name__icontains=search.strip())

    donations = list(qs)
    st.markdown(f"**Total Platform Donations: {len(donations)}**")

    for don in donations:
        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0; color: #f8fafc;">📦 #{don.id} — {don.item_name} ({don.quantity} units)</h4>
                            <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                                Donor: <strong style="color: #f8fafc;">{don.donor.name}</strong> • Category: <strong>{don.category}</strong> • Condition: {don.condition}
                            </div>
                        </div>
                        <div>{get_status_badge(don.status)}</div>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.85rem; margin-top: 8px;">
                        📍 Pickup: {don.location} • 📅 Date: {format_date(don.donation_date)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_admin_requirements():
    """Renders all NGO requirements platform-wide."""
    reqs = list(NGORequirement.objects.all().select_related("ngo").order_by("-created_at"))
    st.markdown(f"**Total NGO Requirements: {len(reqs)}**")

    for r in reqs:
        st.markdown(
            f"""
            <div class="glass-card" style="padding: 16px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #f8fafc;">📋 {r.item_name} ({r.category})</h4>
                        <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 2px;">
                            NGO: <strong style="color: #38bdf8;">{r.ngo.ngo_name}</strong> • Priority: {get_status_badge(r.priority)}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #f8fafc; font-weight: 700;">{r.fulfilled_quantity} / {r.required_quantity} units</div>
                        <div style="color: {'#10b981' if r.is_active else '#94a3b8'}; font-size: 0.78rem;">{'Active' if r.is_active else 'Closed'}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_admin_pickups():
    """Renders platform-wide pickups tracker."""
    pickups = list(
        PickupRequest.objects.all()
        .select_related("allocation__donation__donor", "allocation__ngo")
        .order_by("-created_at")
    )
    st.markdown(f"**Total Pickup Requests: {len(pickups)}**")

    for p in pickups:
        a = p.allocation
        st.markdown(
            f"""
            <div class="glass-card" style="padding: 16px; margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin: 0; color: #f8fafc;">🚚 Pickup #{p.id} — {a.donation.item_name} ({a.allocated_quantity} units)</h4>
                        <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                            Donor: <strong>{a.donation.donor.name}</strong> → NGO: <strong>{a.ngo.ngo_name}</strong>
                        </div>
                    </div>
                    <div>{get_status_badge(p.status)}</div>
                </div>
                <div style="color: #cbd5e1; font-size: 0.82rem; margin-top: 8px;">
                    📍 {p.pickup_address} • 📅 Scheduled: {format_datetime(p.scheduled_time)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_admin_leaderboard():
    """Renders the platform-wide Leaderboard."""
    leaderboard = get_donor_leaderboard()
    st.markdown("### 🏆 Platform Donor Leaderboard")
    for entry in leaderboard:
        st.markdown(
            f"""
            <div class="leaderboard-row">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="font-size: 1.3rem; font-weight: 800; color: {entry['badge_color']}; width: 36px;">#{entry['rank']}</div>
                    <div>
                        <div style="font-weight: 700; color: #f8fafc;">{entry['name']} {entry['icon']}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">📍 {entry['city']}, {entry['state']} • {entry['tier']}</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.15rem; font-weight: 800; color: #38bdf8;">{entry['points']} pts</div>
                    <div style="font-size: 0.78rem; color: #cbd5e1;">{entry['total_donations']} donations ({entry['total_items']} items)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_admin_settings():
    """Renders system configuration and secrets diagnostic view."""
    st.markdown("### ⚙️ System Environment & Secrets Audit")

    has_gemini = bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())
    gemini_status = "✅ Configured (Active)" if has_gemini else "⚠️ Not Configured (Using Smart Heuristic Fallback)"

    st.markdown(
        f"""
        <div class="glass-card">
            <h4>System Status Overview</h4>
            <table style="width: 100%; color: #cbd5e1; font-size: 0.9rem;">
                <tr style="border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <td style="padding: 8px 0;"><strong>Database Engine:</strong></td>
                    <td style="padding: 8px 0; color: #38bdf8;">{DB_ENGINE.upper()}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <td style="padding: 8px 0;"><strong>Database Location / Host:</strong></td>
                    <td style="padding: 8px 0; color: #38bdf8;">{DB_HOST or DB_NAME}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <td style="padding: 8px 0;"><strong>Gemini Vision AI:</strong></td>
                    <td style="padding: 8px 0;">{gemini_status}</td>
                </tr>
                <tr style="border-bottom: 1px solid rgba(148, 163, 184, 0.1);">
                    <td style="padding: 8px 0;"><strong>Admin Account:</strong></td>
                    <td style="padding: 8px 0; color: #f59e0b;">{ADMIN_EMAIL}</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )
