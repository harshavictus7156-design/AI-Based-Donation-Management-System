import { useEffect, useState } from "react";
import api from "../../services/api";
import "./DonorProfile.css";

function DonorProfile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // =====================================================
  // EDIT MODE
  // =====================================================

  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState("");
  const [saveSuccess, setSaveSuccess] = useState("");

  const [editForm, setEditForm] = useState({
    name: "",
    phone: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    language_preference: "English",
  });

  // =====================================================
  // FETCH DONOR PROFILE
  // =====================================================

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);

        const userId =
          localStorage.getItem("user_id");

        console.log(
          "Fetching donor profile:",
          userId
        );

        /*
         * We use the logged-in donor ID.
         * Change the endpoint only if your backend
         * uses a different profile URL.
         */

        const response = await api.get(
          `register/${userId}/`
        );

        console.log(
          "Donor Profile:",
          response.data
        );

        setProfile(response.data);

      } catch (error) {
        console.error(
          "========== PROFILE ERROR =========="
        );

        console.error(error);

        console.error(
          "Status:",
          error.response?.status
        );

        console.error(
          "Response:",
          error.response?.data
        );

        console.error(
          "==================================="
        );

        /*
         * Fallback to localStorage so the page
         * can still display basic information.
         */

        setProfile({
          name:
            localStorage.getItem(
              "user_name"
            ) || "Donor",

          email:
            localStorage.getItem(
              "user_email"
            ) || "",

          phone: "",
          address: "",
          city: "",
          state: "",
          pincode: "",
          language_preference:
            "English",
        });

      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  // =====================================================
  // EDIT PROFILE
  // =====================================================

  const startEditing = () => {
    setEditForm({
      name: profile?.name || "",
      phone: profile?.phone || "",
      address: profile?.address || "",
      city: profile?.city || "",
      state: profile?.state || "",
      pincode: profile?.pincode || "",
      language_preference:
        profile?.language_preference || "English",
    });

    setSaveError("");
    setSaveSuccess("");
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setSaveError("");
    setSaveSuccess("");
  };

  const handleEditChange = (event) => {
    const { name, value } = event.target;

    setEditForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const saveProfile = async (event) => {
    event.preventDefault();

    const userId = localStorage.getItem("user_id");

    if (!userId) {
      setSaveError("User session not found. Please login again.");
      return;
    }

    if (!editForm.name.trim()) {
      setSaveError("Full name is required.");
      return;
    }

    setSaving(true);
    setSaveError("");
    setSaveSuccess("");

    try {
      const response = await api.patch(
        `register/${userId}/`,
        {
          name: editForm.name.trim(),
          phone: editForm.phone.trim(),
          address: editForm.address.trim(),
          city: editForm.city.trim(),
          state: editForm.state.trim(),
          pincode: editForm.pincode.trim(),
          language_preference:
            editForm.language_preference,
        }
      );

      setProfile(response.data);

      // Keep basic cached profile details in sync.
      localStorage.setItem(
        "user_name",
        response.data?.name || editForm.name
      );

      if (response.data?.email) {
        localStorage.setItem(
          "user_email",
          response.data.email
        );
      }

      // Also keep the registered location useful for
      // the Donate Item page.
      const locationParts = [
        response.data?.city,
        response.data?.state,
      ].filter(Boolean);

      if (locationParts.length > 0) {
        localStorage.setItem(
          "user_location",
          locationParts.join(", ")
        );
      }

      setEditForm({
        name: response.data?.name || editForm.name,
        phone: response.data?.phone || "",
        address: response.data?.address || "",
        city: response.data?.city || "",
        state: response.data?.state || "",
        pincode: response.data?.pincode || "",
        language_preference:
          response.data?.language_preference ||
          "English",
      });

      setSaveSuccess("Profile updated successfully.");
      setIsEditing(false);
    } catch (error) {
      console.error(
        "========== UPDATE PROFILE ERROR =========="
      );
      console.error("STATUS:", error.response?.status);
      console.error("DATA:", error.response?.data);
      console.error("ERROR:", error);

      const data = error.response?.data;

      let message =
        "Unable to update profile. Please try again.";

      if (typeof data === "string") {
        message = data;
      } else if (data?.detail) {
        message = data.detail;
      } else if (data?.message) {
        message = data.message;
      } else if (data && typeof data === "object") {
        message = Object.entries(data)
          .map(([field, value]) => {
            const errorText = Array.isArray(value)
              ? value.join(", ")
              : String(value);

            return `${field}: ${errorText}`;
          })
          .join(" | ");
      }

      setSaveError(message);
    } finally {
      setSaving(false);
    }
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="profile-loading">

        <div className="profile-spinner" />

        <p>
          Loading your profile...
        </p>

      </div>
    );
  }

  // =====================================================
  // PROFILE DATA
  // =====================================================

  const name =
    profile?.name ||
    localStorage.getItem("user_name") ||
    "Donor";

  const email =
    profile?.email ||
    localStorage.getItem("user_email") ||
    "Not available";

  const phone =
    profile?.phone ||
    "Not available";

  const address =
    profile?.address ||
    "Not available";

  const city =
    profile?.city ||
    "Not available";

  const state =
    profile?.state ||
    "Not available";

  const pincode =
    profile?.pincode ||
    "Not available";

  const language =
    profile?.language_preference ||
    "English";

  // =====================================================
  // INITIAL
  // =====================================================

  const initial =
    name.charAt(0).toUpperCase();

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="donor-profile-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <section className="profile-hero">

        <div className="profile-hero-content">

          <span className="profile-eyebrow">
            DONOR PROFILE
          </span>

          <h1>
            Your profile
          </h1>

          <p>
            Manage your personal information
            and keep your donation account
            up to date.
          </p>

        </div>

        <div className="profile-hero-symbol">
          👤
        </div>

      </section>


      {/* =================================================
          PROFILE MAIN
      ================================================= */}

      <div className="profile-layout">

        {/* =================================================
            LEFT PROFILE CARD
        ================================================= */}

        <aside className="profile-summary">

          <div className="profile-avatar">
            {initial}
          </div>

          <h2>
            {name}
          </h2>

          <p>
            {email}
          </p>

          <div className="profile-role">
            ● DONOR ACCOUNT
          </div>

          <div className="profile-divider" />

          <div className="profile-summary-item">

            <span>
              Member
            </span>

            <strong>
              Donor
            </strong>

          </div>

          <div className="profile-summary-item">

            <span>
              Language
            </span>

            <strong>
              {language}
            </strong>

          </div>

        </aside>


        {/* =================================================
            RIGHT DETAILS
        ================================================= */}

        <main className="profile-details">

          {/* =================================================
              PERSONAL INFORMATION
          ================================================= */}

          <section className="profile-card">

            <div className="profile-card-heading">

              <div className="profile-card-icon">
                👤
              </div>

              <div>
                <span>
                  PERSONAL INFORMATION
                </span>

                <h2>
                  {isEditing
                    ? "Edit your details"
                    : "Basic details"}
                </h2>
              </div>

            </div>

            {isEditing ? (

              <form
                className="profile-edit-form"
                onSubmit={saveProfile}
              >

                <div className="profile-edit-grid">

                  <label className="profile-edit-field">
                    <span>Full Name</span>

                    <input
                      type="text"
                      name="name"
                      value={editForm.name}
                      onChange={handleEditChange}
                      required
                    />
                  </label>

                  <label className="profile-edit-field">
                    <span>Email Address</span>

                    <input
                      type="email"
                      value={email}
                      readOnly
                      disabled
                    />

                    <small>
                      Email cannot be changed here.
                    </small>
                  </label>

                  <label className="profile-edit-field">
                    <span>Phone Number</span>

                    <input
                      type="tel"
                      name="phone"
                      value={editForm.phone}
                      onChange={handleEditChange}
                    />
                  </label>

                  <label className="profile-edit-field">
                    <span>Preferred Language</span>

                    <select
                      name="language_preference"
                      value={
                        editForm.language_preference
                      }
                      onChange={handleEditChange}
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
                    </select>
                  </label>

                </div>

              </form>

            ) : (

              <div className="profile-info-grid">

                <div className="profile-info">
                  <span>Full Name</span>
                  <strong>{name}</strong>
                </div>

                <div className="profile-info">
                  <span>Email Address</span>
                  <strong>{email}</strong>
                </div>

                <div className="profile-info">
                  <span>Phone Number</span>
                  <strong>{phone}</strong>
                </div>

                <div className="profile-info">
                  <span>Preferred Language</span>
                  <strong>{language}</strong>
                </div>

              </div>

            )}

          </section>


          {/* =================================================
              LOCATION
          ================================================= */}

          <section className="profile-card">

            <div className="profile-card-heading">

              <div className="profile-card-icon coral">
                📍
              </div>

              <div>
                <span>
                  LOCATION
                </span>

                <h2>
                  {isEditing
                    ? "Edit address details"
                    : "Address details"}
                </h2>
              </div>

            </div>

            {isEditing ? (

              <div className="profile-edit-grid">

                <label className="profile-edit-field full">
                  <span>Address</span>

                  <textarea
                    name="address"
                    value={editForm.address}
                    onChange={handleEditChange}
                    rows="3"
                  />
                </label>

                <label className="profile-edit-field">
                  <span>City</span>

                  <input
                    type="text"
                    name="city"
                    value={editForm.city}
                    onChange={handleEditChange}
                  />
                </label>

                <label className="profile-edit-field">
                  <span>State</span>

                  <input
                    type="text"
                    name="state"
                    value={editForm.state}
                    onChange={handleEditChange}
                  />
                </label>

                <label className="profile-edit-field">
                  <span>Pincode</span>

                  <input
                    type="text"
                    name="pincode"
                    value={editForm.pincode}
                    onChange={handleEditChange}
                    maxLength="10"
                  />
                </label>

              </div>

            ) : (

              <>
                <div className="profile-address">

                  <div className="address-icon">
                    📍
                  </div>

                  <div>
                    <span>
                      Address
                    </span>

                    <strong>
                      {address}
                    </strong>
                  </div>

                </div>

                <div className="profile-info-grid location-grid">

                  <div className="profile-info">
                    <span>City</span>
                    <strong>{city}</strong>
                  </div>

                  <div className="profile-info">
                    <span>State</span>
                    <strong>{state}</strong>
                  </div>

                  <div className="profile-info">
                    <span>Pincode</span>
                    <strong>{pincode}</strong>
                  </div>

                </div>
              </>

            )}

          </section>


          {/* =================================================
              ACCOUNT
          ================================================= */}

          <section className="profile-card account-card">

            <div className="profile-card-heading">

              <div className="profile-card-icon">
                🔐
              </div>

              <div>

                <span>
                  ACCOUNT
                </span>

                <h2>
                  Account settings
                </h2>

              </div>

            </div>


            {saveError && (
              <div className="profile-save-message error">
                {saveError}
              </div>
            )}

            {saveSuccess && (
              <div className="profile-save-message success">
                ✓ {saveSuccess}
              </div>
            )}

            {isEditing && (
              <div className="profile-edit-actions">

                <button
                  type="button"
                  className="dashboard-button"
                  onClick={cancelEditing}
                  disabled={saving}
                >
                  Cancel
                </button>

                <button
                  type="button"
                  className="edit-profile-button"
                  onClick={saveProfile}
                  disabled={saving}
                >
                  {saving ? "Saving..." : "✓ Save Changes"}
                </button>

              </div>
            )}

            {!isEditing && (
              <div className="account-actions">

                <button
                  className="edit-profile-button"
                  onClick={startEditing}
                >
                  ✎
                  <span>
                    Edit Profile
                  </span>
                  →
                </button>

                <button
                  className="dashboard-button"
                  onClick={() =>
                    window.location.href =
                      "/dashboard"
                  }
                >
                  ←
                  <span>
                    Back to Dashboard
                  </span>
                </button>

              </div>
            )}

          </section>

        </main>

      </div>

    </div>
  );
}

export default DonorProfile;