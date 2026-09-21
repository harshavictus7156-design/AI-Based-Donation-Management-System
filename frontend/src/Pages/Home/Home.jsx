import { useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../../components/Navbar/Navbar";
import "./Home.css";

function Home() {

  const [showDonateChoice, setShowDonateChoice] =
    useState(false);

  const [showNGOChoice, setShowNGOChoice] =
    useState(false);


  // =====================================================
  // DONOR BUTTON
  // =====================================================

  const handleDonateClick = () => {
    setShowDonateChoice(true);
  };


  // =====================================================
  // NGO BUTTON
  // =====================================================

  const handleNGOClick = () => {
    setShowNGOChoice(true);
  };


  return (
    <div className="home-page">


      {/* =================================================
          HERO
      ================================================= */}

      <section className="home-hero">

        <div className="home-hero-content">

          <div className="home-eyebrow">
            AI-POWERED DONATION PLATFORM
          </div>


          <h1>
            Give what matters.
            <br />
            <span>Reach who needs it.</span>
          </h1>


          <p>
            Connect meaningful donations with trusted NGOs
            through intelligent matching, transparent tracking,
            and a platform built around real-world impact.
          </p>


          {/* =================================================
              HERO BUTTONS
          ================================================= */}

          <div className="home-hero-buttons">


            {/* DONATE */}

            <button
              type="button"
              className="home-primary-btn"
              onClick={handleDonateClick}
            >
              Donate an Item
              <span>→</span>
            </button>


            {/* NGO */}

            <button
              type="button"
              className="home-secondary-btn"
              onClick={handleNGOClick}
            >
              Register your NGO
            </button>


          </div>


          <div className="home-trust-line">
            <span>✓</span>
            Built for donors and verified NGOs
          </div>

        </div>


        {/* =================================================
            HERO VISUAL
        ================================================= */}

        <div className="home-hero-visual">

          <div className="hero-orbit orbit-one"></div>

          <div className="hero-orbit orbit-two"></div>


          <div className="hero-impact-card">

            <div className="impact-card-top">

              <span>
                LIVE IMPACT
              </span>

              <span className="impact-dot"></span>

            </div>


            <div className="impact-main-icon">
              ♡
            </div>


            <h3>
              Every donation
              <br />
              can create a ripple.
            </h3>


            <p>
              From a donor's hands to
              an organization that needs it.
            </p>


            <div className="impact-mini-stats">

              <div>
                <strong>
                  1K+
                </strong>

                <span>
                  Donations
                </span>
              </div>


              <div>
                <strong>
                  50+
                </strong>

                <span>
                  NGOs
                </span>
              </div>


              <div>
                <strong>
                  100+
                </strong>

                <span>
                  Donors
                </span>
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =================================================
          INTRO
      ================================================= */}

      <section className="home-intro">

        <div className="home-section-label">
          WHY THIS PLATFORM
        </div>


        <h2>
          Turning generosity into
          <span>
            {" "}meaningful action.
          </span>
        </h2>


        <p>
          Finding the right place for a donation should not
          be complicated. Our platform brings donors and NGOs
          together through a simple, transparent and intelligent
          experience.
        </p>

      </section>


      {/* =================================================
          FEATURES
      ================================================= */}

      <section className="home-features">


        <div className="home-feature-card">

          <div className="feature-number">
            01
          </div>

          <div className="feature-icon">
            ✦
          </div>

          <h3>
            AI Matching
          </h3>

          <p>
            Intelligent matching helps connect your donated
            items with NGOs based on their needs.
          </p>

          <span className="feature-arrow">
            →
          </span>

        </div>


        <div className="home-feature-card">

          <div className="feature-number">
            02
          </div>

          <div className="feature-icon">
            ◈
          </div>

          <h3>
            Secure Donations
          </h3>

          <p>
            Your account and donation information are handled
            through secure authentication and verification.
          </p>

          <span className="feature-arrow">
            →
          </span>

        </div>


        <div className="home-feature-card">

          <div className="feature-number">
            03
          </div>

          <div className="feature-icon">
            ◎
          </div>

          <h3>
            Transparent Tracking
          </h3>

          <p>
            Follow your donations and stay informed about
            their progress from submission to collection.
          </p>

          <span className="feature-arrow">
            →
          </span>

        </div>

      </section>


      {/* =================================================
          IMPACT
      ================================================= */}

      <section className="home-impact">

        <div className="home-impact-content">

          <div className="home-section-label light-label">
            OUR IMPACT
          </div>


          <h2>
            Small contributions.
            <br />
            Bigger possibilities.
          </h2>


          <p>
            Every item donated through the platform represents
            something useful that can reach another person,
            organization, or community.
          </p>

        </div>


        <div className="home-impact-stats">

          <div className="home-impact-stat">

            <strong>
              100+
            </strong>

            <span>
              Donors
            </span>

          </div>


          <div className="home-impact-stat">

            <strong>
              50+
            </strong>

            <span>
              NGOs
            </span>

          </div>


          <div className="home-impact-stat">

            <strong>
              1000+
            </strong>

            <span>
              Donations
            </span>

          </div>

        </div>

      </section>


      {/* =================================================
          HOW IT WORKS
      ================================================= */}

      <section className="home-how">

        <div className="home-section-heading">

          <div className="home-section-label">
            HOW IT WORKS
          </div>


          <h2>
            Three steps.
            <br />
            One meaningful journey.
          </h2>

        </div>


        <div className="home-steps">


          <div className="home-step">

            <div className="step-circle">
              01
            </div>

            <h3>
              Donate
            </h3>

            <p>
              Tell us what you would like
              to give and submit your donation.
            </p>

          </div>


          <div className="home-step-line"></div>


          <div className="home-step">

            <div className="step-circle">
              02
            </div>

            <h3>
              Match
            </h3>

            <p>
              Our platform helps connect the
              donation with a suitable NGO.
            </p>

          </div>


          <div className="home-step-line"></div>


          <div className="home-step">

            <div className="step-circle">
              03
            </div>

            <h3>
              Impact
            </h3>

            <p>
              Your donation reaches an organization
              where it can be genuinely useful.
            </p>

          </div>

        </div>

      </section>


      {/* =================================================
          FINAL CTA
      ================================================= */}

      <section className="home-final-cta">

        <div>

          <span>
            READY TO MAKE A DIFFERENCE?
          </span>


          <h2>
            Your unused item could
            <br />
            become someone else's opportunity.
          </h2>

        </div>


        <Link to="/register/donor">

          <button className="home-final-btn">

            Start Donating

            <span>
              →
            </span>

          </button>

        </Link>

      </section>


      {/* =================================================
          FOOTER
      ================================================= */}

      <footer className="home-footer">

        <div className="footer-brand">

          <div className="footer-logo">
            AI
          </div>


          <div>

            <strong>
              ResourceBridge
            </strong>

            <span>
              Technology with purpose.
            </span>

          </div>

        </div>


        <div className="footer-copy">
          © 2026 Donation Management System
        </div>

      </footer>


      {/* =================================================
          DONOR LOGIN / REGISTER CHOICE
      ================================================= */}

      {showDonateChoice && (

        <div
          className="home-donate-overlay"
          onClick={() =>
            setShowDonateChoice(false)
          }
        >

          <div
            className="home-donate-choice"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <button
              type="button"
              className="home-choice-close"
              onClick={() =>
                setShowDonateChoice(false)
              }
              aria-label="Close"
            >
              ×
            </button>


            <div className="home-choice-icon">
              📦
            </div>


            <span className="home-section-label">
              READY TO DONATE?
            </span>


            <h2>
              First, let's get you started.
            </h2>


            <p>
              Login if you already have an account,
              or create a donor account to continue
              with your donation.
            </p>


            <div className="home-choice-buttons">

              <Link
                to="/login"
                className="home-choice-login"
                onClick={() =>
                  setShowDonateChoice(false)
                }
              >
                Login
                <span>
                  →
                </span>
              </Link>


              <Link
                to="/register/donor"
                className="home-choice-register"
                onClick={() =>
                  setShowDonateChoice(false)
                }
              >
                Register as Donor
                <span>
                  →
                </span>
              </Link>

            </div>

          </div>

        </div>

      )}


      {/* =================================================
          NGO LOGIN / REGISTER CHOICE
      ================================================= */}

      {showNGOChoice && (

        <div
          className="home-donate-overlay"
          onClick={() =>
            setShowNGOChoice(false)
          }
        >

          <div
            className="home-donate-choice"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <button
              type="button"
              className="home-choice-close"
              onClick={() =>
                setShowNGOChoice(false)
              }
              aria-label="Close"
            >
              ×
            </button>


            <div className="home-choice-icon">
              🏢
            </div>


            <span className="home-section-label">
              JOIN AS AN NGO
            </span>


            <h2>
              First, let's get you started.
            </h2>


            <p>
              Login if your NGO already has an account,
              or register your organization to join
              the donation platform.
            </p>


            <div className="home-choice-buttons">

              <Link
                to="/login"
                className="home-choice-login"
                onClick={() =>
                  setShowNGOChoice(false)
                }
              >
                Login
                <span>
                  →
                </span>
              </Link>


              <Link
                to="/register/ngo"
                className="home-choice-register"
                onClick={() =>
                  setShowNGOChoice(false)
                }
              >
                Register as NGO
                <span>
                  →
                </span>
              </Link>

            </div>

          </div>

        </div>

      )}

    </div>
  );
}

export default Home;