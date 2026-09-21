import { useEffect, useState } from "react";
import api from "../../services/api";
import "./AdminNGOs.css";

function AdminNGOs() {

    const [ngos, setNgos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filter, setFilter] = useState("All");
    const [search, setSearch] = useState("");

    const [selectedNGO, setSelectedNGO] = useState(null);

    const [actionLoading, setActionLoading] = useState(null);


    // =====================================================
    // FETCH NGOS
    // =====================================================

    const fetchNGOs = async () => {

        try {

            setLoading(true);
            setError("");

            let url = "admin/ngos/";

            if (filter !== "All") {
                url += `?status=${encodeURIComponent(filter)}`;
            }

            const { data } = await api.get(url);

            if (data.success) {

                setNgos(data.ngos || []);

            } else {

                setError(
                    data.message ||
                    "Unable to load NGOs."
                );
            }

        } catch (err) {

            console.error(
                "NGO API ERROR:",
                err
            );

            setError(
                err.response?.status === 401
                    ? "Your admin session has expired. Please sign in again."
                    : err.response?.status === 403
                        ? "You do not have permission to manage NGOs."
                        : err.response?.data?.message || "Unable to load NGOs."
            );

        } finally {

            setLoading(false);

        }
    };


    // =====================================================
    // LOAD WHEN FILTER CHANGES
    // =====================================================

    useEffect(() => {

        fetchNGOs();

    }, [filter]);


    // =====================================================
    // APPROVE NGO
    // =====================================================

    const approveNGO = async (id) => {

        try {

            setActionLoading(id);

            await api.post(`admin/ngos/${id}/approve/`);

            alert(
                "NGO approved successfully."
            );

            setSelectedNGO(null);

            fetchNGOs();

        } catch (error) {

            console.error(error);

            alert(
                "Unable to approve NGO."
            );

        } finally {

            setActionLoading(null);

        }
    };


    // =====================================================
    // REJECT NGO
    // =====================================================

    const rejectNGO = async (id) => {

        const confirmed = window.confirm(
            "Are you sure you want to reject this NGO?"
        );

        if (!confirmed) {
            return;
        }

        try {

            setActionLoading(id);

            await api.post(`admin/ngos/${id}/reject/`);

            alert(
                "NGO rejected successfully."
            );

            setSelectedNGO(null);

            fetchNGOs();

        } catch (error) {

            console.error(error);

            alert(
                "Unable to reject NGO."
            );

        } finally {

            setActionLoading(null);

        }
    };


    // =====================================================
    // VIEW NGO DETAILS
    // =====================================================

    const viewNGO = async (id) => {

        try {

            const { data } = await api.get(`admin/ngos/${id}/`);

            setSelectedNGO(
                data.ngo
            );

        } catch (error) {

            console.error(error);

            alert(
                error.response?.data?.message ||
                "Unable to load NGO details."
            );
        }
    };


    // =====================================================
    // STATUS CLASS
    // =====================================================

    const getStatusClass = (status) => {

        if (status === "Approved") {
            return "status-approved";
        }

        if (status === "Rejected") {
            return "status-rejected";
        }

        return "status-pending";
    };


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="admin-ngos-page">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="admin-ngos-header">

                <div>

                    <h1>
                        NGO Management
                    </h1>

                    <p>
                        Manage NGO registrations and approvals
                    </p>

                </div>

                <button
                    className="refresh-btn"
                    onClick={fetchNGOs}
                >
                    ↻ Refresh
                </button>

            </div>


            {/* =================================================
                FILTERS
            ================================================= */}

            <div className="ngo-filters">

                <input
                    className="ngo-search"
                    type="search"
                    value={search}
                    onChange={(event) => setSearch(event.target.value)}
                    placeholder="Search NGOs"
                    aria-label="Search NGOs"
                />

                <button
                    className={
                        filter === "All"
                            ? "filter-btn active"
                            : "filter-btn"
                    }
                    onClick={() => setFilter("All")}
                >
                    All
                </button>

                <button
                    className={
                        filter === "Pending"
                            ? "filter-btn active"
                            : "filter-btn"
                    }
                    onClick={() => setFilter("Pending")}
                >
                    Pending
                </button>

                <button
                    className={
                        filter === "Approved"
                            ? "filter-btn active"
                            : "filter-btn"
                    }
                    onClick={() => setFilter("Approved")}
                >
                    Approved
                </button>

                <button
                    className={
                        filter === "Rejected"
                            ? "filter-btn active"
                            : "filter-btn"
                    }
                    onClick={() => setFilter("Rejected")}
                >
                    Rejected
                </button>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div className="ngo-error">

                    {error}

                </div>

            )}


            {/* =================================================
                LOADING
            ================================================= */}

            {loading ? (

                <div className="ngo-loading">

                    Loading NGOs...

                </div>

            ) : ngos.filter((ngo) => {
                const query = search.trim().toLowerCase();
                return !query || [
                    ngo.ngo_name,
                    ngo.email_id,
                    ngo.phone_no,
                    ngo.city,
                    ngo.state,
                    ngo.registration_no,
                ].some((value) => String(value || "").toLowerCase().includes(query));
            }).length === 0 ? (

                <div className="ngo-empty">

                    <div className="empty-icon">
                        🏢
                    </div>

                    <h3>
                        No NGOs Found
                    </h3>

                    <p>
                        {search.trim()
                            ? "No NGOs match your search."
                            : "There are no NGOs in this category."}
                    </p>

                </div>

            ) : (

                /* =================================================
                   NGO TABLE
                ================================================= */

                <div className="ngo-table-container">

                    <table className="ngo-table">

                        <thead>

                            <tr>

                                <th>
                                    NGO
                                </th>

                                <th>
                                    Registration No.
                                </th>

                                <th>
                                    Location
                                </th>

                                <th>
                                    Contact
                                </th>

                                <th>
                                    Status
                                </th>

                                <th>
                                    Actions
                                </th>

                            </tr>

                        </thead>

                        <tbody>

                            {ngos.filter((ngo) => {
                                const query = search.trim().toLowerCase();
                                return !query || [
                                    ngo.ngo_name,
                                    ngo.email_id,
                                    ngo.phone_no,
                                    ngo.city,
                                    ngo.state,
                                    ngo.registration_no,
                                ].some((value) => String(value || "").toLowerCase().includes(query));
                            }).map((ngo) => (

                                <tr
                                    key={ngo.id}
                                >

                                    {/* NGO */}

                                    <td>

                                        <div className="ngo-info">

                                            {ngo.picture ? (

                                                <img
                                                    src={ngo.picture}
                                                    alt={ngo.ngo_name}
                                                    className="ngo-avatar"
                                                />

                                            ) : (

                                                <div className="ngo-avatar-placeholder">
                                                    🏢
                                                </div>

                                            )}

                                            <div>

                                                <strong>
                                                    {ngo.ngo_name}
                                                </strong>

                                                <span>
                                                    {ngo.email_id}
                                                </span>

                                            </div>

                                        </div>

                                    </td>


                                    {/* REGISTRATION */}

                                    <td>

                                        {ngo.registration_no || "N/A"}

                                    </td>


                                    {/* LOCATION */}

                                    <td>

                                        <div className="location-info">

                                            <span>
                                                {ngo.city || "N/A"}
                                            </span>

                                            <small>
                                                {ngo.state || ""}
                                            </small>

                                        </div>

                                    </td>


                                    {/* CONTACT */}

                                    <td>

                                        {ngo.phone_no || "N/A"}

                                    </td>


                                    {/* STATUS */}

                                    <td>

                                        <span
                                            className={
                                                `ngo-status ${getStatusClass(
                                                    ngo.status
                                                )}`
                                            }
                                        >

                                            {ngo.status}

                                        </span>

                                    </td>


                                    {/* ACTIONS */}

                                    <td>

                                        <div className="ngo-actions">

                                            <button
                                                className="view-btn"
                                                onClick={() =>
                                                    viewNGO(ngo.id)
                                                }
                                            >
                                                View
                                            </button>


                                            {ngo.status === "Pending" && (

                                                <>

                                                    <button
                                                        className="approve-btn"
                                                        disabled={
                                                            actionLoading === ngo.id
                                                        }
                                                        onClick={() =>
                                                            approveNGO(
                                                                ngo.id
                                                            )
                                                        }
                                                    >
                                                        {actionLoading === ngo.id
                                                            ? "..."
                                                            : "Approve"}
                                                    </button>


                                                    <button
                                                        className="reject-btn"
                                                        disabled={
                                                            actionLoading === ngo.id
                                                        }
                                                        onClick={() =>
                                                            rejectNGO(
                                                                ngo.id
                                                            )
                                                        }
                                                    >
                                                        Reject
                                                    </button>

                                                </>

                                            )}

                                        </div>

                                    </td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            )}


            {/* =================================================
                NGO DETAILS MODAL
            ================================================= */}

            {selectedNGO && (

                <div
                    className="ngo-modal-overlay"
                    onClick={() =>
                        setSelectedNGO(null)
                    }
                >

                    <div
                        className="ngo-modal"
                        onClick={(e) =>
                            e.stopPropagation()
                        }
                    >

                        <div className="modal-header">

                            <div>

                                <h2>
                                    {selectedNGO.ngo_name}
                                </h2>

                                <span
                                    className={
                                        `ngo-status ${getStatusClass(
                                            selectedNGO.status
                                        )}`
                                    }
                                >
                                    {selectedNGO.status}
                                </span>

                            </div>

                            <button
                                className="close-btn"
                                onClick={() =>
                                    setSelectedNGO(null)
                                }
                            >
                                ×
                            </button>

                        </div>


                        <div className="modal-body">

                            <div className="detail-section">

                                <h3>
                                    NGO Information
                                </h3>

                                <div className="detail-grid">

                                    <div>
                                        <label>
                                            Registration Number
                                        </label>

                                        <p>
                                            {selectedNGO.registration_no || "N/A"}
                                        </p>
                                    </div>

                                    <div>
                                        <label>
                                            Email
                                        </label>

                                        <p>
                                            {selectedNGO.email_id || "N/A"}
                                        </p>
                                    </div>

                                    <div>
                                        <label>
                                            Phone
                                        </label>

                                        <p>
                                            {selectedNGO.phone_no || "N/A"}
                                        </p>
                                    </div>

                                    <div>
                                        <label>
                                            Website
                                        </label>

                                        <p>
                                            {selectedNGO.website_link || "N/A"}
                                        </p>
                                    </div>

                                </div>

                            </div>


                            <div className="detail-section">

                                <h3>
                                    Address
                                </h3>

                                <p className="address-text">

                                    {selectedNGO.address || "N/A"}

                                    <br />

                                    {selectedNGO.city || ""}

                                    {selectedNGO.state
                                        ? `, ${selectedNGO.state}`
                                        : ""}

                                    {selectedNGO.pincode
                                        ? ` - ${selectedNGO.pincode}`
                                        : ""}

                                </p>

                            </div>


                            <div className="detail-section">

                                <h3>
                                    Description
                                </h3>

                                <p className="description-text">

                                    {selectedNGO.description ||
                                        "No description provided."}

                                </p>

                            </div>


                            {selectedNGO.certificate && (

                                <div className="detail-section">

                                    <h3>
                                        Certificate
                                    </h3>

                                    <a
                                        href={
                                            selectedNGO.certificate
                                        }
                                        target="_blank"
                                        rel="noreferrer"
                                        className="certificate-btn"
                                    >
                                        View Certificate
                                    </a>

                                </div>

                            )}

                        </div>


                        {selectedNGO.status === "Pending" && (

                            <div className="modal-actions">

                                <button
                                    className="approve-btn large"
                                    onClick={() =>
                                        approveNGO(
                                            selectedNGO.id
                                        )
                                    }
                                >
                                    ✓ Approve NGO
                                </button>

                                <button
                                    className="reject-btn large"
                                    onClick={() =>
                                        rejectNGO(
                                            selectedNGO.id
                                        )
                                    }
                                >
                                    ✕ Reject NGO
                                </button>

                            </div>

                        )}

                    </div>

                </div>

            )}

        </div>
    );
}

export default AdminNGOs;