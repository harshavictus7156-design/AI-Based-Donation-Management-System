import "./Navbar.css";
import { Link, useNavigate } from "react-router-dom";
import ThemeToggle from "../ThemeToggle/ThemeToggle";

function Navbar() {
  const navigate = useNavigate();

  const token = localStorage.getItem("access");
  const userType = String(
    localStorage.getItem("user_type") || ""
  )
    .trim()
    .toLowerCase();

  // =====================================================
  // LOGOUT
  // =====================================================

  const handleLogout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user_type");

    navigate("/login");
  };

  return (
    <nav className="navbar">

      {/* =================================================
          LOGO
      ================================================= */}

      <div className="logo">
       ResourceBridge
      </div>


      {/* =================================================
          NAVIGATION
      ================================================= */}

      <ul className="nav-links">

        {/* =================================================
            HOME
        ================================================= */}

        <li>
          <Link to="/">
            Home
          </Link>
        </li>


        {/* =================================================
            NOT LOGGED IN
        ================================================= */}

        {!token && (
          <>
            <li>
              <Link to="/login">
                Login
              </Link>
            </li>

            <li>
              <Link to="/register">
                Register
              </Link>
            </li>
          </>
        )}


        {/* =================================================
            LOGGED IN
        ================================================= */}

        {token && (
          <>

            {/* =================================================
                DONOR DASHBOARD
            ================================================= */}

            {userType === "donor" && (
              <>
                <li>
                  <Link to="/dashboard">
                    Dashboard
                  </Link>
                </li>

                <li>
                  <Link to="/donate-item">
                    📦 Donate
                  </Link>
                </li>

                <li>
                  <Link to="/my-donations">
                    📋 My Donations
                  </Link>
                </li>

                <li>
                  <Link to="/profile">
                    👤 Profile
                  </Link>
                </li>
              </>
            )}


            {/* =================================================
                NGO OPTIONS
            ================================================= */}

            {userType === "ngo" && (
              <>
                <li>
                  <Link to="/ngo-dashboard">
                    🏢 NGO Dashboard
                  </Link>
                </li>

                <li>
                  <Link to="/ngo-profile">
                    👤 NGO Profile
                  </Link>
                </li>
              </>
            )}


            {/* =================================================
                LOGOUT
            ================================================= */}

            <li>
              <button
                type="button"
                onClick={handleLogout}
                className="logout-button"
              >
                Logout
              </button>
            </li>

          </>
        )}


        {/* =================================================
            THEME TOGGLE
        ================================================= */}

        <li className="theme-toggle-item">
          <ThemeToggle />
        </li>

      </ul>

    </nav>
  );
}

export default Navbar;