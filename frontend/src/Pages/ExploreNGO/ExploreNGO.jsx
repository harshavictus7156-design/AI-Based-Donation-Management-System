import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./ExploreNGO.css";

function ExploreNGO() {
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
        console.error("Failed to fetch NGOs:", err);
        setError("Unable to load NGOs at the moment.");
      } finally {
        setLoading(false);
      }
    };

    fetchNGOs();
  }, []);

  return (
    <div className="explore-ngo-page">

      <section className="explore-ngo-hero">
        <span className="explore-ngo-badge">
          OUR NGO PARTNERS
        </span>

        <h1>
          Explore <span>NGOs</span>
        </h1>

        <p>
          Discover trusted NGOs working to create meaningful impact
          in communities and connect your donations with the right causes.
        </p>
      </section>

      <section className="ngo-list-section">

        <div className="ngo-list-header">
          <h2>Verified NGOs</h2>
          <p>
            Choose from organizations working on real community needs.
          </p>
        </div>

        {loading && (
          <div className="ngo-loading">
            Loading NGOs...
          </div>
        )}

        {error && (
          <div className="ngo-error">
            {error}
          </div>
        )}

        {!loading && !error && ngos.length === 0 && (
          <div className="ngo-empty">
            <h3>No NGOs available</h3>
            <p>
              There are currently no approved NGOs available to explore.
            </p>
          </div>
        )}

        {!loading && !error && ngos.length > 0 && (
          <div className="ngo-grid">

            {ngos.map((ngo) => (
              <div
                className="ngo-card"
                key={ngo.id}
              >

                <div className="ngo-card-icon">
                  🏢
                </div>

                <h3>
                  {ngo.ngo_name || ngo.name || "NGO"}
                </h3>

                <p className="ngo-description">
                  {ngo.description ||
                    "An organization working to support communities through meaningful initiatives."}
                </p>

                <div className="ngo-details">

                  {ngo.city && (
                    <span>
                      📍 {ngo.city}
                    </span>
                  )}

                  {ngo.state && (
                    <span>
                      🌎 {ngo.state}
                    </span>
                  )}

                </div>

              </div>
            ))}

          </div>
        )}

      </section>

      <section className="ngo-register-cta">

        <h2>Are you an NGO?</h2>

        <p>
          Join our platform and connect with donors who want to make
          a meaningful difference.
        </p>

        <button
          onClick={() => navigate("/register/ngo")}
        >
          Register Your NGO →
        </button>

      </section>

    </div>
  );
}

export default ExploreNGO;