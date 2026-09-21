import { NavLink, useNavigate } from "react-router-dom";
import "./NGOSidebar.css";

const main = [
  ["/ngo-dashboard", "🏠", "Dashboard"],
  ["/ngo-donations", "📦", "Donations"],
  ["/ngo-requirements", "🎯", "Requirements"],
  ["/ngo-allocations", "🤝", "Allocations"],
  ["/ngo-pickups", "🚚", "Pickups"],
];
const insights = [["/ngo-analytics", "📊", "Analytics"], ["/ngo-impact", "❤️", "Impact"]];
const comm = [["/ngo-notifications", "🔔", "Notifications"]];
const account = [["/ngo-profile", "🏢", "Organization Profile"], ["/ngo-settings", "⚙️", "Settings"]];

function Group({ title, items, onNavigate }) {
  return <div className="ngo-nav-group"><div className="ngo-nav-label">{title}</div>{items.map(([to, icon, label]) => <NavLink key={to} to={to} onClick={onNavigate} className={({isActive}) => `ngo-nav-item ${isActive ? "active" : ""}`}><span>{icon}</span><span>{label}</span></NavLink>)}</div>;
}

export default function NGOSidebar({ onNavigate }) {
  const navigate = useNavigate();
  const name = localStorage.getItem("user_name") || "NGO";
  const logout = () => {
    ["access", "refresh", "user_type", "user_id", "user_name", "user_email"].forEach(k => localStorage.removeItem(k));
    navigate("/login", { replace: true });
  };
  return <aside className="ngo-sidebar">
    <div className="ngo-brand"><div className="ngo-brand-mark">🤝</div><div><strong>ResourceBridge</strong><small>NGO Workspace</small></div></div>
    <div className="ngo-user"><div className="ngo-avatar">{name.charAt(0).toUpperCase()}</div><div><strong>{name}</strong><small>NGO</small></div></div>
    <nav>
      <Group title="MAIN" items={main} onNavigate={onNavigate}/>
      <Group title="INSIGHTS" items={insights} onNavigate={onNavigate}/>
      <Group title="COMMUNICATION" items={comm} onNavigate={onNavigate}/>
      <Group title="ACCOUNT" items={account} onNavigate={onNavigate}/>
    </nav>
    <div className="ngo-sidebar-bottom">
      <button className="ngo-bottom-item" onClick={() => document.documentElement.classList.toggle("dark-mode")}><span>🌙</span> Appearance</button>
      <button className="ngo-bottom-item logout" onClick={logout}><span>🚪</span> Logout</button>
    </div>
  </aside>;
}
