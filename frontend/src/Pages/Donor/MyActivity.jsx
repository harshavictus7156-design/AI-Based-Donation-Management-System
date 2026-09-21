import { useEffect, useMemo, useState } from "react";
import { FiActivity, FiCheckCircle, FiClock, FiPackage, FiTruck } from "react-icons/fi";
import api from "../../services/api";
import "./MyActivity.css";

function MyActivity() {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await api.get("my-donations/");
        setDonations(Array.isArray(response.data) ? response.data : []);
      } catch (error) {
        console.error("Activity fetch error:", error);
        setDonations([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const stats = useMemo(() => {
    const normalized = donations.map((d) => String(d.status || "pending").toLowerCase());
    return {
      created: donations.length,
      accepted: normalized.filter((s) => ["accepted", "collected", "completed", "delivered"].includes(s)).length,
      collected: normalized.filter((s) => ["collected", "completed", "delivered"].includes(s)).length,
      pending: normalized.filter((s) => s === "pending").length,
    };
  }, [donations]);

  const activities = useMemo(() => {
    return donations.slice(0, 8).map((donation) => {
      const status = String(donation.status || "pending").toLowerCase();
      let icon = FiPackage;
      let title = "Donation created";
      let tone = "created";
      let description = `${donation.item_name || "Your donation"} was added to your donation list.`;

      if (["accepted", "collected", "completed", "delivered"].includes(status)) {
        icon = FiCheckCircle;
        title = "Donation accepted";
        tone = "accepted";
        description = `${donation.item_name || "Your donation"} was accepted by the selected NGO.`;
      }
      if (["collected", "completed", "delivered"].includes(status)) {
        icon = FiTruck;
        title = "Donation collected";
        tone = "collected";
        description = `${donation.item_name || "Your donation"} has been collected successfully.`;
      }

      return { ...donation, icon, title, tone, description };
    });
  }, [donations]);

  return (
    <div className="activity-page">
      <header className="activity-header">
        <span className="activity-eyebrow"><FiActivity /> DONOR ACTIVITY</span>
        <h1>Everything you've given, in one place.</h1>
        <p>Track your donation journey from creation to collection.</p>
      </header>

      <section className="activity-stats">
        <div className="activity-stat"><FiPackage /><span>Donations made</span><strong>{stats.created}</strong></div>
        <div className="activity-stat"><FiCheckCircle /><span>Accepted</span><strong>{stats.accepted}</strong></div>
        <div className="activity-stat"><FiTruck /><span>Collected</span><strong>{stats.collected}</strong></div>
        <div className="activity-stat"><FiClock /><span>Pending</span><strong>{stats.pending}</strong></div>
      </section>

      <section className="activity-card">
        <div className="activity-card-header">
          <div><span>RECENT ACTIVITY</span><h2>Your donation journey</h2></div>
          <FiActivity />
        </div>

        {loading ? (
          <div className="activity-empty">Loading your activity...</div>
        ) : activities.length === 0 ? (
          <div className="activity-empty">
            <div className="activity-empty-icon">📦</div>
            <h3>No activity yet</h3>
            <p>Your donation journey will appear here after you make a donation.</p>
          </div>
        ) : (
          <div className="activity-timeline">
            {activities.map((item) => {
              const Icon = item.icon;
              return (
                <div className="activity-item" key={item.id}>
                  <div className={`activity-dot ${item.tone}`}><Icon /></div>
                  <div className="activity-line" />
                  <div className="activity-item-content">
                    <div className="activity-item-top">
                      <strong>{item.title}</strong>
                      <time>{item.donation_date ? new Date(item.donation_date).toLocaleDateString() : "Recently"}</time>
                    </div>
                    <p>{item.description}</p>
                    {item.ngo_name && <span className="activity-ngo">NGO: {item.ngo_name}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default MyActivity;
