import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./ExploreNGOs.css";

function ExploreNGOs() {
  const navigate = useNavigate();

  const [ngos, setNgos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchNGOs = async () => {
      try {
        const response = await api.get("ngos/");

        setNgos(
          Array.isArray(response.data)
            ? response.data
            : response.data.results || []
        );
      } catch (err) {
        console.error("Error fetching NGOs:", err);
        setError("Unable to load NGOs. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchNGOs();
  }, []);

  return (
    <div className="explore-ngos-page">

      <div className="explore-ngos-container">

        <div className="explore-ngos-header">
          <span className="explore-badge">
            OUR NGO PARTNERS
          </span>

          <h1>
            Explore <span>NGOs</span>
          </h1>

          <p>
            Discover trusted organizations working to create meaningful
            impact in communities.
          </p>
        </div>

        {loading && (
          <div className="explore-message">
            Loading NGOs...
          </div>
        )}

        {error && (
          <div className="explore-message error">
            {error}
          </div>
        )}

        {!loading && !error && ngos.length === 0 && (
          <div className="explore-message">
            No NGOs are currently available.
          </div>
        )}

        {!loading && !error && ngos.length > 0 && (
          <div className="ngo-grid">

            {ngos.map((ngo) => (
              <div className="ngo-card" key={ngo.id}>

                <div className="ngo-card-logo">
                  {ngo.logo ? (
                    <img
                      src={ngo.logo}
                      alt={ngo.ngo_name || "NGO"}
                    />
                  ) : (
                    <span>🤝</span>
                  )}
                </div>

                <div className="ngo-card-content">

                  <h2>
                    {ngo.ngo_name || ngo.name || "NGO"}
                  </h2>

                  <p className="ngo-description">
                    {ngo.description ||
                      ngo.ngo_description ||
                      "Working towards meaningful community support and social impact."}
                  </p>

                  <div className="ngo-details">

                    {(ngo.city || ngo.state) && (
                      <p>
                        📍 {ngo.city || ""}
                        {ngo.city && ngo.state ? ", " : ""}
                        {ngo.state || ""}
                      </p>
                    )}

                    {ngo.email && (
                      <p>
                        ✉️ {ngo.email}
                      </p>
                    )}

                    {ngo.phone && (
                      <p>
                        📞 {ngo.phone}
                      </p>
                    )}

                  </div>

                  <button
                    className="ngo-view-button"
                    onClick={() =>
                      navigate(`/ngo-details/${ngo.id}`)
                    }
                  >
                    View NGO
                    <span>→</span>
                  </button>

                </div>

              </div>
            ))}

          </div>
        )}

        <div className="explore-ngos-bottom">
          <p>Want to register your organization?</p>

          <button
            onClick={() => navigate("/register/ngo")}
          >
            Register your NGO
          </button>
        </div>

      </div>

    </div>
  );
}

export default ExploreNGOs;