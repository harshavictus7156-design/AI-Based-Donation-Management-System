import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./NGOProfile.css";

function NGOProfile() {
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [editData, setEditData] = useState({
    ngo_name: "",
    description: "",
    registration_no: "",
    email_id: "",
    phone_no: "",
    website_link: "",
    address: "",
    city: "",
    state: "",
    pincode: "",
    language: "English",
  });

  // =====================================================
  // FETCH PROFILE
  // =====================================================

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("profile/");

      console.log(
        "========== NGO PROFILE =========="
      );

      console.log(response.data);

      setProfile(response.data);

    } catch (error) {
      console.error(
        "========== NGO PROFILE ERROR =========="
      );

      console.error(error);
      console.error("Status:", error.response?.status);
      console.error("Response:", error.response?.data);

      setError(
        error.response?.data?.detail ||
        error.response?.data?.message ||
        "Unable to load NGO profile."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // LOAD PROFILE
  // =====================================================

  useEffect(() => {
    fetchProfile();
  }, []);

  // =====================================================
  // SET EDIT DATA
  // =====================================================

  const prepareEditData = (data) => {
    return {
      ngo_name: data?.ngo_name || "",
      description: data?.description || "",
      registration_no: data?.registration_no || "",
      email_id: data?.email_id || "",
      phone_no: data?.phone_no || "",
      website_link: data?.website_link || "",
      address: data?.address || "",
      city: data?.city || "",
      state: data?.state || "",
      pincode: data?.pincode || "",
      language: data?.language || "English",
    };
  };

  // =====================================================
  // EDIT
  // =====================================================

  const handleEdit = () => {
    setEditData(
      prepareEditData(profile)
    );

    setEditing(true);
  };

  // =====================================================
  // INPUT CHANGE
  // =====================================================

  const handleChange = (e) => {
    const {
      name,
      value,
    } = e.target;

    setEditData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  // =====================================================
  // CANCEL
  // =====================================================

  const handleCancel = () => {
    setEditData(
      prepareEditData(profile)
    );

    setEditing(false);
  };

  // =====================================================
  // SAVE
  // =====================================================

  const handleSave = async (e) => {
    e.preventDefault();

    // ---------------------------------------------------
    // VALIDATION
    // ---------------------------------------------------

    if (!editData.ngo_name.trim()) {
      alert("NGO name is required.");
      return;
    }

    if (!editData.email_id.trim()) {
      alert("Email is required.");
      return;
    }

    if (
      editData.phone_no &&
      !/^\d{10}$/.test(editData.phone_no)
    ) {
      alert(
        "Phone number must contain exactly 10 digits."
      );

      return;
    }

    if (
      editData.pincode &&
      !/^\d{6}$/.test(editData.pincode)
    ) {
      alert(
        "Pincode must contain exactly 6 digits."
      );

      return;
    }

    try {
      setSaving(true);

      /*
        IMPORTANT:
        This endpoint assumes your backend NGO
        detail URL is:

        /ngo/<id>/

        If your backend uses a different URL,
        only this URL needs to be changed.
      */

      const userId =
        profile?.id ||
        localStorage.getItem("user_id");

      if (!userId) {
        alert(
          "NGO ID not found. Please login again."
        );

        return;
      }

      console.log(
        "========== UPDATING NGO PROFILE =========="
      );

      console.log("NGO ID:", userId);
      console.log("Data:", editData);

      const response = await api.patch(
        `ngo/${userId}/`,
        editData
      );

      console.log(
        "NGO PROFILE UPDATED:",
        response.data
      );

      await fetchProfile();

      setEditing(false);

      alert(
        "NGO profile updated successfully! ✅"
      );

    } catch (error) {
      console.error(
        "========== NGO PROFILE UPDATE ERROR =========="
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

      if (error.response?.data) {
        alert(
          JSON.stringify(
            error.response.data
          )
        );
      } else {
        alert(
          "Unable to update NGO profile."
        );
      }

    } finally {
      setSaving(false);
    }
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="ngo-profile-page">

        <div className="ngo-profile-card">

          <div className="ngo-profile-loading">
            <div className="ngo-loading-spinner"></div>

            <h2>
              Loading NGO Profile...
            </h2>
          </div>

        </div>

      </div>
    );
  }

  // =====================================================
  // ERROR
  // =====================================================

  if (error) {
    return (
      <div className="ngo-profile-page">

        <div className="ngo-profile-card">

          <div className="ngo-profile-message">

            <div className="ngo-message-icon">
              ⚠️
            </div>

            <h2>
              Profile Error
            </h2>

            <p>
              {error}
            </p>

            <button
              className="ngo-refresh-button"
              onClick={fetchProfile}
            >
              Try Again
            </button>

          </div>

        </div>

      </div>
    );
  }

  // =====================================================
  // NO PROFILE
  // =====================================================

  if (!profile) {
    return (
      <div className="ngo-profile-page">

        <div className="ngo-profile-card">

          <div className="ngo-profile-message">

            <div className="ngo-message-icon">
              🏢
            </div>

            <h2>
              No NGO Profile Found
            </h2>

            <p>
              We couldn't find your organization profile.
            </p>

          </div>

        </div>

      </div>
    );
  }

  // =====================================================
  // STATUS
  // =====================================================

  const status = String(
    profile.status || "Pending"
  ).toLowerCase();

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="ngo-profile-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="ngo-profile-header">

        <button
          type="button"
          className="ngo-dashboard-back-button"
          onClick={() =>
            navigate("/ngo-dashboard")
          }
        >
          ← Back to Dashboard
        </button>

        <span className="ngo-profile-badge">
          NGO PROFILE
        </span>

        <h1>
          {profile.ngo_name || "NGO Profile"}
        </h1>

        <p>
          Manage and view your organization information.
        </p>

      </div>


      {/* =================================================
          PROFILE CARD
      ================================================= */}

      <div className="ngo-profile-card">

        {/* =================================================
            LOGO
        ================================================= */}

        <div className="ngo-logo-section">

          {profile.picture ? (

            <img
              src={profile.picture}
              alt={
                profile.ngo_name ||
                "NGO"
              }
              className="ngo-logo"
            />

          ) : (

            <div className="ngo-logo-placeholder">
              🏢
            </div>

          )}

        </div>


        {/* =================================================
            EDIT MODE
        ================================================= */}

        {editing ? (

          <form
            className="ngo-edit-form"
            onSubmit={handleSave}
          >

            {/* NGO NAME */}

            <div className="ngo-edit-group full-edit-field">

              <label>
                🏢 NGO Name
              </label>

              <input
                type="text"
                name="ngo_name"
                value={editData.ngo_name}
                onChange={handleChange}
                placeholder="Enter NGO name"
                required
              />

            </div>


            {/* DESCRIPTION */}

            <div className="ngo-edit-group full-edit-field">

              <label>
                📝 Description
              </label>

              <textarea
                name="description"
                value={editData.description}
                onChange={handleChange}
                placeholder="Describe your organization"
                rows="4"
              />

            </div>


            {/* REGISTRATION */}

            <div className="ngo-edit-group">

              <label>
                📋 Registration Number
              </label>

              <input
                type="text"
                name="registration_no"
                value={editData.registration_no}
                onChange={handleChange}
                placeholder="Registration number"
              />

            </div>


            {/* EMAIL */}

            <div className="ngo-edit-group">

              <label>
                📧 Email
              </label>

              <input
                type="email"
                name="email_id"
                value={editData.email_id}
                onChange={handleChange}
                placeholder="ngo@example.com"
                required
              />

            </div>


            {/* PHONE */}

            <div className="ngo-edit-group">

              <label>
                📞 Phone
              </label>

              <input
                type="tel"
                name="phone_no"
                value={editData.phone_no}
                onChange={handleChange}
                placeholder="10-digit number"
                maxLength="10"
              />

            </div>


            {/* WEBSITE */}

            <div className="ngo-edit-group">

              <label>
                🌐 Website
              </label>

              <input
                type="url"
                name="website_link"
                value={editData.website_link}
                onChange={handleChange}
                placeholder="https://example.org"
              />

            </div>


            {/* ADDRESS */}

            <div className="ngo-edit-group full-edit-field">

              <label>
                📍 Address
              </label>

              <textarea
                name="address"
                value={editData.address}
                onChange={handleChange}
                placeholder="Organization address"
                rows="3"
              />

            </div>


            {/* CITY */}

            <div className="ngo-edit-group">

              <label>
                🏙️ City
              </label>

              <input
                type="text"
                name="city"
                value={editData.city}
                onChange={handleChange}
                placeholder="City"
              />

            </div>


            {/* STATE */}

            <div className="ngo-edit-group">

              <label>
                🌎 State
              </label>

              <input
                type="text"
                name="state"
                value={editData.state}
                onChange={handleChange}
                placeholder="State"
              />

            </div>


            {/* PINCODE */}

            <div className="ngo-edit-group">

              <label>
                📮 Pincode
              </label>

              <input
                type="text"
                name="pincode"
                value={editData.pincode}
                onChange={handleChange}
                placeholder="6-digit pincode"
                maxLength="6"
              />

            </div>


            {/* LANGUAGE */}

            <div className="ngo-edit-group">

              <label>
                🗣️ Language
              </label>

              <select
                name="language"
                value={editData.language}
                onChange={handleChange}
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


            {/* EDIT ACTIONS */}

            <div className="ngo-edit-actions">

              <button
                type="button"
                className="ngo-cancel-button"
                onClick={handleCancel}
                disabled={saving}
              >
                Cancel
              </button>

              <button
                type="submit"
                className="ngo-save-button"
                disabled={saving}
              >

                {saving ? (
                  <>
                    <span className="ngo-small-spinner"></span>
                    Saving...
                  </>
                ) : (
                  <>
                    💾 Save Changes
                  </>
                )}

              </button>

            </div>

          </form>

        ) : (

          <>
            {/* =================================================
                VIEW MODE
            ================================================= */}

            <div className="ngo-profile-field">

              <strong>
                🏢 NGO Name
              </strong>

              <span>
                {profile.ngo_name || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                📝 Description
              </strong>

              <span>
                {profile.description || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                📋 Registration Number
              </strong>

              <span>
                {profile.registration_no || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                📧 Email
              </strong>

              <span>
                {profile.email_id || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                📞 Phone
              </strong>

              <span>
                {profile.phone_no || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                🌐 Website
              </strong>

              <span>
                {profile.website_link || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                📍 Address
              </strong>

              <span>
                {profile.address || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                🏙️ City
              </strong>

              <span>
                {profile.city || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                🌎 State
              </strong>

              <span>
                {profile.state || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                📮 Pincode
              </strong>

              <span>
                {profile.pincode || "-"}
              </span>

            </div>


            <div className="ngo-profile-field">

              <strong>
                🗣️ Language
              </strong>

              <span>
                {profile.language || "-"}
              </span>

            </div>


            {/* STATUS */}

            <div className="ngo-profile-field">

              <strong>
                🔐 Verification Status
              </strong>

              <span
                className={
                  `ngo-status ngo-status-${status}`
                }
              >
                {profile.status || "Pending"}
              </span>

            </div>


            {/* CERTIFICATE */}

            <div className="ngo-certificate-section">

              <h3>
                📄 NGO Certificate
              </h3>

              {profile.certificate_files ? (

                <a
                  href={profile.certificate_files}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="certificate-button"
                >
                  📄 View Certificate
                </a>

              ) : (

                <p>
                  Certificate not available.
                </p>

              )}

            </div>


            {/* PROFILE ACTIONS */}

            <div className="ngo-profile-actions">

              <button
                type="button"
                className="ngo-edit-button"
                onClick={handleEdit}
              >
                ✏️ Edit Profile
              </button>

              <button
                type="button"
                className="ngo-refresh-button"
                onClick={fetchProfile}
              >
                🔄 Refresh Profile
              </button>

            </div>

          </>

        )}

      </div>

    </div>
  );
}

export default NGOProfile;