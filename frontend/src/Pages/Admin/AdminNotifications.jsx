import "./AdminNotifications.css";

function AdminNotifications() {
    return (
        <div className="admin-page-content">

            <div className="admin-page-header">
                <div>
                    <h1>Notifications</h1>
                    <p>System notifications and alerts</p>
                </div>
            </div>

            <div className="admin-empty-card">

                <div className="admin-empty-icon">
                    🔔
                </div>

                <h2>Notifications</h2>

                <p>
                    Monitor important notifications and
                    system activities.
                </p>

            </div>

        </div>
    );
}

export default AdminNotifications;