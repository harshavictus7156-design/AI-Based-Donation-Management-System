import { useEffect, useState } from "react";
import { getDashboard } from "../../services/dashboardService";
import "./DashboardCards.css";

function DashboardCards() {

  const [dashboard, setDashboard] = useState({
    total_donors: 0,
    total_donations: 0,
    total_quantity: 0,
    pending_donations: 0,
    accepted_donations: 0,
    collected_donations: 0,
  });

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const data = await getDashboard();

      console.log("Dashboard Data:", data);

      setDashboard(data);

    } catch (error) {
      console.error(
        "Dashboard Error:",
        error
      );
    }
  };

  return (
    <div className="dashboard-cards">

      <div className="dashboard-card">
        <h3>👥 Total Donors</h3>
        <h2>
          {dashboard.total_donors}
        </h2>
      </div>

      <div className="dashboard-card">
        <h3>📦 Total Donations</h3>
        <h2>
          {dashboard.total_donations}
        </h2>
      </div>

      <div className="dashboard-card">
        <h3>🔢 Total Items</h3>
        <h2>
          {dashboard.total_quantity}
        </h2>
      </div>

      <div className="dashboard-card">
        <h3>⏳ Pending</h3>
        <h2>
          {dashboard.pending_donations}
        </h2>
      </div>

      <div className="dashboard-card">
        <h3>✅ Accepted</h3>
        <h2>
          {dashboard.accepted_donations}
        </h2>
      </div>

      <div className="dashboard-card">
        <h3>🚚 Collected</h3>
        <h2>
          {dashboard.collected_donations}
        </h2>
      </div>

    </div>
  );
}

export default DashboardCards;