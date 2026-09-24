"""
Navigation bar and Header component.
Displays branding, active user info, role badge, notifications count, and navigation actions.
"""

import streamlit as st
from src.auth import logout, get_current_user, get_current_role
from src.services.notification_service import get_unread_count


def render_header():
    """Renders the top navigation header."""
    user = get_current_user()
    role = get_current_role()
    is_auth = st.session_state.get("is_authenticated", False)
    
    unread_count = get_unread_count(user) if is_auth else 0

    col1, col2 = st.columns([3, 2], vertical_alignment="center")

    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                <span style="font-size: 2rem;">🤝</span>
                <div>
                    <span class="brand-title">SmartDonate AI</span>
                    <div class="brand-subtitle">Intelligent Resource Matching & Distribution Platform</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        if is_auth:
            user_name = user.get("name", "User")
            role_colors = {
                "Donor": "#38bdf8",
                "NGO": "#10b981",
                "Admin": "#f59e0b",
            }
            color = role_colors.get(role, "#a78bfa")
            
            c_info, c_btn = st.columns([3, 2], vertical_alignment="center")
            with c_info:
                st.markdown(
                    f"""
                    <div style="text-align: right;">
                        <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">{user_name}</div>
                        <span style="
                            display: inline-block;
                            padding: 2px 10px;
                            background: {color}20;
                            border: 1px solid {color}60;
                            color: {color};
                            border-radius: 9999px;
                            font-size: 0.72rem;
                            font-weight: 700;
                            text-transform: uppercase;
                        ">
                            {role} Workspace
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_btn:
                if st.button("🚪 Logout", key="header_logout_btn", use_container_width=True):
                    logout()
        else:
            c_home, c_login, c_reg = st.columns([1, 1, 1], vertical_alignment="center")
            with c_home:
                if st.button("🏠 Home", use_container_width=True):
                    st.session_state.current_page = "Home"
                    st.rerun()
            with c_login:
                if st.button("🔑 Login", use_container_width=True):
                    st.session_state.current_page = "Login"
                    st.rerun()
            with c_reg:
                if st.button("✨ Register", use_container_width=True):
                    st.session_state.current_page = "Register"
                    st.rerun()

    st.markdown("<hr style='border-color: rgba(148, 163, 184, 0.15); margin-top: 6px; margin-bottom: 18px;' />", unsafe_allow_html=True)
