import { useEffect, useState } from "react";
import api from "../../services/api";
import "./Profile.css";

function Profile() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const userType = localStorage.getItem("user_type");

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("profile/");

      console.log("Profile:", response.data);

      setProfile(response.data);
    } catch (error) {
      console.error("PROFILE ERROR:", error);
      console.error("Status:", error.response?.status);
      console.error("Response:", error.response?.data);

      setError(
        error.response?.data?.detail ||
        "Unable to load profile."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  // =====================================================
  // PROFILE IMAGE UPLOAD
  // =====================================================

  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.type.startsWith("image/")) {
      alert("Please select an image file.");
      return;
    }

    try {
      setUploading(true);

      const data = new FormData();

      data.append("picture", file);

      const response = await api.post(
        "profile/upload/",
        data,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      console.log(
        "Profile Image Uploaded:",
        response.data
      );

      alert("Profile image updated successfully! 📸");

      await fetchProfile();

    } catch (error) {
      console.error(
        "PROFILE IMAGE UPLOAD ERROR:",
        error
      );

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
          "Unable to upload profile image."
        );
      }

    } finally {
      setUploading(false);
    }
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="profile-page">

        <div className="profile-card">

          <h2>
            Loading Profile...
          </h2>

        </div>

      </div>
    );
  }

  // =====================================================
  // ERROR
  // =====================================================

  if (error) {
    return (
      <div className="profile-page">

        <div className="profile-card">

          <h2>
            ⚠️ Profile Error
          </h2>

          <p>
            {error}
          </p>

          <button onClick={fetchProfile}>
            Try Again
          </button>

        </div>

      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-page">

        <div className="profile-card">

          <h2>
            No Profile Found
          </h2>

        </div>

      </div>
    );
  }

  const isNGO =
    userType?.toLowerCase() === "ngo";

  return (
    <div className="profile-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="profile-header">

        <span className="profile-badge">
          {isNGO
            ? "NGO PROFILE"
            : "DONOR PROFILE"}
        </span>

        <h1>
          My Profile
        </h1>

        <p>
          View and manage your account information.
        </p>

      </div>


      {/* =================================================
          PROFILE CARD
      ================================================= */}

      <div className="profile-card">

        {/* =================================================
            PROFILE IMAGE
        ================================================= */}

        <div className="profile-image-section">

          {profile.picture ? (

            <img
              src={profile.picture}
              alt="Profile"
              className="profile-image"
            />

          ) : (

            <div className="profile-placeholder">
              👤
            </div>

          )}

        </div>


        {/* =================================================
            CHANGE PROFILE IMAGE
        ================================================= */}

        <div className="profile-upload-section">

          <label
            htmlFor="profile-picture"
            className="profile-upload-button"
          >
            {uploading
              ? "Uploading..."
              : "📸 Change Profile Picture"}
          </label>

          <input
            id="profile-picture"
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            disabled={uploading}
            className="profile-file-input"
          />

          <small>
            JPG, PNG or other image formats
          </small>

        </div>


        {/* =================================================
            NGO PROFILE
        ================================================= */}

        {isNGO ? (

          <>

            <div className="profile-field">
              <strong>🏢 NGO Name</strong>
              <span>
                {profile.ngo_name || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📧 Email</strong>
              <span>
                {profile.email_id || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📞 Phone</strong>
              <span>
                {profile.phone_no || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📋 Registration No.</strong>
              <span>
                {profile.registration_no || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📍 Address</strong>
              <span>
                {profile.address || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>🏙️ City</strong>
              <span>
                {profile.city || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>🌎 State</strong>
              <span>
                {profile.state || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📮 Pincode</strong>
              <span>
                {profile.pincode || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>✅ Status</strong>
              <span>
                {profile.status || "Pending"}
              </span>
            </div>

          </>

        ) : (

          /* =================================================
             DONOR PROFILE
          ================================================= */

          <>

            <div className="profile-field">
              <strong>👤 Name</strong>
              <span>
                {profile.name || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📧 Email</strong>
              <span>
                {profile.email || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📞 Phone</strong>
              <span>
                {profile.phone || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📍 Address</strong>
              <span>
                {profile.address || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>🏙️ City</strong>
              <span>
                {profile.city || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>🌎 State</strong>
              <span>
                {profile.state || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>📮 Pincode</strong>
              <span>
                {profile.pincode || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>🗣️ Language</strong>
              <span>
                {profile.language_preference || "-"}
              </span>
            </div>

            <div className="profile-field">
              <strong>✅ Account Status</strong>
              <span>
                {profile.status_active
                  ? "Active"
                  : "Inactive"}
              </span>
            </div>

          </>

        )}

      </div>

    </div>
  );
}

export default Profile;