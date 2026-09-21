import "./AdminPickups.css";
import AdminManagementPage from "./AdminManagementPage";

function AdminPickups() {
    return <AdminManagementPage type="pickups" title="Pickups" subtitle="Monitor donation pickup requests" />;

    return (
        <div className="admin-page-content">

            <div className="admin-page-header">
                <div>
                    <h1>Pickups</h1>
                    <p>Monitor donation pickup requests</p>
                </div>
            </div>

            <div className="admin-empty-card">

                <div className="admin-empty-icon">
                    🚚
                </div>

                <h2>Pickup Management</h2>

                <p>
                    Track pickup requests and their
                    current delivery status.
                </p>

            </div>

        </div>
    );
}

export default AdminPickups;
