import "./AdminSettings.css";

function AdminSettings() {
    return (
        <div className="admin-page-content">

            <div className="admin-page-header">
                <div>
                    <h1>Settings</h1>
                    <p>Administrator settings</p>
                </div>
            </div>

            <div className="settings-card">

                <div className="settings-row">
                    <div>
                        <strong>Account</strong>
                        <span>Administrator</span>
                    </div>
                </div>

                <div className="settings-row">
                    <div>
                        <strong>Role</strong>
                        <span>System Administrator</span>
                    </div>
                </div>

                <div className="settings-row">
                    <div>
                        <strong>Platform</strong>
                        <span>AI Based Donation System</span>
                    </div>
                </div>

            </div>

        </div>
    );
}

export default AdminSettings;