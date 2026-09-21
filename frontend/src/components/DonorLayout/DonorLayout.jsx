import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { FiMenu, FiX } from "react-icons/fi";
import { useNavigate } from "react-router-dom";
import Sidebar from "../Sidebar/Sidebar";
import { NotificationBell } from "../NotificationBell/NotificationBell";
import "./DonorLayout.css";

const pageMeta = {
  "/dashboard": { title: "Dashboard", subtitle: "Your donation overview" },
  "/donate-item": { title: "Donate an Item", subtitle: "Turn something you have into something someone needs" },
  "/my-donations": { title: "My Donations", subtitle: "Track everything you have donated" },
  "/my-activity": { title: "My Activity", subtitle: "Follow your donation journey" },
  "/explore-ngos": { title: "Explore NGOs", subtitle: "Discover organizations making a difference" },
  "/ranking": { title: "Donor Ranking", subtitle: "See the community impact leaderboard" },
  "/notifications": { title: "Notifications", subtitle: "Stay updated on your donations" },
  "/profile": { title: "Profile", subtitle: "Manage your donor information" },
  "/settings": { title: "Settings", subtitle: "Personalize your donor experience" },
};

function DonorLayout({ children }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const userName = localStorage.getItem("user_name") || "Donor";

  const currentPath = location.pathname;
  const meta = Object.entries(pageMeta).find(([path]) => currentPath === path)?.[1]
    || (currentPath.startsWith("/edit-donation/")
      ? { title: "Edit Donation", subtitle: "Update your donation details" }
      : { title: "Donor Workspace", subtitle: "Manage your donations" });

  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") setSidebarOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <div className="donor-layout">
      <Sidebar mobileOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close navigation"
          className="donor-sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="donor-layout-content">
        <header className="donor-appbar">
          <div className="donor-appbar-left">
            <button
              type="button"
              className="donor-menu-button"
              aria-label="Open navigation"
              onClick={() => setSidebarOpen(true)}
            >
              {sidebarOpen ? <FiX /> : <FiMenu />}
            </button>
            <div>
              <span className="donor-appbar-kicker">DONOR WORKSPACE</span>
              <h1>{meta.title}</h1>
              <p>{meta.subtitle}</p>
            </div>
          </div>

          <div className="donor-appbar-right">
            <NotificationBell route="/notifications" className="donor-appbar-notification-wrap" />
            <div className="donor-appbar-user">
              <div className="donor-appbar-avatar">{userName.charAt(0).toUpperCase()}</div>
              <div>
                <strong>{userName}</strong>
                <small>Donor</small>
              </div>
            </div>
          </div>
        </header>

        <div className="donor-page-shell">
          {children}
        </div>
      </main>
    </div>
  );
}

export default DonorLayout;
