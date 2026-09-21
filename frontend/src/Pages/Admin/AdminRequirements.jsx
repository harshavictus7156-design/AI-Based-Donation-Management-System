import "./AdminRequirements.css";
import AdminManagementPage from "./AdminManagementPage";

function AdminRequirements() {
    return <AdminManagementPage type="requirements" title="NGO Requirements" subtitle="Monitor requirements posted by NGOs" />;

    return (
        <div className="admin-page-content">

            <div className="admin-page-header">
                <div>
                    <h1>NGO Requirements</h1>
                    <p>Monitor requirements posted by NGOs</p>
                </div>
            </div>

            <div className="admin-empty-card">

                <div className="admin-empty-icon">
                    📋
                </div>

                <h2>Requirement Management</h2>

                <p>
                    Review donation requirements created
                    by registered NGOs.
                </p>

            </div>

        </div>
    );
}

export default AdminRequirements;
