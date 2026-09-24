"""
Authentication views for Login, Donor Registration, and NGO Registration.
"""

import streamlit as st
from src.auth import login
from src.services.donor_service import register_donor
from src.services.ngo_service import register_ngo
from src.utils import save_uploaded_file
from src.config import DONOR_PICS_DIR, NGO_PICS_DIR, NGO_CERTS_DIR


def render_login_view():
    """Renders the Unified Multi-Role Login interface."""
    st.markdown(
        """
        <div style="max-width: 460px; margin: 0 auto; text-align: center; margin-bottom: 24px;">
            <span style="font-size: 2.5rem;">🔐</span>
            <h2 style="color: #f8fafc; margin-top: 8px;">Sign In to SmartDonate</h2>
            <p style="color: #94a3b8; font-size: 0.9rem;">
                Access your Donor, NGO, or Administrator account
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        with st.form("login_form", clear_on_submit=False):
            role_tab = st.selectbox(
                "I am signing in as:",
                ["Donor", "NGO Organization", "Administrator"],
                index=0,
            )
            email = st.text_input("Email Address", placeholder="e.g. donor@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")

            submit = st.form_submit_button("Sign In →", type="primary", use_container_width=True)

            if submit:
                target_role = "Donor" if "Donor" in role_tab else ("NGO" if "NGO" in role_tab else "Admin")
                success, message, user_data = login(email, password, target_role)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="text-align: center; color: #94a3b8; font-size: 0.88rem;">
                Don't have an account yet?
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Register as Donor", use_container_width=True):
                st.session_state.current_page = "Register Donor"
                st.rerun()
        with col_b2:
            if st.button("Register as NGO", use_container_width=True):
                st.session_state.current_page = "Register NGO"
                st.rerun()


def render_donor_register_view():
    """Renders the Donor Registration Form."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 2.2rem;">👤</span>
            <h2 style="color: #f8fafc;">Join as a Community Donor</h2>
            <p style="color: #94a3b8;">Create your profile to start donating items and tracking your impact.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        with st.form("donor_register_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name *", placeholder="Jane Doe")
                email = st.text_input("Email Address *", placeholder="jane@example.com")
                phone = st.text_input("Phone Number *", placeholder="10-digit number")
                password = st.text_input("Password *", type="password")
            with col2:
                city = st.text_input("City *", placeholder="e.g. New York")
                state = st.text_input("State *", placeholder="e.g. NY")
                pincode = st.text_input("Pincode / Postal Code *", placeholder="e.g. 10001")
                language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Hindi", "Other"])

            address = st.text_area("Full Default Pickup Address *", placeholder="Street address, apartment/unit, landmarks...")
            picture_file = st.file_uploader("Profile Picture (Optional)", type=["jpg", "jpeg", "png", "webp"])

            submit = st.form_submit_button("Complete Donor Registration →", type="primary", use_container_width=True)

            if submit:
                if not name or not email or not password or not address or not city or not state or not pincode:
                    st.error("Please fill in all required fields marked with *.")
                else:
                    pic_path = save_uploaded_file(picture_file, str(DONOR_PICS_DIR)) if picture_file else None
                    success, msg, donor = register_donor({
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "password": password,
                        "address": address,
                        "city": city,
                        "state": state,
                        "pincode": pincode,
                        "language_preference": language,
                        "picture": pic_path,
                    })
                    if success:
                        st.success(msg)
                        st.info("Please sign in with your new credentials.")
                        st.session_state.current_page = "Login"
                        st.rerun()
                    else:
                        st.error(msg)


def render_ngo_register_view():
    """Renders the NGO Organization Registration Form."""
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 24px;">
            <span style="font-size: 2.2rem;">🏢</span>
            <h2 style="color: #f8fafc;">Register Your Non-Profit Organization</h2>
            <p style="color: #94a3b8;">Connect with donors, publish resource requirements, and receive verified donations.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        with st.form("ngo_register_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                ngo_name = st.text_input("Organization Name *", placeholder="e.g. Hope Foundation")
                registration_no = st.text_input("Govt Registration / 80G / 501(c)(3) Number *")
                email_id = st.text_input("Official Email Address *", placeholder="contact@hopefoundation.org")
                phone_no = st.text_input("Contact Phone Number *", placeholder="10-digit number")
                password = st.text_input("Password *", type="password")
            with col2:
                website_link = st.text_input("Website URL (Optional)", placeholder="https://hopefoundation.org")
                city = st.text_input("City *", placeholder="e.g. Chicago")
                state = st.text_input("State *", placeholder="e.g. IL")
                pincode = st.text_input("Pincode / Postal Code *", placeholder="e.g. 60601")
                language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Hindi", "Other"])

            description = st.text_area("Mission Statement & Description *", placeholder="Briefly describe your organization's mission and impact areas...")
            address = st.text_area("Official Operating Address *", placeholder="Full street address of your facility or warehouse...")

            col_u1, col_u2 = st.columns(2)
            with col_u1:
                certificate_file = st.file_uploader("Upload Registration Certificate (PDF/Image) *", type=["pdf", "jpg", "jpeg", "png"])
            with col_u2:
                picture_file = st.file_uploader("Upload Organization Logo / Photo", type=["jpg", "jpeg", "png", "webp"])

            submit = st.form_submit_button("Submit NGO Application for Verification →", type="primary", use_container_width=True)

            if submit:
                if not ngo_name or not registration_no or not email_id or not password or not address or not description:
                    st.error("Please fill in all required fields marked with *.")
                else:
                    cert_path = save_uploaded_file(certificate_file, str(NGO_CERTS_DIR)) if certificate_file else None
                    pic_path = save_uploaded_file(picture_file, str(NGO_PICS_DIR)) if picture_file else None

                    success, msg, ngo = register_ngo({
                        "ngo_name": ngo_name,
                        "registration_no": registration_no,
                        "email_id": email_id,
                        "phone_no": phone_no,
                        "password": password,
                        "website_link": website_link,
                        "city": city,
                        "state": state,
                        "pincode": pincode,
                        "language": language,
                        "description": description,
                        "address": address,
                        "certificate_files": cert_path,
                        "picture": pic_path,
                    })
                    if success:
                        st.success(msg)
                        st.info("Your application has been received. Our admin team will review your credentials.")
                        st.session_state.current_page = "Login"
                        st.rerun()
                    else:
                        st.error(msg)
