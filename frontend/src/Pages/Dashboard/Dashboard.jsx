import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  const [dashboardData, setDashboardData] = useState({
    total_donors: 0,
    total_ngos: 0,
    total_donations: 0,
  });

  const [loading, setLoading] = useState(true);

  // =====================================================
  // THEME
  // =====================================================

  const [darkMode, setDarkMode] = useState(
    localStorage.getItem("theme") === "dark"
  );

  // =====================================================
  // USER DETAILS
  // =====================================================

  const userName =
    localStorage.getItem("user_name") || "User";

  const userType =
    localStorage.getItem("user_type") || "Donor";

  // =====================================================
  // APPLY THEME
  // =====================================================

  useEffect(() => {
    document.body.classList.toggle(
      "dark-theme",
      darkMode
    );

    localStorage.setItem(
      "theme",
      darkMode ? "dark" : "light"
    );
  }, [darkMode]);

  // =====================================================
  // FETCH DASHBOARD
  // =====================================================

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);

      const response = await api.get(
        "dashboard/"
      );

      console.log(
        "Dashboard Data:",
        response.data
      );

      setDashboardData({
        total_donors:
          response.data.total_donors || 0,

        total_ngos:
          response.data.total_ngos || 0,

        total_donations:
          response.data.total_donations || 0,

        total_amount:
          response.data.total_amount || 0,
      });

    } catch (error) {
      console.error(
        "========== DASHBOARD ERROR =========="
      );

      console.error(error);

      console.error(
        "Status:",
        error.response?.status
      );

      console.error(
        "Response:",
        error.response?.data
      );

      console.error(
        "====================================="
      );

    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="dashboard-page">

      {/* =================================================
          HERO
      ================================================= */}

      <section className="dashboard-main-hero">

        <div className="dashboard-main-hero-content">

          <span className="dashboard-main-eyebrow">
            {String(userType).toUpperCase()} DASHBOARD
          </span>

          <h1>
            Welcome back,{" "}
            <span>{userName}</span> 👋
          </h1>

          <p>
            Track donations, connect with NGOs,
            and see the impact being created
            through your platform.
          </p>

        </div>


        {/* =================================================
            HERO CONTROLS
        ================================================= */}

        <div className="dashboard-hero-controls">

          <button
            type="button"
            className="theme-toggle"
            onClick={() =>
              setDarkMode(!darkMode)
            }
            aria-label="Toggle dark mode"
            title={
              darkMode
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
          >
            {darkMode ? "☀️" : "🌙"}
          </button>


          <div className="dashboard-main-hero-icon">
            ✦
          </div>

        </div>

      </section>


      {/* =================================================
          STATISTICS
      ================================================= */}

      <section className="dashboard-main-stats">

        {/* DONORS */}

        <div className="dashboard-main-stat">

          <div className="main-stat-icon">
            👤
          </div>

          <div>

            <span>
              TOTAL DONORS
            </span>

            <strong>
              {loading
                ? "..."
                : dashboardData.total_donors}
            </strong>

            <small>
              Registered donors
            </small>

          </div>

        </div>


        {/* NGOS */}

        <div className="dashboard-main-stat">

          <div className="main-stat-icon">
            🏢
          </div>

          <div>

            <span>
              TOTAL NGOS
            </span>

            <strong>
              {loading
                ? "..."
                : dashboardData.total_ngos}
            </strong>

            <small>
              Partner organizations
            </small>

          </div>

        </div>


        {/* DONATIONS */}

        <div className="dashboard-main-stat">

          <div className="main-stat-icon coral-stat">
            📦
          </div>

          <div>

            <span>
              TOTAL DONATIONS
            </span>

            <strong>
              {loading
                ? "..."
                : dashboardData.total_donations}
            </strong>

            <small>
              Items donated
            </small>

          </div>

        </div>


        {/* TOTAL VALUE */}

        <div className="dashboard-main-stat">

          <div className="main-stat-icon gold-stat">
            ₹
          </div>

          <div>

            <span>
              TOTAL VALUE
            </span>

            <strong>
              {loading
                ? "..."
                : `₹${dashboardData.total_amount}`}
            </strong>

            <small>
              Donation value
            </small>

          </div>

        </div>

      </section>


      {/* =================================================
          QUICK ACTIONS
      ================================================= */}

      <section className="dashboard-main-section">

        <div className="dashboard-section-title">

          <span>
            QUICK ACTIONS
          </span>

          <h2>
            What would you like to do?
          </h2>

        </div>


        <div className="dashboard-main-actions">

          {/* DONATE */}

          <button
            type="button"
            className="dashboard-action-card"
            onClick={() =>
              navigate("/donate-item")
            }
          >

            <div className="dashboard-action-icon">
              📦
            </div>

            <h3>
              Donate an Item
            </h3>

            <p>
              Give useful items a second
              life by donating them.
            </p>

            <span>
              Start donating →
            </span>

          </button>


          {/* MY DONATIONS */}

          <button
            type="button"
            className="dashboard-action-card"
            onClick={() =>
              navigate("/my-donations")
            }
          >

            <div className="dashboard-action-icon">
              📋
            </div>

            <h3>
              My Donations
            </h3>

            <p>
              Track your donated items
              and their current status.
            </p>

            <span>
              View donations →
            </span>

          </button>


          {/* PROFILE */}

          <button
            type="button"
            className="dashboard-action-card"
            onClick={() =>
              navigate("/profile")
            }
          >

            <div className="dashboard-action-icon">
              👤
            </div>

            <h3>
              My Profile
            </h3>

            <p>
              View and manage your
              account information.
            </p>

            <span>
              View profile →
            </span>

          </button>

        </div>

      </section>


      {/* =================================================
          IMPACT
      ================================================= */}

      <section className="dashboard-impact-section">

        <div className="dashboard-impact-content">

          <span>
            PLATFORM IMPACT
          </span>

          <h2>
            Every contribution
            <br />
            creates an impact.
          </h2>

          <p>
            Donors and NGOs work together
            to make useful resources reach
            the people and organizations
            that need them.
          </p>

        </div>


        <div className="dashboard-impact-number">

          <strong>
            {loading
              ? "..."
              : dashboardData.total_donations}
          </strong>

          <span>
            Total contributions
          </span>

        </div>

      </section>

    </div>
  );
}

export default Dashboard;