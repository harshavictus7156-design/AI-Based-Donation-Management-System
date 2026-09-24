"""
Authentication module for the Streamlit application.
Provides secure password hashing (PBKDF2/Django hasher), session state initialization,
and multi-role login / logout / registration validation for Donors, NGOs, and Administrators.
"""

import streamlit as st
from django.contrib.auth.hashers import check_password, make_password

from src.models import Donor, NGO
from src.config import ADMIN_EMAIL, ADMIN_PASSWORD


def init_session_state():
    """Initializes standard session state variables for the current session."""
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"
    if "theme" not in st.session_state:
        st.session_state.theme = "violet-dark"
    if "selected_ngo_id" not in st.session_state:
        st.session_state.selected_ngo_id = None
    if "active_donation_id" not in st.session_state:
        st.session_state.active_donation_id = None


def hash_password(password: str) -> str:
    """Safely hashes a plain-text password using Django PBKDF2."""
    return make_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed string."""
    try:
        return check_password(plain_password, hashed_password)
    except Exception:
        return False


def login(email: str, password: str, expected_role: str = None) -> tuple[bool, str, dict]:
    """
    Attempts to authenticate a user across Donor, NGO, and Admin roles.
    Returns (success, message, user_dict).
    """
    clean_email = email.strip().lower()
    clean_password = password.strip()

    if not clean_email or not clean_password:
        return False, "Email and password are required.", {}

    # 1. Check Admin Credentials
    if (
        clean_email == ADMIN_EMAIL.strip().lower()
        and clean_password == ADMIN_PASSWORD.strip()
    ):
        user_data = {
            "id": 1,
            "name": "Platform Administrator",
            "email": clean_email,
            "role": "Admin",
            "picture": None,
        }
        st.session_state.is_authenticated = True
        st.session_state.user = user_data
        st.session_state.role = "Admin"
        st.session_state.current_page = "Admin Dashboard"
        return True, "Welcome, Administrator!", user_data

    # 2. Check Donor Account
    if expected_role in (None, "Donor"):
        try:
            donor = Donor.objects.filter(email__iexact=clean_email).first()
            if donor:
                if not donor.status_active:
                    return False, "Your donor account is deactivated. Please contact support.", {}
                if verify_password(clean_password, donor.password):
                    user_data = {
                        "id": donor.id,
                        "name": donor.name,
                        "email": donor.email,
                        "phone": donor.phone,
                        "role": "Donor",
                        "city": donor.city,
                        "state": donor.state,
                        "pincode": donor.pincode,
                        "address": donor.address,
                        "language": donor.language_preference,
                        "picture": donor.picture.url if donor.picture else None,
                    }
                    st.session_state.is_authenticated = True
                    st.session_state.user = user_data
                    st.session_state.role = "Donor"
                    st.session_state.current_page = "Donor Dashboard"
                    return True, f"Welcome back, {donor.name}!", user_data
        except Exception as e:
            print(f"Donor auth check error: {e}")

    # 3. Check NGO Account
    if expected_role in (None, "NGO"):
        try:
            ngo = NGO.objects.filter(email_id__iexact=clean_email).first()
            if ngo:
                if verify_password(clean_password, ngo.password):
                    if ngo.status == "Rejected":
                        return False, "Your NGO application was rejected by the administration.", {}
                    
                    user_data = {
                        "id": ngo.id,
                        "name": ngo.ngo_name,
                        "email": ngo.email_id,
                        "phone": ngo.phone_no,
                        "role": "NGO",
                        "registration_no": ngo.registration_no,
                        "status": ngo.status,
                        "city": ngo.city,
                        "state": ngo.state,
                        "pincode": ngo.pincode,
                        "address": ngo.address,
                        "website": ngo.website_link,
                        "description": ngo.description,
                        "picture": ngo.picture.url if ngo.picture else None,
                        "certificate": ngo.certificate_files.url if ngo.certificate_files else None,
                    }
                    st.session_state.is_authenticated = True
                    st.session_state.user = user_data
                    st.session_state.role = "NGO"
                    st.session_state.current_page = "NGO Dashboard"
                    return True, f"Welcome back, {ngo.ngo_name}!", user_data
        except Exception as e:
            print(f"NGO auth check error: {e}")

    return False, "Invalid email or password. Please try again.", {}


def logout():
    """Logs the current user out and clears session state."""
    st.session_state.is_authenticated = False
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.current_page = "Home"
    st.session_state.selected_ngo_id = None
    st.session_state.active_donation_id = None
    st.rerun()


def get_current_user() -> dict:
    """Returns the current authenticated user dictionary or empty dict."""
    return st.session_state.get("user") or {}


def get_current_role() -> str:
    """Returns the current user role: 'Donor', 'NGO', 'Admin', or None."""
    return st.session_state.get("role")
