import { useNavigate, useLocation } from "react-router-dom";
import { FiAward } from "react-icons/fi";
import "./AdminLayout.css";

function AdminLayout({ children }) {

    const navigate = useNavigate();
    const location = useLocation();


    // =====================================================
    // LOGOUT
    // =====================================================

    const handleLogout = () => {

        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user_type");
        localStorage.removeItem("user_id");
        localStorage.removeItem("user_name");
        localStorage.removeItem("user_email");

        navigate("/login", {
            replace: true
        });
    };


    // =====================================================
    // ACTIVE MENU
    // =====================================================

    const isActive = (path) => {

        return location.pathname === path;

    };


    return (

        <div className="admin-layout">


            {/* =================================================
                SIDEBAR
            ================================================= */}

            <aside className="admin-sidebar">


                {/* =================================================
                    LOGO
                ================================================= */}

                <div className="admin-logo">

                    <div className="admin-logo-icon">
                        🤝
                    </div>

                    <div className="admin-logo-text">

                        <h2>
                            AI Donation
                        </h2>

                        <span>
                            Admin Panel
                        </span>

                    </div>

                </div>


                {/* =================================================
                    MENU TITLE
                ================================================= */}

                <div className="admin-menu-title">
                    MAIN MENU
                </div>


                {/* =================================================
                    MENU
                ================================================= */}

                <nav className="admin-menu">


                    {/* DASHBOARD */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-dashboard")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-dashboard")
                        }
                    >

                        <span>
                            📊
                        </span>

                        <span>
                            Dashboard
                        </span>

                    </button>


                    {/* DONORS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-donors")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-donors")
                        }
                    >

                        <span>
                            👥
                        </span>

                        <span>
                            Donors
                        </span>

                    </button>


                    {/* RANKING */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-ranking")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-ranking")
                        }
                    >

                        <FiAward />

                        <span>
                            Ranking
                        </span>

                    </button>


                    {/* NGOS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-ngos")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-ngos")
                        }
                    >

                        <span>
                            🏢
                        </span>

                        <span>
                            NGOs
                        </span>

                    </button>


                    {/* DONATIONS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-donations")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-donations")
                        }
                    >

                        <span>
                            🎁
                        </span>

                        <span>
                            Donations
                        </span>

                    </button>


                    {/* REQUIREMENTS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-requirements")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-requirements")
                        }
                    >

                        <span>
                            📋
                        </span>

                        <span>
                            Requirements
                        </span>

                    </button>


                    {/* ALLOCATIONS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-allocations")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-allocations")
                        }
                    >

                        <span>
                            🤝
                        </span>

                        <span>
                            Allocations
                        </span>

                    </button>


                    {/* PICKUPS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-pickups")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-pickups")
                        }
                    >

                        <span>
                            🚚
                        </span>

                        <span>
                            Pickups
                        </span>

                    </button>


                    {/* NOTIFICATIONS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-notifications")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-notifications")
                        }
                    >

                        <span>
                            🔔
                        </span>

                        <span>
                            Notifications
                        </span>

                    </button>


                    {/* ANALYTICS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-analytics")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-analytics")
                        }
                    >

                        <span>
                            📈
                        </span>

                        <span>
                            Analytics
                        </span>

                    </button>


                </nav>


                {/* =================================================
                    BOTTOM MENU
                ================================================= */}

                <div className="admin-sidebar-bottom">


                    {/* SETTINGS */}

                    <button
                        className={
                            `admin-menu-item ${
                                isActive("/admin-settings")
                                    ? "active"
                                    : ""
                            }`
                        }
                        onClick={() =>
                            navigate("/admin-settings")
                        }
                    >

                        <span>
                            ⚙️
                        </span>

                        <span>
                            Settings
                        </span>

                    </button>


                    {/* LOGOUT */}

                    <button
                        className="admin-menu-item admin-logout"
                        onClick={handleLogout}
                    >

                        <span>
                            🚪
                        </span>

                        <span>
                            Logout
                        </span>

                    </button>


                </div>

            </aside>


            {/* =================================================
                MAIN CONTENT
            ================================================= */}

            <main className="admin-layout-content">

                {children}

            </main>


        </div>
    );
}

export default AdminLayout;
