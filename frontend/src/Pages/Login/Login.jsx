import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../../services/authService";
import "./Login.css";

function Login() {
  const navigate = useNavigate();

  const [loginType, setLoginType] = useState("donor");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  // =====================================================
  // CHANGE LOGIN TYPE
  // =====================================================

  const changeLoginType = (type) => {
    setLoginType(type);

    setEmail("");
    setPassword("");
  };

  // =====================================================
  // LOGIN
  // =====================================================

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please enter email and password.");
      return;
    }

    try {
      setLoading(true);

      const data = await loginUser(
        email,
        password
      );

      console.log(
        "Login Success:",
        data
      );

      // =================================================
      // CHECK RESPONSE
      // =================================================

      if (!data) {
        alert(
          "Invalid login response."
        );
        return;
      }

      if (!data.tokens) {
        alert(
          "Login tokens were not received."
        );

        console.error(
          "Tokens missing:",
          data
        );

        return;
      }

      // =================================================
      // NORMALIZE USER TYPE
      // =================================================

      const userType = String(
        data.user_type || ""
      )
        .trim()
        .toLowerCase();

      console.log(
        "User Type:",
        userType
      );

      // =================================================
      // CHECK SELECTED LOGIN TYPE
      // =================================================

      if (
        loginType === "admin"
        && userType !== "admin"
      ) {
        alert(
          "These credentials do not belong to an admin account."
        );

        return;
      }

      if (
        loginType === "donor"
        && userType !== "donor"
      ) {
        alert(
          "Please use the correct login section for your account."
        );

        return;
      }

      if (
        loginType === "ngo"
        && userType !== "ngo"
      ) {
        alert(
          "Please use the correct login section for your account."
        );

        return;
      }

      // =================================================
      // SAVE TOKENS
      // =================================================

      localStorage.setItem(
        "access",
        data.tokens.access
      );

      localStorage.setItem(
        "refresh",
        data.tokens.refresh
      );

      // =================================================
      // SAVE USER DETAILS
      // =================================================

      localStorage.setItem(
        "user_type",
        userType
      );

      localStorage.setItem(
        "user_id",
        String(data.user_id || "")
      );

      localStorage.setItem(
        "user_name",
        data.name || ""
      );

      localStorage.setItem(
        "user_email",
        data.email || ""
      );

      // =================================================
      // DEBUG
      // =================================================

      console.log(
        "================================="
      );

      console.log(
        "LOGIN SUCCESS"
      );

      console.log(
        "User Type:",
        userType
      );

      console.log(
        "User ID:",
        data.user_id
      );

      console.log(
        "User Name:",
        data.name
      );

      console.log(
        "User Email:",
        data.email
      );

      console.log(
        "================================="
      );

      // =================================================
      // ADMIN LOGIN
      // =================================================

      if (userType === "admin") {

        alert(
          "Admin Login Successful!"
        );

        navigate(
          "/admin-dashboard"
        );

        return;
      }

      // =================================================
      // NGO LOGIN
      // =================================================

      if (userType === "ngo") {

        alert(
          "NGO Login Successful!"
        );

        navigate(
          "/ngo-dashboard"
        );

        return;
      }

      // =================================================
      // DONOR LOGIN
      // =================================================

      if (userType === "donor") {

        alert(
          "Login Successful!"
        );

        navigate(
          "/dashboard"
        );

        return;
      }

      // =================================================
      // UNKNOWN USER TYPE
      // =================================================

      console.error(
        "Unknown user type:",
        data.user_type
      );

      alert(
        "Unknown user type. Please contact the administrator."
      );

    } catch (error) {

      // =================================================
      // LOGIN ERROR
      // =================================================

      console.log(
        "========== LOGIN ERROR =========="
      );

      console.log(
        error
      );

      console.log(
        "Status:",
        error.response?.status
      );

      console.log(
        "Response:",
        error.response?.data
      );

      console.log(
        "================================="
      );

      if (error.response) {

        alert(
          error.response.data?.message ||
          error.response.data?.detail ||
          "Login Failed"
        );

      } else {

        alert(
          "Cannot connect to backend server"
        );
      }

    } finally {

      setLoading(false);

    }
  };

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="login-page">

      {/* =================================================
          LEFT BRAND SECTION
      ================================================= */}

      <section className="login-brand">

        <div className="brand-content">

          <div className="brand-logo">

            <span className="brand-logo-icon">
              ✦
            </span>

            <span>
              ResourceBridge
            </span>

          </div>

          <div className="brand-message">

            <p className="brand-eyebrow">
              GIVE • CONNECT • IMPACT
            </p>

            <h1>
              Give more.
              <br />
              Waste less.
              <br />

              <span>
                Create impact.
              </span>

            </h1>

            <p className="brand-description">
              Connect useful resources with people
              and organizations that need them.
              Every contribution has the power to
              create a meaningful difference.
            </p>

          </div>

          <div className="impact-card">

            <div className="impact-icon">
              ♥
            </div>

            <div>

              <strong>
                Every donation matters.
              </strong>

              <span>
                Your unused items can become
                someone else's opportunity.
              </span>

            </div>

          </div>

        </div>

        <div
          className="brand-decoration decoration-one"
        />

        <div
          className="brand-decoration decoration-two"
        />

      </section>


      {/* =================================================
          RIGHT LOGIN SECTION
      ================================================= */}

      <section className="login-section">

        <div className="login-card">

          {/* =================================================
              HEADER
          ================================================= */}

          <div className="login-header">

            <span className="mobile-logo">
              ✦ ResourceBridge
            </span>

            <p className="login-eyebrow">
              WELCOME BACK
            </p>

            <h2>
              Sign in to continue
            </h2>

            <p>
              Access your donations, profile
              and impact dashboard.
            </p>

          </div>


          {/* =================================================
              LOGIN TYPE TABS
          ================================================= */}

          <div className="login-type-tabs">

            <button
              type="button"
              className={
                loginType === "donor"
                  ? "login-type-tab active"
                  : "login-type-tab"
              }
              onClick={() =>
                changeLoginType("donor")
              }
            >
              <span className="login-tab-icon">
                👤
              </span>

              <span>
                Donor
              </span>
            </button>


            <button
              type="button"
              className={
                loginType === "ngo"
                  ? "login-type-tab active"
                  : "login-type-tab"
              }
              onClick={() =>
                changeLoginType("ngo")
              }
            >
              <span className="login-tab-icon">
                🏢
              </span>

              <span>
                NGO
              </span>
            </button>


            <button
              type="button"
              className={
                loginType === "admin"
                  ? "login-type-tab active admin-tab"
                  : "login-type-tab admin-tab"
              }
              onClick={() =>
                changeLoginType("admin")
              }
            >
              <span className="login-tab-icon">
                🛡️
              </span>

              <span>
                Admin
              </span>
            </button>

          </div>


          {/* =================================================
              SELECTED LOGIN MESSAGE
          ================================================= */}

          <div className="selected-login-message">

            {loginType === "donor" && (
              <>
                <strong>
                  Donor Login
                </strong>

                <span>
                  Sign in to manage your donations.
                </span>
              </>
            )}

            {loginType === "ngo" && (
              <>
                <strong>
                  NGO Login
                </strong>

                <span>
                  Sign in to manage NGO activities.
                </span>
              </>
            )}

            {loginType === "admin" && (
              <>
                <strong>
                  Admin Login
                </strong>

                <span>
                  Sign in to manage ResourceBridge.
                </span>
              </>
            )}

          </div>


          {/* =================================================
              LOGIN FORM
          ================================================= */}

          <form
            onSubmit={handleSubmit}
            className="login-form"
          >

            {/* =================================================
                EMAIL
            ================================================= */}

            <div className="form-group">

              <label htmlFor="email">

                {loginType === "admin"
                  ? "Admin email"
                  : "Email address"}

              </label>

              <div className="input-wrapper">

                <span
                  className="input-icon"
                  aria-hidden="true"
                >
                  ✉️
                </span>

                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="username"
                  placeholder={
                    loginType === "admin"
                      ? "admin@example.com"
                      : "you@example.com"
                  }
                  value={email}
                  onChange={(e) =>
                    setEmail(
                      e.target.value
                    )
                  }
                  required
                />

              </div>

            </div>


            {/* =================================================
                PASSWORD
            ================================================= */}

            <div className="form-group">

              <div className="password-label-row">

                <label htmlFor="password">
                  Password
                </label>

                <button
                  type="button"
                  className="forgot-button"
                  onClick={() =>
                    alert(
                      "Password reset will be available soon."
                    )
                  }
                >
                  Forgot password?
                </button>

              </div>


              <div className="input-wrapper">

                <span className="input-icon">
                  🔒
                </span>

                <input
                  id="password"
                  name="password"
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  autoComplete="current-password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) =>
                    setPassword(
                      e.target.value
                    )
                  }
                  required
                />


                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      !showPassword
                    )
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword
                    ? "◉"
                    : "○"}
                </button>

              </div>

            </div>


            {/* =================================================
                LOGIN BUTTON
            ================================================= */}

            <button
              type="submit"
              className={
                loginType === "admin"
                  ? "login-submit admin-login-submit"
                  : "login-submit"
              }
              disabled={loading}
            >

              {loading ? (

                <>
                  <span className="spinner" />

                  <span>
                    Signing in...
                  </span>
                </>

              ) : (

                <>
                  <span>
                    {loginType === "admin"
                      ? "Sign In as Admin"
                      : "Sign In"}
                  </span>

                  <span className="button-arrow">
                    →
                  </span>
                </>

              )}

            </button>

          </form>


          {/* =================================================
              REGISTER
          ================================================= */}

          {loginType !== "admin" && (

            <div className="register-prompt">

              <span>
                Don't have an account?
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/register")
                }
              >
                Create an account
              </button>

            </div>

          )}


          {/* =================================================
              ADMIN INFORMATION
          ================================================= */}

          {loginType === "admin" && (

            <div className="admin-login-info">

              <span>
                🛡️
              </span>

              <p>
                Admin access is restricted to
                authorized ResourceBridge administrators.
              </p>

            </div>

          )}


          {/* =================================================
              FOOTER
          ================================================= */}

          <p className="login-footer">

            By continuing, you agree to our

            <span>
              {" "}Terms{" "}
            </span>

            and

            <span>
              {" "}Privacy Policy.
            </span>

          </p>

        </div>

      </section>

    </div>
  );
}

export default Login;