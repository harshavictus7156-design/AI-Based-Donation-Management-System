import "./AdminAllocations.css";
import AdminManagementPage from "./AdminManagementPage";

function AdminAllocations() {
    return <AdminManagementPage type="allocations" title="Allocations" subtitle="Monitor donation allocations across NGOs" />;

    return (
        <div className="admin-page-content">

            <div className="admin-page-header">
                <div>
                    <h1>Allocations</h1>
                    <p>Monitor donation allocations</p>
                </div>
            </div>

            <div className="admin-empty-card">

                <div className="admin-empty-icon">
                    🤝
                </div>

                <h2>Donation Allocations</h2>

                <p>
                    Monitor how donations are allocated
                    between donors and NGOs.
                </p>

            </div>

        </div>
    );
}

export default AdminAllocations;
