import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../../services/registerService";
import "./DonorRegister.css";

function DonorRegister() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    language: "English",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    if (!/^\d{10}$/.test(formData.phone)) {
      alert("Phone number must contain exactly 10 digits.");
      return;
    }

    if (!/^\d{6}$/.test(formData.pincode)) {
      alert("Pincode must contain exactly 6 digits.");
      return;
    }

    try {
      setLoading(true);

      const data = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        password: formData.password,
        address: formData.address,
        city: formData.city,
        state: formData.state,
        pincode: formData.pincode,
        language_preference: formData.language,
      };

      console.log("Sending Donor Data:", data);
      console.log("USER TYPE: donor");

      const response = await registerUser("donor", data);

      console.log(
        "Donor Registration Success:",
        response
      );

      alert(
        "Donor Registered Successfully!"
      );

      navigate("/login");

    } catch (error) {

      console.log(
        "========== DONOR REGISTRATION ERROR =========="
      );

      console.log(error);

      console.log(
        "Status:",
        error.response?.status
      );

      console.log(
        "Response:",
        error.response?.data
      );

      console.log(
        "=============================================="
      );

      if (error.response?.data) {

        alert(
          JSON.stringify(
            error.response.data
          )
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

  return (
    <div className="donor-register-page">

      {/* =================================================
          LEFT BRAND PANEL
      ================================================= */}

      <section className="donor-register-brand">

        <div className="donor-brand-content">

          <div className="donor-brand-logo">
            <span className="donor-logo-icon">
              ✦
            </span>

            <span>
              ResourceBridge
            </span>
          </div>


          <div className="donor-brand-message">

            <p className="donor-brand-eyebrow">
              BECOME A DONOR
            </p>

            <h1>
              What you give
              <br />
              can become
              <br />
              <span>someone's hope.</span>
            </h1>

            <p>
              Turn things you no longer need into
              meaningful support for people and
              communities who do.
            </p>

          </div>


          <div className="donor-impact-points">

            <div className="donor-impact-item">
              <span>01</span>
              <div>
                <strong>Donate with purpose</strong>
                <p>
                  Give useful items a second life.
                </p>
              </div>
            </div>

            <div className="donor-impact-item">
              <span>02</span>
              <div>
                <strong>Connect with NGOs</strong>
                <p>
                  Find organizations that need them.
                </p>
              </div>
            </div>

            <div className="donor-impact-item">
              <span>03</span>
              <div>
                <strong>See your impact</strong>
                <p>
                  Track every contribution you make.
                </p>
              </div>
            </div>

          </div>

        </div>

        <div className="donor-decoration donor-decoration-one" />
        <div className="donor-decoration donor-decoration-two" />

      </section>


      {/* =================================================
          RIGHT FORM PANEL
      ================================================= */}

      <section className="donor-register-section">

        <div className="donor-register-card">

          {/* HEADER */}

          <div className="donor-register-header">

            <div className="donor-mobile-logo">
              ✦ ResourceBridge
            </div>

            <p className="donor-register-eyebrow">
              CREATE YOUR ACCOUNT
            </p>

            <h2>
              Join as a donor
            </h2>

            <p>
              Create your account and start
              making a difference.
            </p>

          </div>


          {/* ACCOUNT TYPE */}

          <div className="donor-account-switch">

            <p>
              Register as
            </p>

            <div className="donor-account-buttons">

              <button
                type="button"
                className="donor-account-button active"
              >
                <span>👤</span>
                <div>
                  <strong>Donor</strong>
                  <small>
                    Give useful items
                  </small>
                </div>
              </button>


              <button
                type="button"
                className="donor-account-button"
                onClick={() =>
                  navigate("/register/ngo")
                }
              >
                <span>🏢</span>
                <div>
                  <strong>NGO</strong>
                  <small>
                    Receive donations
                  </small>
                </div>
              </button>

            </div>

          </div>


          {/* FORM */}

          <form
            onSubmit={handleSubmit}
            className="donor-register-form"
          >

            {/* =================================================
                PERSONAL INFORMATION
            ================================================= */}

            <div className="form-section-title">

              <span>01</span>

              <div>
                <h3>
                  Personal information
                </h3>

                <p>
                  Tell us a little about yourself.
                </p>
              </div>

            </div>


            {/* NAME */}

            <div className="donor-form-group full-width">

              <label htmlFor="donor-name">
                Full name
              </label>

              <div className="donor-input-wrapper">

                <span>◉</span>

                <input
                  id="donor-name"
                  type="text"
                  name="name"
                  placeholder="Enter your full name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                />

              </div>

            </div>


            {/* EMAIL + PHONE */}

            <div className="donor-form-grid">

              <div className="donor-form-group">

                <label htmlFor="donor-email">
                  Email address
                </label>

                <div className="donor-input-wrapper">

                  <span>✉</span>

                  <input
                    id="donor-email"
                    type="email"
                    name="email"
                    placeholder="you@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />

                </div>

              </div>


              <div className="donor-form-group">

                <label htmlFor="donor-phone">
                  Phone number
                </label>

                <div className="donor-input-wrapper">

                  <span>☎</span>

                  <input
                    id="donor-phone"
                    type="tel"
                    name="phone"
                    placeholder="10-digit number"
                    value={formData.phone}
                    onChange={handleChange}
                    maxLength="10"
                    pattern="[0-9]{10}"
                    required
                  />

                </div>

              </div>

            </div>


            {/* =================================================
                LOCATION
            ================================================= */}

            <div className="form-section-title location-title">

              <span>02</span>

              <div>
                <h3>
                  Location details
                </h3>

                <p>
                  This helps us connect you with
                  nearby opportunities.
                </p>
              </div>

            </div>


            {/* ADDRESS */}

            <div className="donor-form-group full-width">

              <label htmlFor="donor-address">
                Address
              </label>

              <textarea
                id="donor-address"
                name="address"
                placeholder="Enter your complete address"
                value={formData.address}
                onChange={handleChange}
                rows="3"
                required
              />

            </div>


            {/* CITY STATE PINCODE */}

            <div className="donor-form-grid donor-location-grid">

              <div className="donor-form-group">

                <label htmlFor="donor-city">
                  City
                </label>

                <input
                  id="donor-city"
                  type="text"
                  name="city"
                  placeholder="City"
                  value={formData.city}
                  onChange={handleChange}
                  required
                />

              </div>


              <div className="donor-form-group">

                <label htmlFor="donor-state">
                  State
                </label>

                <input
                  id="donor-state"
                  type="text"
                  name="state"
                  placeholder="State"
                  value={formData.state}
                  onChange={handleChange}
                  required
                />

              </div>


              <div className="donor-form-group">

                <label htmlFor="donor-pincode">
                  Pincode
                </label>

                <input
                  id="donor-pincode"
                  type="text"
                  name="pincode"
                  placeholder="6 digits"
                  value={formData.pincode}
                  onChange={handleChange}
                  maxLength="6"
                  pattern="[0-9]{6}"
                  required
                />

              </div>

            </div>


            {/* LANGUAGE */}

            <div className="donor-form-group full-width">

              <label htmlFor="donor-language">
                Preferred language
              </label>

              <select
                id="donor-language"
                name="language"
                value={formData.language}
                onChange={handleChange}
                required
              >
                <option value="English">
                  English
                </option>

                <option value="Telugu">
                  Telugu
                </option>

                <option value="Hindi">
                  Hindi
                </option>

                <option value="Tamil">
                  Tamil
                </option>

                <option value="Kannada">
                  Kannada
                </option>
              </select>

            </div>


            {/* =================================================
                SECURITY
            ================================================= */}

            <div className="form-section-title security-title">

              <span>03</span>

              <div>
                <h3>
                  Secure your account
                </h3>

                <p>
                  Create a password you'll remember.
                </p>
              </div>

            </div>


            {/* PASSWORDS */}

            <div className="donor-form-grid">

              <div className="donor-form-group">

                <label htmlFor="donor-password">
                  Password
                </label>

                <div className="donor-input-wrapper">

                  <span>🔒</span>

                  <input
                    id="donor-password"
                    type={
                      showPassword
                        ? "text"
                        : "password"
                    }
                    name="password"
                    placeholder="Create password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                  />

                  <button
                    type="button"
                    className="donor-password-toggle"
                    onClick={() =>
                      setShowPassword(
                        !showPassword
                      )
                    }
                  >
                    {showPassword ? "◉" : "○"}
                  </button>

                </div>

              </div>


              <div className="donor-form-group">

                <label htmlFor="donor-confirm-password">
                  Confirm password
                </label>

                <div className="donor-input-wrapper">

                  <span>🔒</span>

                  <input
                    id="donor-confirm-password"
                    type={
                      showConfirmPassword
                        ? "text"
                        : "password"
                    }
                    name="confirmPassword"
                    placeholder="Repeat password"
                    value={
                      formData.confirmPassword
                    }
                    onChange={handleChange}
                    required
                  />

                  <button
                    type="button"
                    className="donor-password-toggle"
                    onClick={() =>
                      setShowConfirmPassword(
                        !showConfirmPassword
                      )
                    }
                  >
                    {showConfirmPassword
                      ? "◉"
                      : "○"}
                  </button>

                </div>

              </div>

            </div>


            {/* SUBMIT */}

            <button
              type="submit"
              className="donor-register-submit"
              disabled={loading}
            >

              {loading ? (
                <>
                  <span className="donor-spinner" />
                  Creating account...
                </>
              ) : (
                <>
                  Create Donor Account
                  <span>→</span>
                </>
              )}

            </button>


            {/* LOGIN */}

            <div className="donor-login-prompt">

              <span>
                Already have an account?
              </span>

              <button
                type="button"
                onClick={() =>
                  navigate("/login")
                }
              >
                Sign in
              </button>

            </div>

          </form>

        </div>

      </section>

    </div>
  );
}

export default DonorRegister;