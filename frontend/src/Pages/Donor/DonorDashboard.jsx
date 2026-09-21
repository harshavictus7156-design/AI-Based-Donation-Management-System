import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiActivity,
  FiArrowRight,
  FiBell,
  FiCheckCircle,
  FiClock,
  FiGift,
  FiHeart,
  FiPackage,
  FiPlus,
  FiTruck,
  FiUser,
} from "react-icons/fi";
import api from "../../services/api";
import DonorLeaderboard from "../../components/DonorLeaderboard/DonorLeaderboard";
import "./DonorDashboard.css";

export default function DonorDashboard() {
  const navigate = useNavigate();

  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);

  const name = localStorage.getItem("user_name") || "Donor";

  useEffect(() => {
    let active = true;

    api
      .get("my-donations/")
      .then(({ data }) => {
        if (!active) return;

        setDonations(
          Array.isArray(data) ? data : data?.results || []
        );
      })
      .catch(() => {
        if (active) {
          setDonations([]);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const count = (statuses) =>
    donations.filter((d) =>
      statuses.includes(
        String(d.status || "pending").toLowerCase()
      )
    ).length;

  const stats = useMemo(
    () => [
      {
        label: "Total Donations",
        value: donations.length,
        icon: FiPackage,
        tone: "violet",
      },
      {
        label: "Pending",
        value: count(["pending"]),
        icon: FiClock,
        tone: "gold",
      },
      {
        label: "Accepted",
        value: count(["accepted"]),
        icon: FiCheckCircle,
        tone: "violet",
      },
      {
        label: "Collected",
        value: count([
          "collected",
          "completed",
          "delivered",
        ]),
        icon: FiTruck,
        tone: "gold",
      },
    ],
    [donations]
  );

  const recent = donations.slice(0, 4);

  const completed = count([
    "collected",
    "completed",
    "delivered",
  ]);

  const accepted = count(["accepted"]);

  const progress = donations.length
    ? Math.round(
        ((accepted + completed) / donations.length) * 100
      )
    : 0;

  return (
    <div className="donor-dashboard-page donor-dashboard-modern">

      {/* HERO SECTION */}
      <section className="donor-dashboard-hero">

        <div className="donor-dashboard-hero-copy">

          <span className="dashboard-eyebrow">
            DONOR WORKSPACE
          </span>

          <h2>
            Welcome back, <strong>{name}</strong>{" "}
            <span aria-hidden="true">👋</span>
          </h2>

          <p>
            Track your donations, follow their progress,
            and keep making a meaningful difference.
          </p>

          {/* MAIN ACTION BUTTONS */}
          <div className="hero-actions">

            {/* EXPLORE NGOs */}
            <button
              className="donor-primary-cta"
              onClick={() => navigate("/explore-ngos")}
            >
              <FiHeart />
              Explore NGOs
              <FiArrowRight />
            </button>

            {/* DONATE ITEM */}
            <button
              className="donor-secondary-cta"
              onClick={() => navigate("/donate-item")}
            >
              <FiPlus />
              Donate an Item
              <FiArrowRight />
            </button>

            {/* MY DONATIONS */}
            <button
              className="donor-secondary-cta"
              onClick={() => navigate("/my-donations")}
            >
              View My Donations
            </button>

          </div>
        </div>

        {/* DONATION PROGRESS CARD */}
        <div className="hero-impact-card">

          <div className="impact-ring">
            <span>
              {loading ? "—" : progress + "%"}
            </span>
          </div>

          <div>
            <span>DONATION PROGRESS</span>

            <h3>
              {progress
                ? "Great momentum"
                : "Ready to begin"}
            </h3>

            <p>
              {progress
                ? "Your active donations are moving forward."
                : "Start your first donation and create impact."}
            </p>
          </div>

          <FiHeart className="impact-heart" />

        </div>

      </section>

      {/* DASHBOARD STATISTICS */}
      <section className="dashboard-stats donor-compact-stats">

        {stats.map(
          ({ label, value, icon: Icon, tone }) => (
            <div
              className="stat-card"
              key={label}
            >

              <div className={"stat-icon " + tone}>
                <Icon />
              </div>

              <div>

                <span>{label}</span>

                <strong>
                  {loading ? "—" : value}
                </strong>

                <small>
                  {label === "Total Donations"
                    ? "Items donated"
                    : "Current status"}
                </small>

              </div>

            </div>
          )
        )}

      </section>

      {/* MAIN DASHBOARD CONTENT */}
      <section className="dashboard-grid-main">

        {/* RECENT DONATIONS */}
        <div className="donor-status-card dashboard-panel">

          <div className="section-heading">

            <div>
              <span>RECENT DONATIONS</span>
              <h2>Latest activity</h2>
            </div>

            <button
              className="text-link"
              onClick={() =>
                navigate("/my-donations")
              }
            >
              View all <FiArrowRight />
            </button>

          </div>

          {loading ? (

            <p className="dashboard-muted">
              Loading your donations…
            </p>

          ) : recent.length === 0 ? (

            <div className="dashboard-empty">

              <FiGift />

              <p>No donations yet.</p>

              <button
                onClick={() =>
                  navigate("/donate-item")
                }
              >
                Make your first donation{" "}
                <FiArrowRight />
              </button>

            </div>

          ) : (

            <div className="recent-mini-list">

              {recent.map((d, i) => {

                const status = String(
                  d.status || "pending"
                ).toLowerCase();

                const title =
                  d.item_name ||
                  d.item ||
                  d.title ||
                  "Donation";

                return (

                  <div
                    className="recent-mini-row"
                    key={d.id || i}
                  >

                    <div className="recent-item-icon">
                      <FiPackage />
                    </div>

                    <div className="recent-item-copy">

                      <strong>{title}</strong>

                      <span>
                        {d.category ||
                          "Donation item"}
                      </span>

                    </div>

                    <span
                      className={"mini-status " + status}
                    >
                      {d.status || "Pending"}
                    </span>

                  </div>

                );
              })}

            </div>

          )}

        </div>

        {/* DONATION JOURNEY */}
        <div className="dashboard-panel ai-insight-panel">

          <div className="panel-icon">
            <FiActivity />
          </div>

          <span className="panel-kicker">
            DONATION JOURNEY
          </span>

          <h3>
            Every contribution counts.
          </h3>

          <p>
            Keep your donation journey moving.
            Accepted and collected items are
            reflected in your progress automatically.
          </p>

          <div className="journey-line">

            <div>
              <span>Accepted</span>
              <strong>{accepted}</strong>
            </div>

            <div>
              <span>Collected</span>
              <strong>{completed}</strong>
            </div>

          </div>

          <button
            onClick={() =>
              navigate("/my-activity")
            }
          >
            View Activity <FiArrowRight />
          </button>

        </div>

      </section>

      {/* DONOR LEADERBOARD */}
      <DonorLeaderboard showCurrentRank />

      {/* QUICK ACTIONS */}
      <section className="quick-actions-section">

        <div className="section-heading section-heading-wide">

          <div>
            <span>QUICK ACTIONS</span>

            <h2>
              What would you like to do?
            </h2>
          </div>

        </div>

        <div className="quick-actions-grid">

          {/* EXPLORE NGOs */}
          <button
            className="quick-action"
            onClick={() =>
              navigate("/explore-ngos")
            }
          >
            <FiHeart />

            <strong>
              Explore NGOs
            </strong>

            <span>
              Find an NGO to support
            </span>

          </button>

          {/* ADD DONATION */}
          <button
            className="quick-action"
            onClick={() =>
              navigate("/donate-item")
            }
          >
            <FiPlus />

            <strong>
              Add Donation
            </strong>

            <span>
              Create a new donation
            </span>

          </button>

          {/* MY DONATIONS */}
          <button
            className="quick-action"
            onClick={() =>
              navigate("/my-donations")
            }
          >
            <FiPackage />

            <strong>
              My Donations
            </strong>

            <span>
              Track your items
            </span>

          </button>

          {/* MY PROFILE */}
          <button
            className="quick-action"
            onClick={() =>
              navigate("/profile")
            }
          >
            <FiUser />

            <strong>
              My Profile
            </strong>

            <span>
              Manage your details
            </span>

          </button>

          {/* NOTIFICATIONS */}
          <button
            className="quick-action"
            onClick={() =>
              navigate("/notifications")
            }
          >
            <FiBell />

            <strong>
              Notifications
            </strong>

            <span>
              See recent updates
            </span>

          </button>

        </div>

      </section>

      {/* IMPACT BANNER */}
      <section className="donor-impact-banner">

        <div className="impact-banner-icon">
          <FiHeart />
        </div>

        <div>

          <strong>
            Together, we create lasting change
          </strong>

          <span>
            Your kindness today can build a better
            tomorrow for someone who needs it.
          </span>

        </div>

        <button
          onClick={() =>
            navigate("/donate-item")
          }
        >
          Donate Now <FiArrowRight />
        </button>

      </section>

    </div>
  );
}