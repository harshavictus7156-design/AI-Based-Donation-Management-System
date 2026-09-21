import { useEffect, useState } from "react";
import api from "../../services/api";
import "./AdminManagementPage.css";

function AdminManagementPage({
    type,
    title,
    subtitle
}) {

    const [data, setData] = useState([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");

    const [search, setSearch] =
        useState("");

    const [primaryFilter, setPrimaryFilter] = useState("all");
    const [activityFilter, setActivityFilter] = useState("all");


    const loadData = async () => {

        try {

            setLoading(true);
            setError("");

            const response =
                await api.get(
                    `/admin/management-data/?type=${type}`
                );

            setData(
                response.data.data || []
            );

        } catch (err) {

            console.error(
                "Admin data error:",
                err
            );

            setError(
                "Unable to load data."
            );

        } finally {

            setLoading(false);

        }

    };


    useEffect(() => {

        loadData();

    }, [type]);


    const filteredData = data.filter((item) => {
        const matchesSearch = JSON.stringify(item)
            .toLowerCase()
            .includes(search.toLowerCase());

        const field = type === "requirements" ? "priority" : "status";
        const matchesPrimary = primaryFilter === "all" || String(item[field] || "").toLowerCase() === primaryFilter;
        const matchesActivity = activityFilter === "all" || (activityFilter === "active" ? item.is_active : !item.is_active);

        return matchesSearch && matchesPrimary && matchesActivity;
    });

    const formatDate = (value) => {
        if (!value) return "N/A";
        const date = new Date(value);
        return Number.isNaN(date.getTime()) ? "N/A" : date.toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
    };


    const renderCells = (item) => {

        if (type === "donors") {

            return (
                <>
                    <td>
                        <strong>
                            {item.name}
                        </strong>
                        <small>
                            #{item.id}
                        </small>
                    </td>

                    <td>
                        {item.email}
                    </td>

                    <td>
                        {item.phone}
                    </td>

                    <td>
                        {item.city}, {item.state}
                    </td>

                    <td>
                        {item.donations}
                    </td>

                    <td>
                        <span
                            className={
                                `admin-status ${
                                    item.status === "Active"
                                        ? "success"
                                        : "neutral"
                                }`
                            }
                        >
                            {item.status}
                        </span>
                    </td>
                </>
            );
        }


        if (type === "donations") {

            return (
                <>
                    <td>
                        #{item.id}
                    </td>

                    <td>
                        <strong>
                            {item.item_name}
                        </strong>
                    </td>

                    <td>
                        {item.category}
                    </td>

                    <td>
                        {item.quantity}
                    </td>

                    <td>
                        {item.donor}
                    </td>

                    <td>
                        {item.ngo}
                    </td>

                    <td>
                        <span
                            className="admin-status"
                        >
                            {item.status}
                        </span>
                    </td>
                </>
            );
        }


        if (type === "requirements") {

            return (
                <>
                    <td>
                        #{item.id}
                    </td>

                    <td>
                        {item.ngo}
                    </td>

                    <td>
                        <strong>
                            {item.item_name}
                        </strong>
                    </td>

                    <td>
                        {item.category}
                    </td>

                    <td>
                        {item.required_quantity}
                    </td>

                    <td>
                        {item.fulfilled_quantity}
                    </td>

                    <td>
                        {item.remaining_quantity}
                    </td>

                    <td>
                        <span
                            className={
                                `priority-${String(
                                    item.priority
                                ).toLowerCase()}`
                            }
                        >
                            {item.priority}
                        </span>
                    </td>

                    <td>
                        {item.is_active
                            ? "Active"
                            : "Closed"}
                    </td>

                    <td>{formatDate(item.created_at)}</td>
                </>
            );
        }


        if (type === "allocations") {

            return (
                <>
                    <td>
                        #{item.id}
                    </td>

                    <td>
                        {item.donation}
                    </td>

                    <td>
                        {item.donor}
                    </td>

                    <td>
                        {item.ngo}
                    </td>

                    <td>
                        {item.quantity}
                    </td>

                    <td>
                        {item.requirement}
                    </td>

                    <td>
                        <span className="admin-status">
                            {item.status}
                        </span>
                    </td>

                    <td>{formatDate(item.allocated_at)}</td>
                </>
            );
        }


        if (type === "pickups") {

            return (
                <>
                    <td>
                        #{item.id}
                    </td>

                    <td>
                        {item.item}
                    </td>

                    <td>
                        {item.donor}
                    </td>

                    <td>
                        {item.ngo}
                    </td>

                    <td>
                        {item.address}
                    </td>

                    <td>
                        {new Date(
                            item.scheduled_time
                        ).toLocaleString()}
                    </td>

                    <td>
                        <span className="admin-status">
                            {item.status}
                        </span>
                    </td>

                    <td>{item.notes || "N/A"}</td>

                    <td>{formatDate(item.created_at)}</td>
                </>
            );
        }

        return null;
    };


    const renderHeaders = () => {

        if (type === "donors") {

            return (
                <>
                    <th>Donor</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Location</th>
                    <th>Donations</th>
                    <th>Status</th>
                </>
            );
        }


        if (type === "donations") {

            return (
                <>
                    <th>ID</th>
                    <th>Item</th>
                    <th>Category</th>
                    <th>Quantity</th>
                    <th>Donor</th>
                    <th>NGO</th>
                    <th>Status</th>
                </>
            );
        }


        if (type === "requirements") {

            return (
                <>
                    <th>ID</th>
                    <th>NGO</th>
                    <th>Item</th>
                    <th>Category</th>
                    <th>Required</th>
                    <th>Fulfilled</th>
                    <th>Remaining</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Created</th>
                </>
            );
        }


        if (type === "allocations") {

            return (
                <>
                    <th>ID</th>
                    <th>Donation</th>
                    <th>Donor</th>
                    <th>NGO</th>
                    <th>Quantity</th>
                    <th>Requirement</th>
                    <th>Status</th>
                    <th>Allocated</th>
                </>
            );
        }


        if (type === "pickups") {

            return (
                <>
                    <th>ID</th>
                    <th>Item</th>
                    <th>Donor</th>
                    <th>NGO</th>
                    <th>Address</th>
                    <th>Scheduled</th>
                    <th>Status</th>
                    <th>Notes</th>
                    <th>Created</th>
                </>
            );
        }

    };


    return (

        <div className="admin-management-page">

            {/* HEADER */}

            <div className="admin-management-header">

                <div>

                    <h1>
                        {title}
                    </h1>

                    <p>
                        {subtitle}
                    </p>

                </div>


                <button
                    className="admin-management-refresh"
                    onClick={loadData}
                >
                    ↻ Refresh
                </button>

            </div>


            {/* TOOLBAR */}

            <div className="admin-management-toolbar">

                <div className="admin-search">

                    🔍

                    <input
                        type="text"
                        placeholder={
                            `Search ${title.toLowerCase()}...`
                        }
                        value={search}
                        onChange={(e) =>
                            setSearch(
                                e.target.value
                            )
                        }
                    />

                </div>

                {(type === "requirements" || type === "allocations" || type === "pickups") && (
                    <select value={primaryFilter} onChange={(event) => setPrimaryFilter(event.target.value)}>
                        <option value="all">All {type === "requirements" ? "priorities" : "statuses"}</option>
                        {(type === "requirements" ? ["low", "medium", "high", "urgent"] : ["pending", "accepted", "rejected", "collected", "confirmed", "dispatched", "delivered", "cancelled"]).map((value) => <option key={value} value={value}>{value}</option>)}
                    </select>
                )}

                {type === "requirements" && (
                    <select value={activityFilter} onChange={(event) => setActivityFilter(event.target.value)}>
                        <option value="all">All activity</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                )}


                <span>
                    {filteredData.length} records
                </span>

            </div>


            {/* ERROR */}

            {error && (

                <div className="admin-management-error">
                    ⚠️ {error}
                </div>

            )}


            {/* LOADING */}

            {loading ? (

                <div className="admin-management-loading">

                    <div className="admin-loader"></div>

                    <p>
                        Loading {title.toLowerCase()}...
                    </p>

                </div>

            ) : (

                <div className="admin-management-card">

                    <div className="admin-management-table-wrapper">

                        <table>

                            <thead>

                                <tr>

                                    {renderHeaders()}

                                </tr>

                            </thead>


                            <tbody>

                                {filteredData.length === 0 ? (

                                    <tr>

                                        <td
                                            colSpan="10"
                                            className="admin-no-data"
                                        >
                                            No records found.
                                        </td>

                                    </tr>

                                ) : (

                                    filteredData.map(
                                        (item) => (

                                            <tr
                                                key={item.id}
                                            >

                                                {renderCells(
                                                    item
                                                )}

                                            </tr>

                                        )
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

export default AdminManagementPage;
