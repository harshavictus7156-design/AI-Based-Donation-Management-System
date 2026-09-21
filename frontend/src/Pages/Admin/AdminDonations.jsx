import { useEffect, useMemo, useState } from "react";
import api from "../../services/api";
import "./AdminDonations.css";

function AdminDonations() {
    const [donations, setDonations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState("");

    const [filter, setFilter] = useState("all");
    const [search, setSearch] = useState("");

    const fetchDonations = async (isRefresh = false) => {
        try {
            if (isRefresh) {
                setRefreshing(true);
            } else {
                setLoading(true);
            }

            setError("");

            const response = await api.get(
                "/admin/management-data/?type=donations"
            );

            setDonations(
                response.data?.data || []
            );

        } catch (err) {
            console.error(
                "Admin donations error:",
                err
            );

            setError(
                err.response?.data?.message ||
                "Unable to load donations."
            );

        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchDonations();
    }, []);

    /* =====================================================
       FILTER + SEARCH
    ===================================================== */

    const filteredDonations = useMemo(() => {
        return donations.filter((donation) => {

            const status =
                String(donation.status || "")
                    .toLowerCase();

            const matchesFilter =
                filter === "all" ||
                status === filter.toLowerCase();

            const searchText =
                search.trim().toLowerCase();

            if (!searchText) {
                return matchesFilter;
            }

            const searchableText = [
                donation.item_name,
                donation.category,
                donation.condition,
                donation.status,
                donation.donor,
                donation.ngo,
                donation.location,
                donation.id
            ]
                .filter(Boolean)
                .join(" ")
                .toLowerCase();

            return (
                matchesFilter &&
                searchableText.includes(searchText)
            );
        });
    }, [donations, filter, search]);


    /* =====================================================
       COUNTS
    ===================================================== */

    const counts = useMemo(() => {
        return {
            all: donations.length,

            pending: donations.filter(
                (d) =>
                    String(d.status)
                        .toLowerCase() === "pending"
            ).length,

            accepted: donations.filter(
                (d) =>
                    String(d.status)
                        .toLowerCase() === "accepted"
            ).length,

            collected: donations.filter(
                (d) =>
                    String(d.status)
                        .toLowerCase() === "collected"
            ).length,

            rejected: donations.filter(
                (d) =>
                    String(d.status)
                        .toLowerCase() === "rejected"
            ).length
        };
    }, [donations]);


    /* =====================================================
       DATE FORMAT
    ===================================================== */

    const formatDate = (date) => {
        if (!date) return "-";

        const parsed = new Date(date);

        if (Number.isNaN(parsed.getTime())) {
            return "-";
        }

        return parsed.toLocaleDateString(
            "en-IN",
            {
                day: "2-digit",
                month: "short",
                year: "numeric"
            }
        );
    };


    /* =====================================================
       STATUS CLASS
    ===================================================== */

    const getStatusClass = (status) => {
        switch (
            String(status || "")
                .toLowerCase()
        ) {
            case "accepted":
                return "accepted";

            case "collected":
                return "collected";

            case "rejected":
                return "rejected";

            case "pending":
            default:
                return "pending";
        }
    };


    return (
        <div className="admin-page-content">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="admin-page-header">

                <div>
                    <h1>
                        Donations
                    </h1>

                    <p>
                        Monitor and manage donations
                    </p>
                </div>

                <button
                    className="admin-refresh-btn"
                    onClick={() =>
                        fetchDonations(true)
                    }
                    disabled={refreshing}
                >
                    <span
                        className={
                            refreshing
                                ? "refresh-icon spinning"
                                : "refresh-icon"
                        }
                    >
                        ↻
                    </span>

                    {refreshing
                        ? "Refreshing..."
                        : "Refresh"}
                </button>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (
                <div className="admin-error-message">
                    <span>⚠</span>
                    {error}
                </div>
            )}


            {/* =================================================
                LOADING
            ================================================= */}

            {loading ? (

                <div className="admin-loading-card">

                    <div className="admin-loader"></div>

                    <p>
                        Loading donations...
                    </p>

                </div>

            ) : (

                <>

                    {/* =================================================
                        STAT CARDS
                    ================================================= */}

                    <div className="donation-summary">

                        <div className="donation-stat-card">

                            <div className="donation-stat-icon blue">
                                🎁
                            </div>

                            <div>
                                <span>
                                    Total Donations
                                </span>

                                <strong>
                                    {counts.all}
                                </strong>
                            </div>

                        </div>


                        <div className="donation-stat-card">

                            <div className="donation-stat-icon yellow">
                                ⏳
                            </div>

                            <div>
                                <span>
                                    Pending
                                </span>

                                <strong>
                                    {counts.pending}
                                </strong>
                            </div>

                        </div>


                        <div className="donation-stat-card">

                            <div className="donation-stat-icon green">
                                ✓
                            </div>

                            <div>
                                <span>
                                    Accepted
                                </span>

                                <strong>
                                    {counts.accepted}
                                </strong>
                            </div>

                        </div>


                        <div className="donation-stat-card">

                            <div className="donation-stat-icon navy">
                                📦
                            </div>

                            <div>
                                <span>
                                    Collected
                                </span>

                                <strong>
                                    {counts.collected}
                                </strong>
                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        TOOLBAR
                    ================================================= */}

                    <div className="donation-toolbar">

                        <div className="donation-filters">

                            <button
                                className={
                                    filter === "all"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    setFilter("all")
                                }
                            >
                                All
                                <span>
                                    {counts.all}
                                </span>
                            </button>

                            <button
                                className={
                                    filter === "pending"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    setFilter("pending")
                                }
                            >
                                Pending
                                <span>
                                    {counts.pending}
                                </span>
                            </button>

                            <button
                                className={
                                    filter === "accepted"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    setFilter("accepted")
                                }
                            >
                                Accepted
                                <span>
                                    {counts.accepted}
                                </span>
                            </button>

                            <button
                                className={
                                    filter === "collected"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    setFilter("collected")
                                }
                            >
                                Collected
                                <span>
                                    {counts.collected}
                                </span>
                            </button>

                            <button
                                className={
                                    filter === "rejected"
                                        ? "active"
                                        : ""
                                }
                                onClick={() =>
                                    setFilter("rejected")
                                }
                            >
                                Rejected
                                <span>
                                    {counts.rejected}
                                </span>
                            </button>

                        </div>


                        {/* SEARCH */}

                        <div className="donation-search">

                            <span>
                                🔍
                            </span>

                            <input
                                type="text"
                                placeholder="Search donations..."
                                value={search}
                                onChange={(e) =>
                                    setSearch(
                                        e.target.value
                                    )
                                }
                            />

                            {search && (
                                <button
                                    className="clear-search"
                                    onClick={() =>
                                        setSearch("")
                                    }
                                >
                                    ×
                                </button>
                            )}

                        </div>

                    </div>


                    {/* =================================================
                        RESULT COUNT
                    ================================================= */}

                    <div className="donation-result-info">

                        <span>
                            Showing{" "}
                            <strong>
                                {filteredDonations.length}
                            </strong>{" "}
                            of{" "}
                            <strong>
                                {donations.length}
                            </strong>{" "}
                            donations
                        </span>

                    </div>


                    {/* =================================================
                        EMPTY
                    ================================================= */}

                    {filteredDonations.length === 0 ? (

                        <div className="admin-empty-card">

                            <div className="admin-empty-icon">
                                🎁
                            </div>

                            <h2>
                                No Donations Found
                            </h2>

                            <p>
                                {donations.length === 0
                                    ? "There are no donations available yet."
                                    : "No donations match your current search or filter."}
                            </p>

                            {(search ||
                                filter !== "all") && (
                                <button
                                    className="donation-reset-btn"
                                    onClick={() => {
                                        setSearch("");
                                        setFilter("all");
                                    }}
                                >
                                    Clear Filters
                                </button>
                            )}

                        </div>

                    ) : (

                        /* =================================================
                           TABLE
                        ================================================= */

                        <div className="admin-donations-card">

                            <div className="donation-table-wrapper">

                                <table className="admin-donations-table">

                                    <thead>

                                        <tr>

                                            <th>
                                                Donation
                                            </th>

                                            <th>
                                                Donor
                                            </th>

                                            <th>
                                                Category
                                            </th>

                                            <th>
                                                Quantity
                                            </th>

                                            <th>
                                                NGO
                                            </th>

                                            <th>
                                                Status
                                            </th>

                                            <th>
                                                Date
                                            </th>

                                        </tr>

                                    </thead>


                                    <tbody>

                                        {filteredDonations.map(
                                            (donation) => (

                                                <tr
                                                    key={
                                                        donation.id
                                                    }
                                                >

                                                    {/* DONATION */}

                                                    <td>

                                                        <div className="donation-info">

                                                            <div className="donation-item-icon">
                                                                🎁
                                                            </div>

                                                            <div>

                                                                <strong>
                                                                    {donation.item_name ||
                                                                        "Unnamed Item"}
                                                                </strong>

                                                                <span>
                                                                    ID #
                                                                    {donation.id}
                                                                </span>

                                                            </div>

                                                        </div>

                                                    </td>


                                                    {/* DONOR */}

                                                    <td>

                                                        <div className="donor-cell">

                                                            <strong>
                                                                {donation.donor ||
                                                                    "Unknown"}
                                                            </strong>

                                                            <span>
                                                                {donation.donor_email ||
                                                                    "Donor"}
                                                            </span>

                                                        </div>

                                                    </td>


                                                    {/* CATEGORY */}

                                                    <td>

                                                        <span className="category-badge">
                                                            {donation.category ||
                                                                "Other"}
                                                        </span>

                                                    </td>


                                                    {/* QUANTITY */}

                                                    <td>

                                                        <span className="quantity-badge">
                                                            {donation.quantity ??
                                                                0}
                                                        </span>

                                                    </td>


                                                    {/* NGO */}

                                                    <td>

                                                        <div className="ngo-cell">

                                                            <strong>
                                                                {donation.ngo ||
                                                                    "Not allocated"}
                                                            </strong>

                                                        </div>

                                                    </td>


                                                    {/* STATUS */}

                                                    <td>

                                                        <span
                                                            className={`donation-status ${getStatusClass(
                                                                donation.status
                                                            )}`}
                                                        >

                                                            <span className="status-dot"></span>

                                                            {donation.status ||
                                                                "Pending"}

                                                        </span>

                                                    </td>


                                                    {/* DATE */}

                                                    <td>

                                                        <span className="donation-date">
                                                            {formatDate(
                                                                donation.donation_date
                                                            )}
                                                        </span>

                                                    </td>

                                                </tr>

                                            )
                                        )}

                                    </tbody>

                                </table>

                            </div>

                        </div>

                    )}

                </>
            )}

        </div>
    );
}

export default AdminDonations;