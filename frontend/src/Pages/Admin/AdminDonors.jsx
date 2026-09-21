import { useEffect, useState } from "react";
import api from "../../services/api";
import "./AdminDonors.css";

function AdminDonors() {

    const [donors, setDonors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [filter, setFilter] = useState("all");

    const fetchDonors = async () => {

        try {

            setLoading(true);
            setError("");

            let url = "/admin/donors/";

            if (filter !== "all") {
                url += `?status=${filter}`;
            }

            const response = await api.get(url);

            setDonors(
                response.data.donors || []
            );

        } catch (err) {

            console.error(
                "Admin donors error:",
                err
            );

            setError(
                err.response?.data?.message ||
                "Unable to load donors."
            );

        } finally {

            setLoading(false);

        }
    };


    useEffect(() => {

        fetchDonors();

    }, [filter]);


    return (

        <div className="admin-page-content">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="admin-page-header">

                <div>

                    <h1>
                        Donors
                    </h1>

                    <p>
                        Manage registered donors
                    </p>

                </div>

                <button
                    className="admin-refresh-btn"
                    onClick={fetchDonors}
                >
                    ↻ Refresh
                </button>

            </div>


            {/* =================================================
                FILTERS
            ================================================= */}

            <div className="donor-toolbar">

                <div className="donor-filter-buttons">

                    <button
                        className={
                            filter === "all"
                                ? "active"
                                : ""
                        }
                        onClick={() => setFilter("all")}
                    >
                        All Donors
                    </button>

                    <button
                        className={
                            filter === "active"
                                ? "active"
                                : ""
                        }
                        onClick={() => setFilter("active")}
                    >
                        Active
                    </button>

                    <button
                        className={
                            filter === "inactive"
                                ? "active"
                                : ""
                        }
                        onClick={() => setFilter("inactive")}
                    >
                        Inactive
                    </button>

                </div>

                <div className="donor-count">

                    {donors.length} Donor
                    {donors.length !== 1 ? "s" : ""}

                </div>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div className="admin-error-message">

                    ⚠️ {error}

                </div>

            )}


            {/* =================================================
                LOADING
            ================================================= */}

            {loading ? (

                <div className="admin-loading-card">

                    <div className="admin-loader"></div>

                    <p>
                        Loading donors...
                    </p>

                </div>

            ) : donors.length === 0 ? (

                /* =================================================
                   EMPTY
                ================================================= */

                <div className="admin-empty-card">

                    <div className="admin-empty-icon">
                        👥
                    </div>

                    <h2>
                        No Donors Found
                    </h2>

                    <p>
                        There are no donors matching
                        the selected filter.
                    </p>

                </div>

            ) : (

                /* =================================================
                   TABLE
                ================================================= */

                <div className="admin-donors-card">

                    <div className="donor-table-wrapper">

                        <table className="admin-donors-table">

                            <thead>

                                <tr>

                                    <th>
                                        Donor
                                    </th>

                                    <th>
                                        Contact
                                    </th>

                                    <th>
                                        Location
                                    </th>

                                    <th>
                                        Donations
                                    </th>

                                    <th>
                                        Status
                                    </th>

                                    <th>
                                        Registered
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {donors.map(
                                    (donor) => (

                                        <tr
                                            key={donor.id}
                                        >

                                            {/* DONOR */}

                                            <td>

                                                <div className="donor-info">

                                                    {donor.picture ? (

                                                        <img
                                                            src={
                                                                donor.picture
                                                            }
                                                            alt={
                                                                donor.name
                                                            }
                                                            className="donor-avatar"
                                                        />

                                                    ) : (

                                                        <div className="donor-avatar donor-avatar-placeholder">

                                                            {donor.name
                                                                ?.charAt(0)
                                                                ?.toUpperCase()}

                                                        </div>

                                                    )}

                                                    <div>

                                                        <strong>
                                                            {donor.name}
                                                        </strong>

                                                        <span>
                                                            ID #{donor.id}
                                                        </span>

                                                    </div>

                                                </div>

                                            </td>


                                            {/* CONTACT */}

                                            <td>

                                                <div className="donor-contact">

                                                    <strong>
                                                        {donor.email}
                                                    </strong>

                                                    <span>
                                                        {donor.phone}
                                                    </span>

                                                </div>

                                            </td>


                                            {/* LOCATION */}

                                            <td>

                                                <div className="donor-location">

                                                    <strong>
                                                        {donor.city}
                                                    </strong>

                                                    <span>
                                                        {donor.state}
                                                    </span>

                                                </div>

                                            </td>


                                            {/* DONATIONS */}

                                            <td>

                                                <span className="donation-count">

                                                    {donor.total_donations}

                                                </span>

                                            </td>


                                            {/* STATUS */}

                                            <td>

                                                <span
                                                    className={
                                                        donor.status_active
                                                            ? "donor-status active"
                                                            : "donor-status inactive"
                                                    }
                                                >

                                                    <span className="status-dot"></span>

                                                    {donor.status_active
                                                        ? "Active"
                                                        : "Inactive"}

                                                </span>

                                            </td>


                                            {/* DATE */}

                                            <td>

                                                <span className="registered-date">

                                                    {donor.registered_date
                                                        ? new Date(
                                                              donor.registered_date
                                                          ).toLocaleDateString()
                                                        : "-"}

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

        </div>

    );
}

export default AdminDonors;