"""
Donor Workspace views:
- Dashboard
- Donate Items (with Gemini AI Vision Analysis & Intelligent Matching)
- My Donations & Pickups
- Explore Approved NGOs & Requirements
- Leaderboard & Points Ranking
- Profile & Settings
- Notifications
"""

import datetime
from PIL import Image
import streamlit as st

from src.models import (
    Donation,
    NGO,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
)
from src.services.donor_service import (
    get_donor_dashboard_stats,
    get_donor_donations,
    get_donor_leaderboard,
    update_donor_profile,
)
from src.services.donation_service import (
    create_donation,
    update_donation,
    allocate_donation,
    create_or_update_pickup_request,
    cancel_pickup_request,
)
from src.services.ai_service import (
    analyze_image_with_gemini,
    find_matching_ngos,
)
from src.services.ngo_service import get_approved_ngos
from src.services.notification_service import (
    get_user_notifications,
    mark_notification_read,
    mark_all_read,
    delete_notification,
)
from src.components.cards import render_kpi_card, render_ngo_card
from src.components.charts import render_category_pie_chart, render_status_bar_chart
from src.utils import get_status_badge, format_date, format_datetime, save_uploaded_file
from src.config import DONATION_ITEMS_DIR, DONOR_PICS_DIR


def render_donor_workspace(user: dict, initial_tab: str = "Dashboard"):
    """Main Donor Workspace with sub-tab navigation."""
    tabs = [
        "📊 Dashboard",
        "🎁 Donate Items",
        "📦 My Donations",
        "🏢 Explore NGOs",
        "🏆 Leaderboard",
        "🔔 Notifications",
        "⚙️ Profile & Settings",
    ]

    selected_tab = st.sidebar.radio("Donor Navigation", tabs, index=0)

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="color: #f8fafc; margin: 0;">{selected_tab}</h2>
            <div style="color: #38bdf8; font-size: 0.9rem; font-weight: 600;">
                Donor: {user.get('name')} (📍 {user.get('city', 'Community')})
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "Dashboard" in selected_tab:
        _render_donor_dashboard(user)
    elif "Donate Items" in selected_tab:
        _render_donate_item(user)
    elif "My Donations" in selected_tab:
        _render_my_donations(user)
    elif "Explore NGOs" in selected_tab:
        _render_explore_ngos(user)
    elif "Leaderboard" in selected_tab:
        _render_donor_leaderboard(user)
    elif "Notifications" in selected_tab:
        _render_donor_notifications(user)
    elif "Profile & Settings" in selected_tab:
        _render_donor_profile_settings(user)


def _render_donor_dashboard(user: dict):
    """Renders the Donor Dashboard view."""
    stats = get_donor_dashboard_stats(user["id"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Donations", stats["total_donations"], "📦", f"{stats['total_items']} items donated", "#38bdf8")
    with col2:
        render_kpi_card("Active / Pending", stats["pending"], "⏳", "Awaiting allocation / pickup", "#f59e0b")
    with col3:
        render_kpi_card("Accepted & Delivered", stats["collected"] + stats["accepted"], "✅", "Received by verified NGOs", "#10b981")
    with col4:
        render_kpi_card("Community Rank", f"#{stats['rank']} {stats['rank_icon']}", "🏆", f"{stats['impact_points']} Impact Points ({stats['rank_tier']})", stats["rank_color"])

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts and Recent Activity
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        donations = Donation.objects.filter(donor_id=user["id"])
        cats = {}
        for d in donations:
            cats[d.category] = cats.get(d.category, 0) + d.quantity
        render_category_pie_chart(cats, "Your Donated Items by Category")
    with col_c2:
        status_data = {
            "Pending": stats["pending"],
            "Accepted": stats["accepted"],
            "Collected": stats["collected"],
        }
        render_status_bar_chart(status_data, "Donation Lifecycle Status")

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent Donations
    st.markdown("### 🕒 Recent Donation Activity")
    recent = get_donor_donations(user["id"])[:5]
    if recent:
        for don in recent:
            with st.container():
                st.markdown(
                    f"""
                    <div class="glass-card" style="padding: 16px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="color: #f8fafc; font-size: 1.05rem;">📦 {don.item_name}</strong>
                                <span style="color: #94a3b8; font-size: 0.85rem; margin-left: 10px;">
                                    ({don.quantity} units • {don.category})
                                </span>
                            </div>
                            <div>{get_status_badge(don.status)}</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; color: #94a3b8; font-size: 0.82rem; margin-top: 8px;">
                            <span>📍 {don.location}</span>
                            <span>📅 {format_date(don.donation_date)}</span>
                            <span>🚚 Pickup: {don.pickup_status}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("You haven't made any donations yet. Click '🎁 Donate Items' to make your first contribution!")


def _render_donate_item(user: dict):
    """Renders the AI-Assisted Donation Creation and Smart Allocation Form."""
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <p style="color: #cbd5e1;">
                Create a new donation. Upload an image to let our <strong>Gemini AI Vision</strong> scan and automatically fill item details, or fill the details manually.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. AI Image Upload and Scan Step
    with st.expander("📸 Step 1: Upload Photo for AI Item Detection (Optional)", expanded=True):
        uploaded_image = st.file_uploader(
            "Upload image of items to donate (JPG, PNG, WEBP)",
            type=["jpg", "jpeg", "png", "webp"],
            key="donate_img_uploader",
        )

        detected_item_name = ""
        detected_category = "Clothing"
        detected_quantity = 1

        if uploaded_image:
            col_i1, col_i2 = st.columns([1, 2])
            with col_i1:
                st.image(uploaded_image, caption="Uploaded Donation Item", use_container_width=True)
            with col_i2:
                if st.button("🤖 Analyze Image with Gemini AI", type="primary"):
                    with st.spinner("Analyzing image features, category, and quantities with Google Gemini AI..."):
                        res = analyze_image_with_gemini(uploaded_image)
                        if res.get("success") and res.get("items"):
                            items = res["items"]
                            first_item = items[0]
                            st.session_state["ai_detected_item"] = first_item.get("item", "")
                            st.session_state["ai_detected_category"] = first_item.get("category", "Other")
                            st.session_state["ai_detected_quantity"] = int(first_item.get("quantity", 1))
                            st.session_state["ai_confidence"] = first_item.get("confidence", 0.9)
                            st.success(f"AI Detected: **{first_item.get('item')}** ({first_item.get('category')}) • Quantity: {first_item.get('quantity')}")
                        else:
                            st.warning(res.get("message", "Unable to detect items from image. You can enter details below."))

                if "ai_detected_item" in st.session_state:
                    detected_item_name = st.session_state.get("ai_detected_item", "")
                    detected_category = st.session_state.get("ai_detected_category", "Clothing")
                    detected_quantity = st.session_state.get("ai_detected_quantity", 1)
                    conf = st.session_state.get("ai_confidence", 0.9)
                    st.markdown(
                        f"""
                        <div class="ai-callout">
                            <div class="ai-callout-title">✨ AI Detection Result</div>
                            <div>Item: <strong>{detected_item_name}</strong> | Category: <strong>{detected_category}</strong> | Conf: <strong>{int(conf*100)}%</strong></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # 2. Donation Details Form
    st.markdown("### 📝 Step 2: Donation Details")
    categories_list = ["Clothing", "Books", "Food", "Electronics", "Furniture", "Medical Supplies", "School Supplies", "Other"]
    cat_index = categories_list.index(detected_category) if detected_category in categories_list else 0

    with st.form("donation_submission_form"):
        col1, col2 = st.columns(2)
        with col1:
            item_name = st.text_input("Item Name / Description *", value=detected_item_name, placeholder="e.g. Winter Jackets, Rice 10kg, Textbooks...")
            category = st.selectbox("Category *", categories_list, index=cat_index)
            quantity = st.number_input("Quantity *", min_value=1, value=max(1, detected_quantity), step=1)
            condition = st.selectbox("Item Condition *", ["New", "Like New", "Good", "Used"], index=1)
        with col2:
            default_address = user.get("address", "") + (f", {user.get('city')}" if user.get('city') else "")
            location = st.text_area("Pickup Address *", value=default_address, placeholder="Enter exact doorstep pickup address...")
            description = st.text_area("Notes / Specifications (Optional)", placeholder="Size, brand, packaging condition...")

        st.markdown("#### 🚚 Pickup Coordination")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pickup_date = st.date_input("Preferred Pickup Date", value=datetime.date.today() + datetime.timedelta(days=1), min_value=datetime.date.today())
        with col_p2:
            pickup_time = st.selectbox("Preferred Time Slot", ["Morning (9 AM - 12 PM)", "Afternoon (12 PM - 4 PM)", "Evening (4 PM - 8 PM)"])
        pickup_notes = st.text_input("Pickup Instructions (Optional)", placeholder="Gate code, landmark, call upon arrival...")

        submit_donation = st.form_submit_button("Submit Donation & Find Matching NGOs →", type="primary", use_container_width=True)

        if submit_donation:
            if not item_name or not location:
                st.error("Please fill in Item Name and Pickup Location.")
            else:
                img_path = save_uploaded_file(uploaded_image, str(DONATION_ITEMS_DIR)) if uploaded_image else None
                success, msg, new_don = create_donation(
                    donor_id=user["id"],
                    item_name=item_name,
                    category=category,
                    quantity=quantity,
                    condition=condition,
                    description=description,
                    location=location,
                    image_path=img_path,
                    pickup_date=pickup_date,
                    pickup_time=pickup_time,
                    pickup_notes=pickup_notes,
                )
                if success:
                    st.session_state["active_donation_id"] = new_don.id
                    st.success(f"Donation #{new_don.id} created successfully!")
                    st.rerun()
                else:
                    st.error(msg)

    # 3. If an active donation is selected, show Matching & Allocation Section
    active_don_id = st.session_state.get("active_donation_id")
    if active_don_id:
        don = Donation.objects.filter(id=active_don_id, donor_id=user["id"]).first()
        if don and don.status == "Pending":
            st.markdown("<br><hr style='border-color: rgba(148, 163, 184, 0.15);'><br>", unsafe_allow_html=True)
            st.markdown(f"### 🎯 Step 3: Match & Allocate Donation #{don.id} ({don.item_name} - Qty {don.quantity})")
            
            matching_ngos = find_matching_ngos(don.item_name, don.category, don.quantity)
            
            if matching_ngos:
                best = matching_ngos[0]
                st.markdown(
                    f"""
                    <div class="ai-callout">
                        <div class="ai-callout-title">🤖 AI Top Recommendation: {best['ngo_name']} ({best['priority'].upper()} Priority)</div>
                        <div style="font-size: 0.95rem; color: #e9d5ff; margin-bottom: 6px;">{best['ai_reason']}</div>
                        <div style="font-size: 0.85rem; color: #cbd5e1;">📍 {best['city']}, {best['state']} • Needed: {best['remaining_need']} • Recommended: {best['recommended_quantity']} units</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_alloc_btn, _ = st.columns([2, 3])
                with col_alloc_btn:
                    if st.button(f"⚡ Accept AI Allocation to {best['ngo_name']} ({best['recommended_quantity']} units)", type="primary"):
                        success, alloc_msg = allocate_donation(
                            donation_id=don.id,
                            donor_id=user["id"],
                            allocations_list=[{
                                "ngo_id": best["ngo_id"],
                                "requirement_id": best["requirement_id"],
                                "quantity": best["recommended_quantity"],
                            }],
                            pickup_date=don.pickup_date,
                            pickup_time=don.pickup_time,
                        )
                        if success:
                            st.success(alloc_msg)
                            st.session_state["active_donation_id"] = None
                            st.rerun()
                        else:
                            st.error(alloc_msg)

                st.markdown("#### Or Choose from All Matching Verified NGOs:")
                for m in matching_ngos:
                    with st.container():
                        st.markdown(
                            f"""
                            <div class="glass-card" style="padding: 16px; margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <h4 style="margin: 0; color: #f8fafc;">🏢 {m['ngo_name']}</h4>
                                        <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                                            Requirement: <strong style="color: #38bdf8;">{m['item_name']}</strong> ({m['category']}) • Priority: {get_status_badge(m['priority'])}
                                        </div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="color: #cbd5e1; font-size: 0.88rem;">Needed: <strong>{m['remaining_need']}</strong> units</div>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        c_qty, c_btn = st.columns([1, 2])
                        with c_qty:
                            custom_qty = st.number_input(f"Quantity for {m['ngo_name']}", min_value=1, max_value=min(don.quantity, m['remaining_need']), value=min(don.quantity, m['remaining_need']), key=f"alloc_qty_{m['requirement_id']}")
                        with c_btn:
                            if st.button(f"Allocate to {m['ngo_name']}", key=f"btn_alloc_{m['requirement_id']}"):
                                success, alloc_msg = allocate_donation(
                                    donation_id=don.id,
                                    donor_id=user["id"],
                                    allocations_list=[{
                                        "ngo_id": m["ngo_id"],
                                        "requirement_id": m["requirement_id"],
                                        "quantity": custom_qty,
                                    }],
                                    pickup_date=don.pickup_date,
                                    pickup_time=don.pickup_time,
                                )
                                if success:
                                    st.success(alloc_msg)
                                    st.session_state["active_donation_id"] = None
                                    st.rerun()
                                else:
                                    st.error(alloc_msg)
            else:
                st.info("No approved NGO currently has an active matching requirement for this specific item. You can explore all verified NGOs in 'Explore NGOs' or leave it listed as Pending for NGOs to discover.")


def _render_my_donations(user: dict):
    """Renders the My Donations management interface."""
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search = st.text_input("🔍 Search donations by item or NGO...", placeholder="Type item name...")
    with col_s2:
        status_filter = st.selectbox("Status Filter", ["All", "Pending", "Accepted", "Rejected", "Collected"])
    with col_s3:
        category_filter = st.selectbox("Category Filter", ["All", "Clothing", "Books", "Food", "Electronics", "Furniture", "Medical Supplies", "School Supplies", "Other"])

    donations = get_donor_donations(user["id"], search, status_filter, category_filter)

    if not donations:
        st.info("No donations found matching your query.")
        return

    st.markdown(f"**Showing {len(donations)} donation(s)**")

    for don in donations:
        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="margin: 0; color: #f8fafc; font-size: 1.2rem;">📦 #{don.id} — {don.item_name}</h3>
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                                Category: <strong style="color: #e2e8f0;">{don.category}</strong> • 
                                Quantity: <strong style="color: #38bdf8;">{don.quantity} units</strong> • 
                                Condition: <strong style="color: #a78bfa;">{don.condition}</strong>
                            </div>
                        </div>
                        <div>{get_status_badge(don.status)}</div>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.9rem; margin: 10px 0;">
                        {don.description or 'No extra notes provided.'}
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 12px 16px; border-radius: 10px; font-size: 0.82rem; color: #94a3b8; margin-bottom: 12px;">
                        <div>📍 <strong>Pickup Location:</strong> {don.location}</div>
                        <div>📅 <strong>Submitted On:</strong> {format_date(don.donation_date)}</div>
                        <div>🚚 <strong>Pickup Status:</strong> {don.pickup_status} {f'({don.pickup_date} • {don.pickup_time})' if don.pickup_date else ''}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Actions Row
            col_a1, col_a2, col_a3, _ = st.columns([1, 1, 1, 2])
            with col_a1:
                if don.status == "Pending":
                    if st.button("🎯 Smart Match", key=f"match_{don.id}", use_container_width=True):
                        st.session_state["active_donation_id"] = don.id
                        st.session_state.current_page = "Donate Items"
                        st.rerun()
            with col_a2:
                # Schedule / Update Pickup
                with st.popover("🚚 Pickup Options", use_container_width=True):
                    st.markdown("#### Schedule / Reschedule Pickup")
                    new_date = st.date_input("Pickup Date", value=don.pickup_date or (datetime.date.today() + datetime.timedelta(days=1)), key=f"pk_date_{don.id}")
                    new_slot = st.selectbox("Slot", ["Morning (9 AM - 12 PM)", "Afternoon (12 PM - 4 PM)", "Evening (4 PM - 8 PM)"], key=f"pk_slot_{don.id}")
                    new_notes = st.text_input("Notes", value=don.location, key=f"pk_notes_{don.id}")
                    if st.button("Save Pickup Schedule", key=f"save_pk_{don.id}"):
                        don.pickup_date = new_date
                        don.pickup_time = new_slot
                        don.pickup_status = "Scheduled"
                        don.save()
                        st.success("Pickup scheduled successfully!")
                        st.rerun()

                    # Cancel pickup option
                    if don.pickup_status in ["Scheduled", "Confirmed"]:
                        if st.button("Cancel Pickup Request", key=f"cancel_pk_{don.id}"):
                            don.pickup_status = "Cancelled"
                            don.save()
                            st.warning("Pickup cancelled.")
                            st.rerun()
            with col_a3:
                if don.status == "Pending":
                    with st.popover("✏️ Edit", use_container_width=True):
                        e_name = st.text_input("Item Name", value=don.item_name, key=f"edit_name_{don.id}")
                        e_qty = st.number_input("Quantity", min_value=1, value=don.quantity, key=f"edit_qty_{don.id}")
                        e_loc = st.text_area("Location", value=don.location, key=f"edit_loc_{don.id}")
                        if st.button("Save Changes", key=f"save_edit_{don.id}"):
                            success, msg = update_donation(
                                donation_id=don.id,
                                donor_id=user["id"],
                                item_name=e_name,
                                category=don.category,
                                quantity=e_qty,
                                condition=don.condition,
                                description=don.description,
                                location=e_loc,
                            )
                            if success:
                                st.success("Updated successfully.")
                                st.rerun()
                            else:
                                st.error(msg)


def _render_explore_ngos(user: dict):
    """Renders the directory of approved NGOs."""
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        search = st.text_input("🔍 Search NGOs by name, cause, or location...", placeholder="e.g. Food bank, Education, Chicago...")
    with col_s2:
        all_cities = list(set(NGO.objects.filter(status="Approved").values_list("city", flat=True)))
        city_filter = st.selectbox("Filter City", ["All"] + [c for c in all_cities if c])

    ngos = get_approved_ngos(search, city_filter)

    if not ngos:
        st.info("No approved NGOs found matching your search.")
        return

    st.markdown(f"**Found {len(ngos)} verified NGO(s)**")

    for ngo in ngos:
        render_ngo_card(ngo)
        
        # Show active requirements for this NGO
        reqs = list(ngo.requirements.filter(is_active=True))
        if reqs:
            with st.expander(f"📋 View Active Needs of {ngo.ngo_name} ({len(reqs)} requirements)"):
                for r in reqs:
                    rem = r.required_quantity - r.fulfilled_quantity
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: rgba(15, 23, 42, 0.6); border-radius: 8px; margin-bottom: 6px;">
                            <div>
                                <strong style="color: #f8fafc;">{r.item_name}</strong> ({r.category})
                            </div>
                            <div style="display: flex; gap: 12px; align-items: center;">
                                <span style="color: #cbd5e1; font-size: 0.85rem;">Needed: <strong>{rem}</strong> / {r.required_quantity}</span>
                                {get_status_badge(r.priority)}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


def _render_donor_leaderboard(user: dict):
    """Renders the Community Leaderboard and rankings."""
    st.markdown("### 🏆 Community Donor Leaderboard")
    st.markdown("<p style='color: #94a3b8;'>Recognizing top community contributors making an impact.</p>", unsafe_allow_html=True)

    leaderboard = get_donor_leaderboard(user.get("id"))
    if not leaderboard:
        st.info("No donor activity recorded yet.")
        return

    for entry in leaderboard:
        is_curr = entry["is_current_user"]
        curr_class = "current-user" if is_curr else ""
        you_badge = " (You)" if is_curr else ""

        st.markdown(
            f"""
            <div class="leaderboard-row {curr_class}">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="font-size: 1.4rem; font-weight: 800; color: {entry['badge_color']}; width: 36px;">
                        #{entry['rank']}
                    </div>
                    <div>
                        <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem;">
                            {entry['name']}{you_badge} <span style="font-size: 1rem;">{entry['icon']}</span>
                        </div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">
                            📍 {entry['city'] or 'Community'}, {entry['state'] or ''} • <span style="color: {entry['badge_color']}; font-weight: 600;">{entry['tier']}</span>
                        </div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.2rem; font-weight: 800; color: #38bdf8;">{entry['points']} pts</div>
                    <div style="font-size: 0.78rem; color: #cbd5e1;">{entry['total_donations']} donations ({entry['total_items']} items)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_donor_notifications(user: dict):
    """Renders the Donor notifications feed."""
    from src.components.notifications_drawer import render_notifications_view
    render_notifications_view(user)


def _render_donor_profile_settings(user: dict):
    """Renders Donor Profile and Theme Settings."""
    st.markdown("### 👤 Donor Profile & Preferences")

    with st.form("donor_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=user.get("name", ""))
            phone = st.text_input("Phone Number", value=user.get("phone", ""))
            city = st.text_input("City", value=user.get("city", ""))
            state = st.text_input("State", value=user.get("state", ""))
        with col2:
            pincode = st.text_input("Pincode / Postal Code", value=user.get("pincode", ""))
            language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Hindi", "Other"], index=0)
            st.text_input("Registered Email (Cannot be modified)", value=user.get("email", ""), disabled=True)

        address = st.text_area("Default Pickup Address", value=user.get("address", ""))
        pic = st.file_uploader("Update Profile Photo", type=["jpg", "jpeg", "png", "webp"])

        if st.form_submit_button("Update Profile", type="primary"):
            pic_path = save_uploaded_file(pic, str(DONOR_PICS_DIR)) if pic else None
            success, msg = update_donor_profile(user["id"], {
                "name": name,
                "phone": phone,
                "city": city,
                "state": state,
                "pincode": pincode,
                "language_preference": language,
                "address": address,
                "picture": pic_path,
            })
            if success:
                st.success("Profile updated successfully!")
                user["name"] = name
                user["phone"] = phone
                user["city"] = city
                user["state"] = state
                user["pincode"] = pincode
                user["address"] = address
                st.session_state.user = user
                st.rerun()
            else:
                st.error(msg)
