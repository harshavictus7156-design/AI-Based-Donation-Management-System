"""
NGO Workspace views:
- NGO Dashboard & Analytics
- Requirements Management (Add, Edit, Delete, Fulfillment Tracking)
- Incoming Allocations Review (Accept, Reject with Reason)
- Pickups Coordination & Status Updates
- NGO Profile & Verification Status
- Notifications & Leaderboard
"""

import streamlit as st
from src.models import (
    NGO,
    NGORequirement,
    DonationAllocation,
    PickupRequest,
)
from src.services.ngo_service import (
    get_ngo_dashboard_stats,
    add_requirement,
    update_requirement,
    delete_requirement,
    accept_allocation,
    reject_allocation,
    update_pickup_status,
    update_ngo_profile,
)
from src.services.donor_service import get_donor_leaderboard
from src.components.cards import render_kpi_card
from src.components.charts import render_category_pie_chart, render_status_bar_chart
from src.utils import get_status_badge, format_date, format_datetime, save_uploaded_file
from src.config import NGO_PICS_DIR, NGO_CERTS_DIR


def render_ngo_workspace(user: dict):
    """Main NGO Organization Workspace with sidebar navigation."""
    tabs = [
        "📊 NGO Dashboard",
        "📋 Manage Requirements",
        "📥 Incoming Allocations",
        "🚚 Pickups Coordination",
        "🏢 Organization Profile",
        "🏆 Community Ranking",
        "🔔 Notifications",
    ]

    selected_tab = st.sidebar.radio("NGO Navigation", tabs, index=0)

    # Verification warning banner if NGO is pending
    ngo = NGO.objects.filter(id=user["id"]).first()
    if ngo and ngo.status == "Pending":
        st.warning("⚠️ **Account Verification Pending**: Your NGO profile is under review by the administrator. Once approved, you can publish active requirements and receive donations.")
    elif ngo and ngo.status == "Rejected":
        st.error("❌ **Account Application Rejected**: Your organization profile was not approved. Please contact platform administrators.")

    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h2 style="color: #f8fafc; margin: 0;">{selected_tab}</h2>
            <div style="color: #10b981; font-size: 0.9rem; font-weight: 600;">
                🏢 {user.get('name')} {get_status_badge(ngo.status if ngo else 'Pending')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "Dashboard" in selected_tab:
        _render_ngo_dashboard(user)
    elif "Manage Requirements" in selected_tab:
        _render_ngo_requirements(user)
    elif "Incoming Allocations" in selected_tab:
        _render_ngo_allocations(user)
    elif "Pickups Coordination" in selected_tab:
        _render_ngo_pickups(user)
    elif "Organization Profile" in selected_tab:
        _render_ngo_profile(user)
    elif "Community Ranking" in selected_tab:
        _render_ngo_leaderboard(user)
    elif "Notifications" in selected_tab:
        _render_ngo_notifications(user)


def _render_ngo_dashboard(user: dict):
    """Renders the NGO Dashboard with KPIs and Analytics."""
    stats = get_ngo_dashboard_stats(user["id"])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Incoming Donations", stats["pending_allocations"], "📥", "Pending your review", "#38bdf8")
    with col2:
        render_kpi_card("Active Needs", stats["active_requirements"], "📋", f"{stats['fulfilled_requirements']} fulfilled", "#f59e0b")
    with col3:
        render_kpi_card("Accepted Allocations", stats["accepted_allocations"] + stats["collected_allocations"], "✅", "Resources allocated", "#10b981")
    with col4:
        render_kpi_card("Pending Pickups", stats["pending_pickups"], "🚚", "Scheduled for collection", "#8b5cf6")

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        reqs = NGORequirement.objects.filter(ngo_id=user["id"])
        cat_counts = {}
        for r in reqs:
            cat_counts[r.category] = cat_counts.get(r.category, 0) + r.required_quantity
        render_category_pie_chart(cat_counts, "Required Items by Category")
    with col_c2:
        alloc_status = {
            "Pending": stats["pending_allocations"],
            "Accepted": stats["accepted_allocations"],
            "Collected": stats["collected_allocations"],
        }
        render_status_bar_chart(alloc_status, "Incoming Allocation Status")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick incoming items preview
    st.markdown("### 📥 Recent Incoming Allocations")
    recent_allocs = (
        DonationAllocation.objects.filter(ngo_id=user["id"])
        .select_related("donation__donor")
        .order_by("-allocated_at")[:5]
    )
    if recent_allocs:
        for a in recent_allocs:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #f8fafc; font-size: 1rem;">📦 {a.donation.item_name}</strong>
                            <span style="color: #38bdf8; margin-left: 8px;">({a.allocated_quantity} units)</span>
                            <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 2px;">
                                From Donor: <strong>{a.donation.donor.name}</strong> • Category: {a.donation.category}
                            </div>
                        </div>
                        <div>{get_status_badge(a.status)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No incoming allocations yet. Once donors allocate items matching your requirements, they will appear here.")


def _render_ngo_requirements(user: dict):
    """Renders the Requirements Management view."""
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown("### 📋 Published Resource Requirements")
    with col_t2:
        pass

    # Add New Requirement Form
    with st.expander("➕ Add New Resource Requirement", expanded=False):
        with st.form("add_requirement_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("Item Name / Description *", placeholder="e.g. Rice (50kg bags), Textbooks, Blankets")
                category = st.selectbox("Category *", ["Clothing", "Books", "Food", "Electronics", "Furniture", "Medical Supplies", "School Supplies", "Other"])
                req_qty = st.number_input("Quantity Needed *", min_value=1, value=10, step=1)
            with col2:
                priority = st.selectbox("Urgency / Priority *", ["High", "Medium", "Low", "Urgent"])
                desc = st.text_area("Detailed Notes / Purpose", placeholder="Describe how these resources will be distributed...")

            if st.form_submit_button("Publish Requirement →", type="primary", use_container_width=True):
                success, msg, _ = add_requirement(
                    ngo_id=user["id"],
                    item_name=item_name,
                    category=category,
                    required_quantity=req_qty,
                    priority=priority,
                    description=desc,
                )
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # List Existing Requirements
    reqs = list(NGORequirement.objects.filter(ngo_id=user["id"]).order_by("-created_at"))

    if not reqs:
        st.info("Your organization has no requirements published yet. Click '➕ Add New Resource Requirement' above to post your needs.")
        return

    for r in reqs:
        rem = r.remaining_quantity
        pct = min(1.0, r.fulfilled_quantity / r.required_quantity) if r.required_quantity > 0 else 0

        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0; color: #f8fafc; font-size: 1.15rem;">🎯 {r.item_name}</h4>
                            <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                                Category: <strong style="color: #e2e8f0;">{r.category}</strong> • 
                                Priority: {get_status_badge(r.priority)} • 
                                Status: <strong style="color: {'#10b981' if r.is_active else '#94a3b8'};">{'Active' if r.is_active else 'Closed'}</strong>
                            </div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.1rem; font-weight: 800; color: #38bdf8;">
                                {r.fulfilled_quantity} / {r.required_quantity} units
                            </div>
                            <div style="font-size: 0.78rem; color: #94a3b8;">
                                {rem} needed
                            </div>
                        </div>
                    </div>
                    <div style="margin: 10px 0;">
                        <div style="background: rgba(15, 23, 42, 0.8); border-radius: 9999px; height: 8px; width: 100%; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #7c3aed, #38bdf8); height: 100%; width: {int(pct*100)}%;"></div>
                        </div>
                    </div>
                    <div style="color: #cbd5e1; font-size: 0.88rem;">{r.description or 'No extra details.'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c_edit, c_del, _ = st.columns([1, 1, 3])
            with c_edit:
                with st.popover("✏️ Edit Requirement", use_container_width=True):
                    e_name = st.text_input("Item Name", value=r.item_name, key=f"req_name_{r.id}")
                    e_qty = st.number_input("Required Qty", min_value=1, value=r.required_quantity, key=f"req_qty_{r.id}")
                    e_prio = st.selectbox("Priority", ["High", "Medium", "Low", "Urgent"], index=["High", "Medium", "Low", "Urgent"].index(r.priority), key=f"req_prio_{r.id}")
                    e_act = st.checkbox("Active", value=r.is_active, key=f"req_act_{r.id}")
                    e_desc = st.text_area("Description", value=r.description, key=f"req_desc_{r.id}")
                    if st.button("Save Changes", key=f"req_save_{r.id}"):
                        success, msg = update_requirement(
                            req_id=r.id,
                            ngo_id=user["id"],
                            item_name=e_name,
                            category=r.category,
                            required_quantity=e_qty,
                            priority=e_prio,
                            description=e_desc,
                            is_active=e_act,
                        )
                        if success:
                            st.success("Updated successfully.")
                            st.rerun()
                        else:
                            st.error(msg)
            with c_del:
                if st.button("🗑️ Delete", key=f"req_del_{r.id}", use_container_width=True):
                    success, msg = delete_requirement(r.id, user["id"])
                    if success:
                        st.success("Requirement deleted.")
                        st.rerun()


def _render_ngo_allocations(user: dict):
    """Renders Incoming Donations / Allocations review."""
    st.markdown("### 📥 Incoming Donation Allocations")
    st.markdown("<p style='color: #94a3b8;'>Review resources allocated by donors. Accepting an allocation will update your requirement fulfillment and trigger pickup dispatch.</p>", unsafe_allow_html=True)

    allocs = list(
        DonationAllocation.objects.filter(ngo_id=user["id"])
        .select_related("donation__donor", "requirement")
        .order_by("-allocated_at")
    )

    if not allocs:
        st.info("No incoming allocations at this time.")
        return

    for a in allocs:
        don = a.donation
        req_text = f"Linked Requirement: #{a.requirement.id} - {a.requirement.item_name}" if a.requirement else "Direct Donation Allocation"

        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h3 style="margin: 0; color: #f8fafc; font-size: 1.15rem;">📦 {don.item_name}</h3>
                            <div style="color: #38bdf8; font-size: 0.88rem; font-weight: 700; margin-top: 4px;">
                                Allocated Quantity: {a.allocated_quantity} units (Condition: {don.condition})
                            </div>
                            <div style="color: #94a3b8; font-size: 0.82rem; margin-top: 4px;">
                                Donor: <strong style="color: #f8fafc;">{don.donor.name}</strong> • 📞 {don.donor.phone} • ✉️ {don.donor.email}
                            </div>
                        </div>
                        <div>{get_status_badge(a.status)}</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 12px; border-radius: 8px; margin: 10px 0; font-size: 0.82rem; color: #cbd5e1;">
                        <div>📍 <strong>Pickup Address:</strong> {don.location}</div>
                        <div>🏷️ <strong>Category:</strong> {don.category} | {req_text}</div>
                        <div>📅 <strong>Allocated On:</strong> {format_datetime(a.allocated_at)}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if a.status == "Pending":
                col_acc, col_rej, _ = st.columns([1, 1, 2])
                with col_acc:
                    if st.button("✅ Accept Donation", key=f"acc_{a.id}", type="primary", use_container_width=True):
                        success, msg = accept_allocation(a.id, user["id"])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with col_rej:
                    with st.popover("❌ Decline Donation", use_container_width=True):
                        reason = st.text_input("Reason for declining (Optional)", key=f"rej_rsn_{a.id}")
                        if st.button("Confirm Decline", key=f"conf_rej_{a.id}"):
                            success, msg = reject_allocation(a.id, user["id"], reason)
                            if success:
                                st.warning(msg)
                                st.rerun()
                            else:
                                st.error(msg)


def _render_ngo_pickups(user: dict):
    """Renders Pickups Management view for NGO."""
    st.markdown("### 🚚 Pickups Coordination & Delivery Tracker")
    st.markdown("<p style='color: #94a3b8;'>Manage the status of donation pickups from donor doorsteps to your facility.</p>", unsafe_allow_html=True)

    pickups = list(
        PickupRequest.objects.filter(allocation__ngo_id=user["id"])
        .select_related("allocation__donation__donor", "allocation__ngo")
        .order_by("-created_at")
    )

    if not pickups:
        st.info("No pickup requests currently scheduled.")
        return

    for p in pickups:
        a = p.allocation
        don = a.donation

        with st.container():
            st.markdown(
                f"""
                <div class="glass-card" style="margin-bottom: 14px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div>
                            <h4 style="margin: 0; color: #f8fafc;">🚚 Pickup #{p.id} — {don.item_name} ({a.allocated_quantity} units)</h4>
                            <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                                Donor: <strong style="color: #f8fafc;">{don.donor.name}</strong> • 📞 {don.donor.phone}
                            </div>
                        </div>
                        <div>{get_status_badge(p.status)}</div>
                    </div>
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 12px; border-radius: 8px; margin: 10px 0; font-size: 0.82rem; color: #cbd5e1;">
                        <div>📍 <strong>Pickup Address:</strong> {p.pickup_address}</div>
                        <div>📅 <strong>Scheduled Date/Time:</strong> {format_datetime(p.scheduled_time)}</div>
                        <div>📝 <strong>Donor Notes:</strong> {p.notes or 'None'}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Update status dropdown
            col_u1, col_u2, _ = st.columns([2, 1, 2])
            with col_u1:
                status_opts = ["Pending", "Confirmed", "Dispatched", "Delivered", "Cancelled"]
                curr_idx = status_opts.index(p.status) if p.status in status_opts else 0
                new_st = st.selectbox("Update Status", status_opts, index=curr_idx, key=f"pk_sel_{p.id}")
            with col_u2:
                if st.button("Update Status", key=f"pk_btn_{p.id}", use_container_width=True):
                    success, msg = update_pickup_status(p.id, user["id"], new_st)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)


def _render_ngo_profile(user: dict):
    """Renders NGO Organization Profile and Document Verification view."""
    st.markdown("### 🏢 Organization Profile & Credentials")

    ngo = NGO.objects.filter(id=user["id"]).first()
    if not ngo:
        st.error("NGO record not found.")
        return

    with st.form("ngo_profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            ngo_name = st.text_input("Organization Name", value=ngo.ngo_name)
            phone = st.text_input("Phone Number", value=ngo.phone_no)
            website = st.text_input("Website Link", value=ngo.website_link)
            city = st.text_input("City", value=ngo.city)
        with col2:
            st.text_input("Registration / 80G Number", value=ngo.registration_no, disabled=True)
            st.text_input("Official Email Address", value=ngo.email_id, disabled=True)
            state = st.text_input("State", value=ngo.state)
            pincode = st.text_input("Pincode", value=ngo.pincode)

        desc = st.text_area("Mission Statement / Description", value=ngo.description)
        address = st.text_area("Operating Address", value=ngo.address)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            logo = st.file_uploader("Update Organization Logo", type=["jpg", "jpeg", "png", "webp"])
        with col_f2:
            cert = st.file_uploader("Update Registration Certificate", type=["pdf", "jpg", "jpeg", "png"])

        if st.form_submit_button("Save Profile Changes", type="primary"):
            logo_path = save_uploaded_file(logo, str(NGO_PICS_DIR)) if logo else None
            cert_path = save_uploaded_file(cert, str(NGO_CERTS_DIR)) if cert else None

            success, msg = update_ngo_profile(ngo.id, {
                "ngo_name": ngo_name,
                "phone_no": phone,
                "website_link": website,
                "city": city,
                "state": state,
                "pincode": pincode,
                "description": desc,
                "address": address,
                "picture": logo_path,
                "certificate_files": cert_path,
            })
            if success:
                st.success("NGO profile updated successfully.")
                user["name"] = ngo_name
                st.session_state.user = user
                st.rerun()
            else:
                st.error(msg)


def _render_ngo_leaderboard(user: dict):
    """Renders Community Leaderboard in NGO workspace."""
    st.markdown("### 🏆 Community Leaderboard")
    st.markdown("<p style='color: #94a3b8;'>Recognizing top contributors helping NGOs fulfill community needs.</p>", unsafe_allow_html=True)
    leaderboard = get_donor_leaderboard()
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


def _render_ngo_notifications(user: dict):
    """Renders NGO notification center."""
    from src.components.notifications_drawer import render_notifications_view
    render_notifications_view(user)
