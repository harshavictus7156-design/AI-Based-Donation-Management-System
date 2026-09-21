// ============================================================
// EDIT DONATION
// ------------------------------------------------------------
// Only pickup information can be modified while the donation
// is still Pending.
//
// Editable:
//   • Pickup Address
//   • Pickup Date
//   • Pickup Time
//   • Pickup Notes
//
// The actual donation details are intentionally not displayed
// or editable from this page.
// ============================================================

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../../services/api";

import "./EditDonation.css";


// ============================================================
// HELPER FUNCTIONS
// ============================================================

const getPickupValue = (...values) => {
  const value = values.find(
    (item) =>
      item !== undefined &&
      item !== null &&
      item !== ""
  );

  return value ?? "";
};


const formatDateForInput = (value) => {
  if (!value) {
    return "";
  }

  // Already in YYYY-MM-DD format.
  if (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}$/.test(value)
  ) {
    return value;
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  const year = date.getFullYear();
  const month = String(
    date.getMonth() + 1
  ).padStart(2, "0");

  const day = String(
    date.getDate()
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
};


const formatTimeForInput = (value) => {
  if (!value) {
    return "";
  }

  /*
   * Handles:
   * 10:30
   * 10:30:00
   * 10:30 AM
   * 10:30:00 AM
   */

  const stringValue = String(value).trim();

  const timeMatch = stringValue.match(
    /^(\d{1,2}):(\d{2})(?::\d{2})?\s*(AM|PM)?$/i
  );

  if (!timeMatch) {
    return "";
  }

  let hours = Number(timeMatch[1]);
  const minutes = timeMatch[2];
  const period = timeMatch[3]?.toUpperCase();

  if (period === "PM" && hours !== 12) {
    hours += 12;
  }

  if (period === "AM" && hours === 12) {
    hours = 0;
  }

  return `${String(hours).padStart(2, "0")}:${minutes}`;
};


// ============================================================
// COMPONENT
// ============================================================

function EditDonation() {
  const navigate = useNavigate();
  const { id } = useParams();


  // ----------------------------------------------------------
  // Pickup Form
  // ----------------------------------------------------------

  const [formData, setFormData] = useState({
    location: "",
    pickup_date: "",
    pickup_time: "",
    pickup_notes: "",
  });


  // ----------------------------------------------------------
  // Donation Status
  // ----------------------------------------------------------

  const [status, setStatus] = useState("Pending");


  // ----------------------------------------------------------
  // UI State
  // ----------------------------------------------------------

  const [loading, setLoading] = useState(true);

  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");


  // ==========================================================
  // LOAD DONATION
  // ==========================================================

  useEffect(() => {
    const fetchDonation = async () => {
      try {
        setLoading(true);
        setError("");


        const response = await api.get(
          `donation/${id}/`
        );

        const donation = response.data;


        // ------------------------------------------------------
        // Check Donation Status
        // ------------------------------------------------------

        const currentStatus = String(
          donation.status || "Pending"
        ).trim();

        setStatus(currentStatus);


        // ------------------------------------------------------
        // Only Pending Donations Can Be Edited
        // ------------------------------------------------------

        if (
          currentStatus.toLowerCase() !==
          "pending"
        ) {
          setError(
            "This donation can no longer be edited because it has already been processed."
          );

          return;
        }


        // ------------------------------------------------------
        // Pickup Object
        // ------------------------------------------------------

        const pickup =
          donation.pickup ||
          donation.pickup_details ||
          {};


        // ------------------------------------------------------
        // Load Existing Pickup Information
        // ------------------------------------------------------

        setFormData({
          location: getPickupValue(
            donation.location,
            donation.pickup_location,
            donation.address,
            pickup.location,
            pickup.address,
            pickup.pickup_address
          ),

          pickup_date: formatDateForInput(
            getPickupValue(
              donation.pickup_date,
              donation.scheduled_date,
              pickup.pickup_date,
              pickup.scheduled_date
            )
          ),

          pickup_time: formatTimeForInput(
            getPickupValue(
              donation.pickup_time,
              donation.scheduled_time,
              pickup.pickup_time,
              pickup.scheduled_time,
              pickup.time
            )
          ),

          pickup_notes: getPickupValue(
            donation.pickup_notes,
            donation.pickup_note,
            pickup.pickup_notes,
            pickup.notes
          ),
        });

      } catch (err) {
        console.error(
          "EDIT DONATION FETCH ERROR:",
          err.response?.data || err
        );

        setError(
          err.response?.data?.detail ||
            err.response?.data?.message ||
            "Unable to load donation details."
        );

      } finally {
        setLoading(false);
      }
    };


    if (id) {
      fetchDonation();
    } else {
      setLoading(false);
      setError("Donation ID is missing.");
    }
  }, [id]);


  // ==========================================================
  // HANDLE INPUT
  // ==========================================================

  const handleChange = (event) => {
    const {
      name,
      value,
    } = event.target;


    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));


    // Clear previous error when user starts correcting input.
    if (error) {
      setError("");
    }
  };


  // ==========================================================
  // SAVE PICKUP DETAILS
  // ==========================================================

  const handleSubmit = async (event) => {
    event.preventDefault();


    // --------------------------------------------------------
    // Validation
    // --------------------------------------------------------

    if (!formData.location.trim()) {
      setError(
        "Please enter the pickup address."
      );

      return;
    }


    if (!formData.pickup_date) {
      setError(
        "Please select a pickup date."
      );

      return;
    }


    if (!formData.pickup_time) {
      setError(
        "Please select a pickup time."
      );

      return;
    }


    // Prevent selecting a past date.
    const selectedDate = new Date(
      `${formData.pickup_date}T${formData.pickup_time}`
    );

    if (
      !Number.isNaN(selectedDate.getTime()) &&
      selectedDate < new Date()
    ) {
      setError(
        "Pickup date and time cannot be in the past."
      );

      return;
    }


    try {
      setSaving(true);
      setError("");


      // ------------------------------------------------------
      // Update ONLY pickup information
      // ------------------------------------------------------

      await api.patch(
        `donation/${id}/`,
        {
          location:
            formData.location.trim(),

          pickup_date:
            formData.pickup_date,

          pickup_time:
            formData.pickup_time,

          pickup_notes:
            formData.pickup_notes.trim(),
        }
      );


      // ------------------------------------------------------
      // Success
      // ------------------------------------------------------

      alert(
        "Pickup details updated successfully."
      );


      navigate("/my-donations");

    } catch (err) {
      console.error(
        "EDIT DONATION ERROR:",
        err.response?.data || err
      );


      setError(
        err.response?.data?.detail ||
          err.response?.data?.message ||
          "Unable to update pickup details."
      );

    } finally {
      setSaving(false);
    }
  };


  // ==========================================================
  // LOADING STATE
  // ==========================================================

  if (loading) {
    return (
      <div className="edit-donation-page">

        <div className="edit-donation-loading">

          <div className="loading-icon">
            🚚
          </div>

          <h2>
            Loading pickup details...
          </h2>

          <p>
            Please wait while we load your donation.
          </p>

        </div>

      </div>
    );
  }


  // ==========================================================
  // NON-PENDING DONATION
  // ==========================================================

  if (
    status.toLowerCase() !==
    "pending"
  ) {
    return (
      <div className="edit-donation-page">

        <div className="edit-donation-error">

          <div className="error-icon">
            🔒
          </div>

          <h2>
            Donation cannot be edited
          </h2>

          <p>
            {error ||
              "This donation has already been processed and its pickup details can no longer be changed."}
          </p>


          <button
            type="button"
            className="edit-back-button"
            onClick={() =>
              navigate("/my-donations")
            }
          >
            ← Back to My Donations
          </button>

        </div>

      </div>
    );
  }


  // ==========================================================
  // MAIN PAGE
  // ==========================================================

  return (
    <div className="edit-donation-page">

      {/* ======================================================
          PAGE HEADER
          ====================================================== */}

      <div className="edit-donation-header">

        <span className="edit-donation-badge">
          DONOR DASHBOARD
        </span>

        <h1>
          Edit Pickup Details
        </h1>

        <p>
          Update when and where your donation
          should be picked up.
        </p>

      </div>


      {/* ======================================================
          ERROR MESSAGE
          ====================================================== */}

      {error && (
        <div className="edit-donation-error inline-error">
          <span>
            ⚠️
          </span>

          <p>
            {error}
          </p>
        </div>
      )}


      {/* ======================================================
          PICKUP FORM
          ====================================================== */}

      <form
        className="edit-donation-form"
        onSubmit={handleSubmit}
      >

        <div className="edit-donation-card">

          {/* --------------------------------------------------
              CARD HEADER
              -------------------------------------------------- */}

          <div className="card-heading">

            <div className="heading-icon">
              🚚
            </div>

            <div>

              <span>
                PICKUP DETAILS
              </span>

              <h2>
                Update your pickup
              </h2>

            </div>

          </div>


          {/* --------------------------------------------------
              PICKUP ADDRESS
              -------------------------------------------------- */}

          <div className="form-group">

            <label htmlFor="pickup-location">
              Pickup Address
            </label>

            <div className="pickup-address-input">

              <span
                className="pickup-field-icon"
                aria-hidden="true"
              >
                📍
              </span>

              <input
                id="pickup-location"
                type="text"
                name="location"
                value={formData.location}
                onChange={handleChange}
                placeholder="Enter pickup address"
                autoComplete="street-address"
                required
              />

            </div>

          </div>


          {/* --------------------------------------------------
              PICKUP DATE & TIME
              -------------------------------------------------- */}

          <div className="pickup-date-time-grid">

            {/* Pickup Date */}

            <div className="form-group pickup-field">

              <label htmlFor="pickup-date">
                Pickup Date
              </label>

              <div className="pickup-date-input">

                <input
                  id="pickup-date"
                  type="date"
                  name="pickup_date"
                  value={formData.pickup_date}
                  onChange={handleChange}
                  required
                />

              </div>

            </div>


            {/* Pickup Time */}

            <div className="form-group pickup-field">

              <label htmlFor="pickup-time">
                Pickup Time
              </label>

              <div className="pickup-time-input">

                <input
                  id="pickup-time"
                  type="time"
                  name="pickup_time"
                  value={formData.pickup_time}
                  onChange={handleChange}
                  required
                />

              </div>

            </div>

          </div>


          {/* --------------------------------------------------
              PICKUP NOTES
              -------------------------------------------------- */}

          <div className="form-group pickup-notes-group">

            <label htmlFor="pickup-notes">
              Pickup Notes
            </label>

            <textarea
              id="pickup-notes"
              name="pickup_notes"
              rows="4"
              value={formData.pickup_notes}
              onChange={handleChange}
              placeholder="Add any instructions for pickup..."
            />

          </div>


          {/* --------------------------------------------------
              INFORMATION NOTE
              -------------------------------------------------- */}

          <div className="edit-pickup-note">

            <strong>
              💡 Pickup details only
            </strong>

            <p>
              Your donation details remain unchanged.
              You can update only the pickup address,
              date, time and notes while the donation
              is pending.
            </p>

          </div>

        </div>


        {/* ====================================================
            ACTION BUTTONS
            ==================================================== */}

        <div className="edit-donation-actions">

          <button
            type="button"
            className="edit-cancel-button"
            onClick={() =>
              navigate("/my-donations")
            }
            disabled={saving}
          >
            Cancel
          </button>


          <button
            type="submit"
            className="edit-save-button"
            disabled={saving}
          >
            {saving
              ? "Saving..."
              : "Save Pickup Details"}
          </button>

        </div>

      </form>

    </div>
  );
}


export default EditDonation;