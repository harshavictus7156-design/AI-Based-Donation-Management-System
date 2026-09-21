import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../services/api";
import "./NGODetails.css";

function NGODetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [ngo, setNgo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchNGO = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(`ngo/${id}/`);

        setNgo(response.data);
      } catch (err) {
        console.error("Error fetching NGO details:", err);

        setError(
          err.response?.data?.detail ||
          "Unable to load NGO details."
        );
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchNGO();
    }
  }, [id]);

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="ngo-details-page">
        <div className="ngo-details-message">
          Loading NGO details...
        </div>
      </div>
    );
  }

  // =====================================================
  // ERROR
  // =====================================================

  if (error || !ngo) {
    return (
      <div className="ngo-details-page">

        <div className="ngo-details-message error">
          {error || "NGO not found."}
        </div>

        <button
          className="ngo-back-button"
          onClick={() => navigate("/explore-ngos")}
        >
          ← Back to Explore NGOs
        </button>

      </div>
    );
  }

  // =====================================================
  // NGO DETAILS
  // =====================================================

  return (
    <div className="ngo-details-page">

      <div className="ngo-details-container">

        {/* =================================================
            BACK BUTTON
        ================================================= */}

        <button
          className="ngo-back-button"
          onClick={() => navigate("/explore-ngos")}
        >
          ← Back to Explore NGOs
        </button>


        {/* =================================================
            NGO HEADER
        ================================================= */}

        <div className="ngo-details-header">

          <div className="ngo-details-image">

            {ngo.picture ? (
              <img
                src={ngo.picture}
                alt={ngo.ngo_name || "NGO"}
              />
            ) : (
              <div className="ngo-placeholder-logo">
                🤝
              </div>
            )}

          </div>


          <div className="ngo-details-title">

            <span className="ngo-details-badge">
              VERIFIED NGO
            </span>

            <h1>
              {ngo.ngo_name || "NGO"}
            </h1>

            <p>
              {ngo.description ||
                "This organization is working towards meaningful community support and social impact."}
            </p>

            {ngo.status && (
              <div className="ngo-status">
                Status:{" "}
                <strong>{ngo.status}</strong>
              </div>
            )}

          </div>

        </div>


        {/* =================================================
            ORGANIZATION INFORMATION
        ================================================= */}

        <div className="ngo-details-section">

          <h2>
            Organization Information
          </h2>

          <div className="ngo-details-grid">

            {/* NGO NAME */}

            <div className="ngo-detail-item">
              <span className="ngo-detail-label">
                NGO Name
              </span>

              <span className="ngo-detail-value">
                {ngo.ngo_name || "Not provided"}
              </span>
            </div>


            {/* DESCRIPTION */}

            <div className="ngo-detail-item full-width">
              <span className="ngo-detail-label">
                Organization Description
              </span>

              <span className="ngo-detail-value">
                {ngo.description || "Not provided"}
              </span>
            </div>


            {/* REGISTRATION NUMBER */}

            <div className="ngo-detail-item">
              <span className="ngo-detail-label">
                Registration Number
              </span>

              <span className="ngo-detail-value">
                {ngo.registration_no || "Not provided"}
              </span>
            </div>


            {/* STATUS */}

            <div className="ngo-detail-item">
              <span className="ngo-detail-label">
                Verification Status
              </span>

              <span className="ngo-detail-value">
                {ngo.status || "Not provided"}
              </span>
            </div>

          </div>

        </div>


        {/* =================================================
            CONTACT INFORMATION
        ================================================= */}

        <div className="ngo-details-section">

          <h2>
            Contact Information
          </h2>

          <div className="ngo-details-grid">

            {/* EMAIL */}

            <div className="ngo-detail-item">

              <span className="ngo-detail-label">
                Email
              </span>

              {ngo.email_id ? (
                <a
                  className="ngo-detail-link"
                  href={`mailto:${ngo.email_id}`}
                >
                  {ngo.email_id}
                </a>
              ) : (
                <span className="ngo-detail-value">
                  Not provided
                </span>
              )}

            </div>


            {/* PHONE */}

            <div className="ngo-detail-item">

              <span className="ngo-detail-label">
                Phone Number
              </span>

              {ngo.phone_no ? (
                <a
                  className="ngo-detail-link"
                  href={`tel:${ngo.phone_no}`}
                >
                  {ngo.phone_no}
                </a>
              ) : (
                <span className="ngo-detail-value">
                  Not provided
                </span>
              )}

            </div>


            {/* WEBSITE */}

            <div className="ngo-detail-item full-width">

              <span className="ngo-detail-label">
                Website
              </span>

              {ngo.website_link ? (
                <a
                  className="ngo-detail-link"
                  href={
                    ngo.website_link.startsWith("http")
                      ? ngo.website_link
                      : `https://${ngo.website_link}`
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {ngo.website_link}
                </a>
              ) : (
                <span className="ngo-detail-value">
                  Not provided
                </span>
              )}

            </div>

          </div>

        </div>


        {/* =================================================
            LOCATION INFORMATION
        ================================================= */}

        <div className="ngo-details-section">

          <h2>
            Organization Location
          </h2>

          <div className="ngo-details-grid">

            {/* ADDRESS */}

            <div className="ngo-detail-item full-width">

              <span className="ngo-detail-label">
                Address
              </span>

              <span className="ngo-detail-value">
                {ngo.address || "Not provided"}
              </span>

            </div>


            {/* CITY */}

            <div className="ngo-detail-item">

              <span className="ngo-detail-label">
                City
              </span>

              <span className="ngo-detail-value">
                {ngo.city || "Not provided"}
              </span>

            </div>


            {/* STATE */}

            <div className="ngo-detail-item">

              <span className="ngo-detail-label">
                State
              </span>

              <span className="ngo-detail-value">
                {ngo.state || "Not provided"}
              </span>

            </div>


            {/* PINCODE */}

            <div className="ngo-detail-item">

              <span className="ngo-detail-label">
                Pin Code
              </span>

              <span className="ngo-detail-value">
                {ngo.pincode || "Not provided"}
              </span>

            </div>


            {/* LANGUAGE */}

            <div className="ngo-detail-item">

              <span className="ngo-detail-label">
                Preferred Language
              </span>

              <span className="ngo-detail-value">
                {ngo.language || "Not provided"}
              </span>

            </div>

          </div>

        </div>


        {/* =================================================
            NGO CERTIFICATE
        ================================================= */}

        <div className="ngo-details-section">

          <h2>
            Verification Certificate
          </h2>

          {ngo.certificate_files ? (

            <div className="ngo-certificate-box">

              <div>
                <span className="certificate-icon">
                  📄
                </span>

                <span>
                  NGO Registration Certificate
                </span>
              </div>

              <a
                href={ngo.certificate_files}
                target="_blank"
                rel="noopener noreferrer"
                className="certificate-button"
              >
                View Certificate
              </a>

            </div>

          ) : (

            <div className="ngo-no-certificate">
              Certificate information is not available.
            </div>

          )}

        </div>


        {/* =================================================
            ACTION SECTION
        ================================================= */}

        <div className="ngo-details-actions">

          <button
            className="ngo-view-button ngo-donate-button"
            onClick={() => navigate("/donate-item")}
          >
            Donate to this NGO
          </button>

          <button
            className="ngo-primary-button"
            onClick={() => navigate("/explore-ngos")}
          >
            ← Explore Other NGOs
          </button>

          <button
            className="ngo-secondary-button"
            onClick={() => navigate("/register/ngo")}
          >
            Register Your NGO
          </button>

        </div>

      </div>

    </div>
  );
}

export default NGODetails;