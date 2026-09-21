// ============================================================
// DONOR SETTINGS
// Account | Notifications | Appearance | Security | Privacy
// ============================================================

// ------------------------------------------------------------
// Imports
// ------------------------------------------------------------

import {
  FiBell,
  FiMoon,
  FiSettings,
  FiShield,
  FiLock,
  FiUser
} from "react-icons/fi";

import ThemeToggle from "../../components/ThemeToggle/ThemeToggle";

import "./DonorNotifications.css";


// ============================================================
// DONOR SETTINGS COMPONENT
// ============================================================

function DonorSettings() {

  return (
    <div className="donor-settings-page">

      {/* ------------------------------------------------------
          PAGE HEADER
          ------------------------------------------------------ */}

      <header className="settings-header">

        <span className="settings-eyebrow">
          <FiSettings />
          ACCOUNT SETTINGS
        </span>

        <h1>Settings</h1>

        <p>
          Manage your account preferences, notifications,
          appearance, and security.
        </p>

      </header>


      {/* ======================================================
          SETTINGS CONTENT
          ====================================================== */}

      <div className="settings-content">


        {/* ----------------------------------------------------
            ACCOUNT
            ---------------------------------------------------- */}

        <section className="settings-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon coral">
              <FiUser />
            </div>

            <div>
              <span>ACCOUNT</span>
              <h2>Account</h2>
            </div>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiUser />
            </div>

            <div className="settings-row-content">

              <strong>Profile</strong>

              <p>
                Manage your personal donor information
                and account details.
              </p>

            </div>

            <button className="settings-action-button">
              Edit
            </button>

          </div>

        </section>


        {/* ----------------------------------------------------
            NOTIFICATIONS
            ---------------------------------------------------- */}

        <section className="settings-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon coral">
              <FiBell />
            </div>

            <div>
              <span>COMMUNICATION</span>
              <h2>Notifications</h2>
            </div>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiBell />
            </div>

            <div className="settings-row-content">

              <strong>Donation updates</strong>

              <p>
                Receive notifications when your donation
                status changes.
              </p>

            </div>

            <span className="settings-status active">
              ON
            </span>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiBell />
            </div>

            <div className="settings-row-content">

              <strong>Pickup reminders</strong>

              <p>
                Get reminders about scheduled donation
                pickups.
              </p>

            </div>

            <span className="settings-status active">
              ON
            </span>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiBell />
            </div>

            <div className="settings-row-content">

              <strong>NGO responses</strong>

              <p>
                Receive alerts when an NGO accepts or
                rejects your donation.
              </p>

            </div>

            <span className="settings-status active">
              ON
            </span>

          </div>

        </section>


        {/* ----------------------------------------------------
            APPEARANCE
            ---------------------------------------------------- */}

        <section className="settings-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon blue">
              <FiMoon />
            </div>

            <div>
              <span>INTERFACE</span>
              <h2>Appearance</h2>
            </div>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiMoon />
            </div>

            <div className="settings-row-content">

              <strong>Theme</strong>

              <p>
                Switch between light and dark mode.
              </p>

            </div>

            <ThemeToggle />

          </div>

        </section>


        {/* ----------------------------------------------------
            SECURITY
            ---------------------------------------------------- */}

        <section className="settings-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon green">
              <FiLock />
            </div>

            <div>
              <span>SECURITY</span>
              <h2>Security</h2>
            </div>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiLock />
            </div>

            <div className="settings-row-content">

              <strong>Password & Security</strong>

              <p>
                Manage your password and account security.
              </p>

            </div>

            <button className="settings-action-button">
              Manage
            </button>

          </div>

        </section>


        {/* ----------------------------------------------------
            PRIVACY
            ---------------------------------------------------- */}

        <section className="settings-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon green">
              <FiShield />
            </div>

            <div>
              <span>PRIVACY</span>
              <h2>Privacy</h2>
            </div>

          </div>


          <div className="settings-row">

            <div className="settings-row-icon">
              <FiShield />
            </div>

            <div className="settings-row-content">

              <strong>Account privacy</strong>

              <p>
                Your donor information is protected within
                your authenticated account.
              </p>

            </div>

            <span className="settings-status secure">
              SECURE
            </span>

          </div>

        </section>


        {/* ----------------------------------------------------
            ACCOUNT MANAGEMENT
            ---------------------------------------------------- */}

        <section className="settings-card settings-danger-card">

          <div className="settings-section-heading">

            <div className="settings-section-icon danger">
              <FiShield />
            </div>

            <div>
              <span>ACCOUNT</span>
              <h2>Account Management</h2>
            </div>

          </div>


          <div className="settings-row">

            <div className="settings-row-content">

              <strong>Account actions</strong>

              <p>
                Manage your account or sign out from
                your donor workspace.
              </p>

            </div>

            <button className="settings-logout-button">
              Logout
            </button>

          </div>

        </section>


      </div>

    </div>
  );
}


export default DonorSettings;