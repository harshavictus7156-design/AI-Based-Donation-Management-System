import { useNavigate } from "react-router-dom";
import "./RegisterChoice.css";

function RegisterChoice() {
  const navigate = useNavigate();

  return (
    <div className="register-choice-page">

      <div className="register-choice-container">

        {/* HERO SECTION */}
        <div className="register-hero">

          <span className="register-badge">
            MAKE A DIFFERENCE
          </span>

          <h1>
            Give More. <span>Waste Less.</span>
            <br />
            Make an Impact.
          </h1>

          <p>
            Donate useful items to people and communities who need them.
            Connect with trusted NGOs and turn unused things into meaningful help.
          </p>

          <div className="register-action-buttons">

  <button
    className="get-started-button"
    onClick={() => navigate("/register/donor")}
  >
    Get Started
    <span>→</span>
  </button>

  <button
  className="explore-ngo-button"
  onClick={() => navigate("/explore-ngos")}
 >
  Explore NGOs
  <span>→</span>
 </button>

 </div>

        </div>

        {/* FEATURES */}
        <div className="register-features">

          <div className="feature-card">

            <div className="feature-icon">
              📦
            </div>

            <h3>Give Items</h3>

            <p>
              Donate clothes, books, food, electronics and other useful
              essentials instead of letting them go to waste.
            </p>

          </div>


          <div className="feature-card">

            <div className="feature-icon">
              🤝
            </div>

            <h3>Connect</h3>

            <p>
              Connect with NGOs that need specific items and make your
              contribution reach the right people.
            </p>

          </div>


          <div className="feature-card">

            <div className="feature-icon">
              🌱
            </div>

            <h3>Create Impact</h3>

            <p>
              Give unused items a second life while supporting communities
              and reducing unnecessary waste.
            </p>

          </div>

        </div>


        {/* HOW IT WORKS */}
        <div className="how-it-works">

          <h2>How It Works</h2>

          <p className="section-description">
            Making a difference takes only a few simple steps.
          </p>

          <div className="steps">

            <div className="step">

              <div className="step-number">
                01
              </div>

              <h3>Create Account</h3>

              <p>
                Register as a donor or NGO.
              </p>

            </div>


            <div className="step">

              <div className="step-number">
                02
              </div>

              <h3>Donate Items</h3>

              <p>
                Choose useful items you want to donate.
              </p>

            </div>


            <div className="step">

              <div className="step-number">
                03
              </div>

              <h3>Make an Impact</h3>

              <p>
                Help NGOs deliver support where it is needed.
              </p>

            </div>

          </div>

        </div>


        {/* LOGIN */}
        <div className="login-section">

          <p>
            Already have an account?
          </p>

          <button
            className="login-button"
            onClick={() => navigate("/login")}
          >
            Login to Your Account
          </button>

        </div>

      </div>

    </div>
  );
}

export default RegisterChoice;