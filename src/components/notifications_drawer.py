"""
Notification center component for Donors, NGOs, and Admins.
"""

import streamlit as st
from src.services.notification_service import (
    get_user_notifications,
    mark_notification_read,
    mark_all_read,
    delete_notification,
)
from src.utils import format_datetime


def render_notifications_view(user: dict):
    """Renders the full notification management panel."""
    st.markdown("### 🔔 Notifications Center")

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("✓ Mark All as Read", use_container_width=True):
            mark_all_read(user)
            st.success("All notifications marked as read.")
            st.rerun()

    notifications = get_user_notifications(user)
    if not notifications:
        st.markdown(
            """
            <div style="text-align: center; padding: 40px; color: #94a3b8;">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">📭</div>
                <h4>No notifications yet</h4>
                <p>You will receive updates here as donations and pickups progress.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for notif in notifications:
        unread_indicator = "🔵 " if not notif.is_read else ""
        bg = "rgba(124, 58, 237, 0.1)" if not notif.is_read else "rgba(30, 41, 59, 0.4)"
        border = "rgba(139, 92, 246, 0.4)" if not notif.is_read else "rgba(148, 163, 184, 0.1)"

        with st.container():
            st.markdown(
                f"""
                <div style="background: {bg}; border: 1px solid {border}; border-radius: 12px; padding: 14px 18px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{unread_indicator}{notif.title}</span>
                        <span style="color: #94a3b8; font-size: 0.78rem;">{format_datetime(notif.created_at)}</span>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.4;">{notif.message}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            col_r, col_d, _ = st.columns([1, 1, 4])
            with col_r:
                if not notif.is_read:
                    if st.button("Mark Read", key=f"read_{notif.id}", use_container_width=True):
                        mark_notification_read(notif.id)
                        st.rerun()
            with col_d:
                if st.button("Delete", key=f"del_{notif.id}", use_container_width=True):
                    delete_notification(notif.id)
                    st.rerun()
