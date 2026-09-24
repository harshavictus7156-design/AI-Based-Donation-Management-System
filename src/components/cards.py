"""
Reusable UI card components for KPIs, donation items, NGO directory, requirements, and leaderboard.
"""

import streamlit as st
from src.utils import get_status_badge, format_date, format_datetime


def render_kpi_card(title: str, value: str or int, icon: str, subtext: str = "", border_color: str = "#8b5cf6"):
    """Renders a modern glowing metric KPI card."""
    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 3px solid {border_color};">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-subtext">{subtext}</div>' if subtext else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ngo_card(ngo, on_view_details=None):
    """Renders an NGO presentation card in exploration directory."""
    with st.container():
        st.markdown(
            f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                    <div>
                        <h3 style="margin: 0; color: #f8fafc; font-size: 1.25rem;">🏢 {ngo.ngo_name}</h3>
                        <div style="color: #38bdf8; font-size: 0.85rem; font-weight: 500; margin-top: 4px;">
                            📍 {ngo.city}, {ngo.state} • Reg #{ngo.registration_no}
                        </div>
                    </div>
                    <div>{get_status_badge(ngo.status)}</div>
                </div>
                <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.5; margin-bottom: 14px;">
                    {ngo.description[:180] + '...' if len(ngo.description) > 180 else (ngo.description or 'No description provided.')}
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.82rem; color: #94a3b8; border-top: 1px solid rgba(148, 163, 184, 0.1); padding-top: 10px;">
                    <span>📞 {ngo.phone_no}</span>
                    <span>✉️ {ngo.email_id}</span>
                    {f'<span>🌐 <a href="{ngo.website_link}" target="_blank" style="color: #a78bfa;">Website</a></span>' if ngo.website_link else ''}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_donation_summary_card(donation):
    """Renders a card for a donation item with its status, allocations, and pickup details."""
    allocations = list(donation.allocations.all())
    st.markdown(
        f"""
        <div class="glass-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                <div>
                    <h4 style="margin: 0; color: #f8fafc; font-size: 1.15rem;">📦 {donation.item_name}</h4>
                    <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                        Category: <strong style="color: #e2e8f0;">{donation.category}</strong> • 
                        Qty: <strong style="color: #38bdf8;">{donation.quantity}</strong> • 
                        Condition: <strong style="color: #a78bfa;">{donation.condition}</strong>
                    </div>
                </div>
                <div>{get_status_badge(donation.status)}</div>
            </div>
            <p style="color: #cbd5e1; font-size: 0.88rem; margin-bottom: 10px;">
                {donation.description or 'No extra notes.'}
            </p>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; font-size: 0.82rem; color: #94a3b8;">
                <div>📍 <strong>Pickup Location:</strong> {donation.location}</div>
                <div>📅 <strong>Submitted:</strong> {format_date(donation.donation_date)}</div>
                {f'<div>🚚 <strong>Pickup Status:</strong> {donation.pickup_status} ({donation.pickup_date})</div>' if donation.pickup_date else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
