import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../../services/registerService";
import "./NGORegister.css";

function NGORegister() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    ngo_name: "",
    description: "",
    registration_number: "",
    email: "",
    phone: "",
    website: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    language: "English",
    password: "",
    confirmPassword: "",
    certificate: null,
    logo: null,
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, files } = e.target;

    setFormData((prev) => ({
      ...prev,
      [name]:
        files && files.length > 0
          ? files[0]
          : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    if (formData.password.length < 6) {
      alert("Password must contain at least 6 characters.");
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

    if (!formData.certificate) {
      alert("Please upload NGO Certificate.");
      return;
    }

    if (!formData.logo) {
      alert("Please upload NGO Logo.");
      return;
    }

    try {
      setLoading(true);

      const data = new FormData();

      data.append("ngo_name", formData.ngo_name);
      data.append("description", formData.description);
      data.append(
        "registration_no",
        formData.registration_number
      );
      data.append("email_id", formData.email);
      data.append("phone_no", formData.phone);

      if (formData.website) {
        data.append(
          "website_link",
          formData.website
        );
      }

      data.append("address", formData.address);
      data.append("city", formData.city);
      data.append("state", formData.state);
      data.append("pincode", formData.pincode);
      data.append("language", formData.language);
      data.append("password", formData.password);

      data.append(
        "certificate_files",
        formData.certificate
      );

      data.append(
        "picture",
        formData.logo
      );

      console.log(
        "========== NGO REGISTRATION DATA =========="
      );

      for (const [key, value] of data.entries()) {
        console.log(key, value);
      }

      const response = await registerUser(
        "ngo",
        data
      );

      console.log(
        "NGO Registration Success:",
        response
      );

      alert(
        "NGO Registered Successfully! 🏢📄"
      );

      navigate("/login");

    } catch (error) {

      console.log(
        "========== NGO REGISTRATION ERROR =========="
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

      if (error.response?.data) {
        alert(
          JSON.stringify(
            error.response.data
          )
        );
      } else {
        alert(
          "Cannot connect to backend server."
        );
      }

    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ngo-register-page">

      {/* =================================================
          LEFT BRAND PANEL
      ================================================= */}

      <section className="ngo-register-brand">

        <div className="ngo-brand-content">

          <div className="ngo-brand-logo">

            <span className="ngo-logo-icon">
              ✦
            </span>

            <span>
              ResourceBridge
            </span>

          </div>


          <div className="ngo-brand-message">

            <p className="ngo-brand-eyebrow">
              BECOME A PARTNER NGO
            </p>

            <h1>
              Your mission
              <br />
              can become
              <br />
              <span>someone's hope.</span>
            </h1>

            <p>
              Connect your organization with meaningful
              donations and resources that can create
              real impact in your community.
            </p>

          </div>


          <div className="ngo-impact-points">

            <div className="ngo-impact-item">

              <span>
                01
              </span>

              <div>
                <strong>
                  Receive useful donations
                </strong>

                <p>
                  Get resources your organization needs.
                </p>
              </div>

            </div>


            <div className="ngo-impact-item">

              <span>
                02
              </span>

              <div>
                <strong>
                  Connect with donors
                </strong>

                <p>
                  Build meaningful connections with donors.
                </p>
              </div>

            </div>


            <div className="ngo-impact-item">

              <span>
                03
              </span>

              <div>
                <strong>
                  Grow your impact
                </strong>

                <p>
                  Turn every contribution into community impact.
                </p>
              </div>

            </div>

          </div>

        </div>


        <div className="ngo-decoration ngo-decoration-one" />
        <div className="ngo-decoration ngo-decoration-two" />

      </section>


      {/* =================================================
          RIGHT FORM PANEL
      ================================================= */}

      <section className="ngo-register-section">

        <div className="ngo-register-card">


          {/* HEADER */}

          <div className="ngo-register-header">

            <div className="ngo-mobile-logo">
              ✦ ResourceBridge
            </div>

            <p className="ngo-register-eyebrow">
              CREATE YOUR ORGANIZATION ACCOUNT
            </p>

            <h2>
              Join as an NGO
            </h2>

            <p>
              Register your organization and start
              connecting with donors.
            </p>

          </div>


          {/* ACCOUNT TYPE */}

          <div className="ngo-account-switch">

            <p>
              Register as
            </p>

            <div className="ngo-account-buttons">

              <button
                type="button"
                className="ngo-account-button"
                onClick={() =>
                  navigate("/register/donor")
                }
              >
                <span>
                  👤
                </span>

                <div>
                  <strong>
                    Donor
                  </strong>

                  <small>
                    Give useful items
                  </small>
                </div>
              </button>


              <button
                type="button"
                className="ngo-account-button active"
              >
                <span>
                  🏢
                </span>

                <div>
                  <strong>
                    NGO
                  </strong>

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
            className="ngo-register-form"
            encType="multipart/form-data"
          >


            {/* =================================================
                ORGANIZATION INFORMATION
            ================================================= */}

            <div className="ngo-form-section-title">

              <span>
                01
              </span>

              <div>

                <h3>
                  Organization information
                </h3>

                <p>
                  Tell us about your NGO.
                </p>

              </div>

            </div>


            {/* NGO NAME */}

            <div className="ngo-form-group full-width">

              <label htmlFor="ngo-name">
                NGO name
              </label>

              <div className="ngo-input-wrapper">

                <span>
                  🏢
                </span>

                <input
                  id="ngo-name"
                  type="text"
                  name="ngo_name"
                  placeholder="Enter your NGO name"
                  value={formData.ngo_name}
                  onChange={handleChange}
                  required
                />

              </div>

            </div>


            {/* DESCRIPTION */}

            <div className="ngo-form-group full-width">

              <label htmlFor="ngo-description">
                Organization description
              </label>

              <textarea
                id="ngo-description"
                name="description"
                placeholder="Describe your NGO and its work"
                value={formData.description}
                onChange={handleChange}
                rows="3"
                required
              />

            </div>


            {/* REGISTRATION + EMAIL */}

            <div className="ngo-form-grid">

              <div className="ngo-form-group">

                <label htmlFor="ngo-registration">
                  Registration number
                </label>

                <input
                  id="ngo-registration"
                  type="text"
                  name="registration_number"
                  placeholder="Registration number"
                  value={formData.registration_number}
                  onChange={handleChange}
                  required
                />

              </div>


              <div className="ngo-form-group">

                <label htmlFor="ngo-email">
                  Email address
                </label>

                <div className="ngo-input-wrapper">

                  <span>
                    ✉
                  </span>

                  <input
                    id="ngo-email"
                    type="email"
                    name="email"
                    placeholder="ngo@example.com"
                    value={formData.email}
                    onChange={handleChange}
                    required
                  />

                </div>

              </div>

            </div>


            {/* PHONE + WEBSITE */}

            <div className="ngo-form-grid">

              <div className="ngo-form-group">

                <label htmlFor="ngo-phone">
                  Phone number
                </label>

                <div className="ngo-input-wrapper">

                  <span>
                    ☎
                  </span>

                  <input
                    id="ngo-phone"
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


              <div className="ngo-form-group">

                <label htmlFor="ngo-website">
                  Website
                </label>

                <input
                  id="ngo-website"
                  type="url"
                  name="website"
                  placeholder="https://example.org"
                  value={formData.website}
                  onChange={handleChange}
                />

              </div>

            </div>


            {/* =================================================
                LOCATION
            ================================================= */}

            <div className="ngo-form-section-title location-title">

              <span>
                02
              </span>

              <div>

                <h3>
                  Organization location
                </h3>

                <p>
                  Help donors connect with your organization.
                </p>

              </div>

            </div>


            {/* ADDRESS */}

            <div className="ngo-form-group full-width">

              <label htmlFor="ngo-address">
                Address
              </label>

              <textarea
                id="ngo-address"
                name="address"
                placeholder="Enter complete organization address"
                value={formData.address}
                onChange={handleChange}
                rows="3"
                required
              />

            </div>


            {/* CITY STATE PINCODE */}

            <div className="ngo-form-grid ngo-location-grid">

              <div className="ngo-form-group">

                <label htmlFor="ngo-city">
                  City
                </label>

                <input
                  id="ngo-city"
                  type="text"
                  name="city"
                  placeholder="City"
                  value={formData.city}
                  onChange={handleChange}
                  required
                />

              </div>


              <div className="ngo-form-group">

                <label htmlFor="ngo-state">
                  State
                </label>

                <input
                  id="ngo-state"
                  type="text"
                  name="state"
                  placeholder="State"
                  value={formData.state}
                  onChange={handleChange}
                  required
                />

              </div>


              <div className="ngo-form-group">

                <label htmlFor="ngo-pincode">
                  Pincode
                </label>

                <input
                  id="ngo-pincode"
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

            <div className="ngo-form-group full-width">

              <label htmlFor="ngo-language">
                Preferred language
              </label>

              <select
                id="ngo-language"
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
                VERIFICATION
            ================================================= */}

            <div className="ngo-form-section-title security-title">

              <span>
                03
              </span>

              <div>

                <h3>
                  Verification & security
                </h3>

                <p>
                  Verify your organization and secure your account.
                </p>

              </div>

            </div>


            {/* CERTIFICATE */}

            <div className="ngo-file-field">

              <label>
                📄 NGO Certificate
              </label>

              <input
                type="file"
                name="certificate"
                onChange={handleChange}
                accept=".pdf,.jpg,.jpeg,.png"
                required
              />

              <small>
                Upload PDF, JPG, JPEG or PNG.
              </small>

            </div>


            {/* LOGO */}

            <div className="ngo-file-field">

              <label>
                🖼️ NGO Logo
              </label>

              <input
                type="file"
                name="logo"
                onChange={handleChange}
                accept="image/*"
                required
              />

              <small>
                Upload your organization's logo.
              </small>

            </div>


            {/* PASSWORDS */}

            <div className="ngo-form-grid">

              <div className="ngo-form-group">

                <label htmlFor="ngo-password">
                  Password
                </label>

                <div className="ngo-input-wrapper">

                  <span>
                    🔒
                  </span>

                  <input
                    id="ngo-password"
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
                    className="ngo-password-toggle"
                    onClick={() =>
                      setShowPassword(
                        !showPassword
                      )
                    }
                  >
                    {showPassword
                      ? "◉"
                      : "○"}
                  </button>

                </div>

              </div>


              <div className="ngo-form-group">

                <label htmlFor="ngo-confirm-password">
                  Confirm password
                </label>

                <div className="ngo-input-wrapper">

                  <span>
                    🔒
                  </span>

                  <input
                    id="ngo-confirm-password"
                    type={
                      showConfirmPassword
                        ? "text"
                        : "password"
                    }
                    name="confirmPassword"
                    placeholder="Repeat password"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    required
                  />

                  <button
                    type="button"
                    className="ngo-password-toggle"
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
              className="ngo-register-submit"
              disabled={loading}
            >

              {loading ? (
                <>
                  <span className="ngo-spinner" />
                  Creating NGO Account...
                </>
              ) : (
                <>
                  Create NGO Account
                  <span>
                    →
                  </span>
                </>
              )}

            </button>


            {/* LOGIN */}

            <div className="ngo-login-prompt">

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

export default NGORegister;