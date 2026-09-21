import { useEffect, useState } from "react";
import api from "../../services/api";
import "./AdminDashboard.css";

function AdminDashboard() {

  // =====================================================
  // STATES
  // =====================================================

  const [stats, setStats] = useState(null);

  const [recentDonations, setRecentDonations] = useState([]);

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");


  // =====================================================
  // FETCH ADMIN DASHBOARD DATA
  // =====================================================

  useEffect(() => {

    const fetchDashboardData = async () => {

      try {

        setLoading(true);
        setError("");

        const { data } = await api.get("admin/dashboard-stats/");


        if (!data.success) {

          throw new Error(
            "Invalid dashboard response"
          );

        }


        setStats(data.stats);

        setRecentDonations(
          data.recent_donations || []
        );


      } catch (err) {

        console.error(
          "Admin dashboard error:",
          err
        );

        setError(
          "Unable to load dashboard data."
        );

      } finally {

        setLoading(false);

      }

    };


    fetchDashboardData();

  }, []);


  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {

    return (

      <div className="admin-loading">

        <div className="admin-loader"></div>

        <p>
          Loading Admin Dashboard...
        </p>

      </div>

    );

  }


  // =====================================================
  // ERROR
  // =====================================================

  if (error || !stats) {

    return (

      <div className="admin-error-page">

        <div className="admin-error-card">

          <div className="admin-error-icon">
            ⚠️
          </div>

          <h2>
            Unable to load dashboard
          </h2>

          <p>
            {error ||
              "No dashboard data available."}
          </p>

          <button
            onClick={() =>
              window.location.reload()
            }
          >
            Try Again
          </button>

        </div>

      </div>

    );

  }


  // =====================================================
  // STAT CARDS
  // =====================================================

  const statCards = [

    {
      title: "Total Donors",
      value: stats.total_donors,
      icon: "👥",
      description: "Registered donors",
    },

    {
      title: "Total NGOs",
      value: stats.total_ngos,
      icon: "🏢",
      description: "Registered NGOs",
    },

    {
      title: "Total Donations",
      value: stats.total_donations,
      icon: "🎁",
      description: "All donations",
    },

    {
      title: "Successful Matches",
      value: stats.matched_donations,
      icon: "🤝",
      description: "Donation allocations",
    },

  ];


  // =====================================================
  // RENDER
  // =====================================================

  return (

    <div className="admin-main">


      {/* =================================================
          HEADER
      ================================================= */}

      <header className="admin-header">

        <div>

          <h1>
            Dashboard
          </h1>

          <p>
            Welcome back, Administrator
          </p>

        </div>


        <div className="admin-profile">

          <div className="admin-avatar">
            A
          </div>


          <div className="admin-profile-info">

            <strong>
              Administrator
            </strong>

            <span>
              System Admin
            </span>

          </div>

        </div>

      </header>


      {/* =================================================
          STATISTICS
      ================================================= */}

      <section className="admin-stats">

        {statCards.map((card) => (

          <div
            className="admin-stat-card"
            key={card.title}
          >

            <div className="stat-icon">
              {card.icon}
            </div>


            <div className="stat-info">

              <span>
                {card.title}
              </span>

              <strong>
                {card.value}
              </strong>

              <small>
                {card.description}
              </small>

            </div>

          </div>

        ))}

      </section>


      {/* =================================================
          SECONDARY STATISTICS
      ================================================= */}

      <section className="admin-secondary-stats">


        <div className="mini-stat">

          <div className="mini-stat-icon">
            📋
          </div>

          <div>

            <small>
              Requirements
            </small>

            <strong>
              {stats.total_requirements}
            </strong>

          </div>

        </div>


        <div className="mini-stat">

          <div className="mini-stat-icon">
            🤝
          </div>

          <div>

            <small>
              Allocations
            </small>

            <strong>
              {stats.total_allocations}
            </strong>

          </div>

        </div>


        <div className="mini-stat">

          <div className="mini-stat-icon">
            🚚
          </div>

          <div>

            <small>
              Pickups
            </small>

            <strong>
              {stats.total_pickups}
            </strong>

          </div>

        </div>


        <div className="mini-stat">

          <div className="mini-stat-icon">
            ⏳
          </div>

          <div>

            <small>
              Pending Pickups
            </small>

            <strong>
              {stats.pending_pickups}
            </strong>

          </div>

        </div>


      </section>


      {/* =================================================
          MAIN CONTENT GRID
      ================================================= */}

      <section className="admin-content-grid">


        {/* =================================================
            RECENT DONATIONS
        ================================================= */}

        <div className="admin-panel">


          <div className="panel-header">

            <div>

              <h2>
                Recent Donations
              </h2>

              <p>
                Latest donations submitted by donors
              </p>

            </div>


            <button
              className="view-all-btn"
              onClick={() =>
                alert(
                  "Donation Management coming next."
                )
              }
            >
              View All
            </button>

          </div>


          <div className="table-wrapper">

            <table className="admin-table">

              <thead>

                <tr>

                  <th>
                    ID
                  </th>

                  <th>
                    Donor
                  </th>

                  <th>
                    Item
                  </th>

                  <th>
                    Category
                  </th>

                  <th>
                    Quantity
                  </th>

                  <th>
                    Status
                  </th>

                </tr>

              </thead>


              <tbody>

                {recentDonations.length === 0 ? (

                  <tr>

                    <td
                      colSpan="6"
                      className="empty-state"
                    >
                      No donations found.
                    </td>

                  </tr>

                ) : (

                  recentDonations.map(
                    (donation) => (

                      <tr
                        key={donation.id}
                      >

                        <td>
                          #{donation.id}
                        </td>

                        <td>
                          {donation.donor}
                        </td>

                        <td>
                          {donation.item_name}
                        </td>

                        <td>
                          {donation.category}
                        </td>

                        <td>
                          {donation.quantity}
                        </td>

                        <td>

                          <span
                            className={
                              `status-badge status-${String(
                                donation.status
                              )
                                .toLowerCase()
                                .replace(
                                  /\s+/g,
                                  "-"
                                )}`
                            }
                          >

                            {donation.status}

                          </span>

                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

        </div>


        {/* =================================================
            PENDING ACTIONS
        ================================================= */}

        <div className="admin-panel">


          <div className="panel-header">

            <div>

              <h2>
                Pending Actions
              </h2>

              <p>
                Items requiring attention
              </p>

            </div>

          </div>


          <div className="pending-list">


            <div className="pending-item">

              <div className="pending-icon">
                🏢
              </div>

              <div>

                <strong>
                  NGO Verification
                </strong>

                <span>
                  {stats.pending_ngos}
                  {" "}
                  NGOs pending
                </span>

              </div>

              <div className="pending-count">
                {stats.pending_ngos}
              </div>

            </div>


            <div className="pending-item">

              <div className="pending-icon">
                🎁
              </div>

              <div>

                <strong>
                  Donation Review
                </strong>

                <span>
                  {stats.pending_donations}
                  {" "}
                  donations pending
                </span>

              </div>

              <div className="pending-count">
                {stats.pending_donations}
              </div>

            </div>


            <div className="pending-item">

              <div className="pending-icon">
                🚚
              </div>

              <div>

                <strong>
                  Pickup Requests
                </strong>

                <span>
                  {stats.pending_pickups}
                  {" "}
                  pickups pending
                </span>

              </div>

              <div className="pending-count">
                {stats.pending_pickups}
              </div>

            </div>


            <div className="pending-item">

              <div className="pending-icon">
                📋
              </div>

              <div>

                <strong>
                  NGO Requirements
                </strong>

                <span>
                  {stats.pending_requirements}
                  {" "}
                  requirements active
                </span>

              </div>

              <div className="pending-count">
                {stats.pending_requirements}
              </div>

            </div>


          </div>

        </div>

      </section>


      {/* =================================================
          DONATION SUMMARY
      ================================================= */}

      <section className="admin-panel donation-summary">


        <div className="panel-header">

          <div>

            <h2>
              Donation Overview
            </h2>

            <p>
              Current donation status
            </p>

          </div>

        </div>


        <div className="status-cards">


          <div className="overview-card">

            <span>
              Pending
            </span>

            <strong>
              {stats.pending_donations}
            </strong>

          </div>


          <div className="overview-card">

            <span>
              Accepted
            </span>

            <strong>
              {stats.accepted_donations}
            </strong>

          </div>


          <div className="overview-card">

            <span>
              Collected
            </span>

            <strong>
              {stats.collected_donations}
            </strong>

          </div>


          <div className="overview-card">

            <span>
              Rejected
            </span>

            <strong>
              {stats.rejected_donations}
            </strong>

          </div>


        </div>

      </section>

    </div>

  );

}

export default AdminDashboard;
