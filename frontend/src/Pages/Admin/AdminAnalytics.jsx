import "./AdminAnalytics.css";

function AdminAnalytics() {
    return (
        <div className="admin-page-content">

            <div className="admin-page-header">
                <div>
                    <h1>Analytics</h1>
                    <p>Donation system performance</p>
                </div>
            </div>

            <div className="analytics-grid">

                <div className="analytics-card">
                    <span>Donation Impact</span>
                    <strong>Active</strong>
                </div>

                <div className="analytics-card">
                    <span>NGO Participation</span>
                    <strong>Active</strong>
                </div>

                <div className="analytics-card">
                    <span>Donor Participation</span>
                    <strong>Active</strong>
                </div>

                <div className="analytics-card">
                    <span>System Matching</span>
                    <strong>AI Powered</strong>
                </div>

            </div>

        </div>
    );
}

export default AdminAnalytics;