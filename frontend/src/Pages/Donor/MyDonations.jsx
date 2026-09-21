import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../../services/api";
import "./MyDonations.css";

function MyDonations() {
  const navigate = useNavigate();

  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // =====================================================
  // FETCH MY DONATIONS
  // =====================================================

  const fetchMyDonations = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("my-donations/");

      console.log("My Donations:", response.data);

      // Handle both array and possible paginated response
      if (Array.isArray(response.data)) {
        setDonations(response.data);
      } else if (Array.isArray(response.data.results)) {
        setDonations(response.data.results);
      } else {
        setDonations([]);
      }
    } catch (error) {
      console.error(
        "========== MY DONATIONS ERROR =========="
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
        "========================================="
      );

      if (error.response?.status === 401) {
        setError(
          "Your login session has expired. Please login again."
        );
      } else if (error.response?.status === 404) {
        setError(
          "My Donations API endpoint was not found."
        );
      } else if (error.response?.status === 500) {
        setError(
          "Server error while loading your donations."
        );
      } else {
        setError(
          "Unable to load your donations. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const getAcceptedAllocation = (donation) => {
    const allocations = Array.isArray(donation.allocated_ngos)
      ? donation.allocated_ngos
      : [];

    return allocations.find(
      (allocation) =>
        String(allocation.status || "").toLowerCase() === "accepted" &&
        Boolean(allocation.allocation_id)
    );
  };

  const getPickupForDonation = (donation) => {
    // Preferred source: DonationSerializer.pickup_details
    if (Array.isArray(donation.pickup_details)) {
      const pickup = donation.pickup_details.find(
        (item) => item?.status !== "Cancelled"
      );

      if (pickup) {
        return pickup;
      }
    }

    // Fallback: pickup information may be nested inside allocated_ngos.
    const allocations = Array.isArray(donation.allocated_ngos)
      ? donation.allocated_ngos
      : [];

    for (const allocation of allocations) {
      if (allocation?.pickup && allocation.pickup.status !== "Cancelled") {
        return {
          allocation_id: allocation.allocation_id,
          pickup_address: allocation.pickup.pickup_address,
          scheduled_time: allocation.pickup.scheduled_time,
          status: allocation.pickup.status,
        };
      }
    }

    // Final fallback for a response that exposes the fields directly.
    if (
      donation.pickup_address ||
      donation.scheduled_time ||
      donation.pickup_date ||
      donation.pickup_time
    ) {
      return {
        pickup_address: donation.pickup_address || donation.location,
        scheduled_time:
          donation.scheduled_time ||
          (
            donation.pickup_date && donation.pickup_time
              ? `${donation.pickup_date}T${donation.pickup_time}`
              : null
          ),
        status: donation.pickup_status || "Not Scheduled",
      };
    }

    return null;
  };

  const formatPickupDate = (scheduledTime) => {
    if (!scheduledTime) return "Not scheduled";
    const date = new Date(scheduledTime);
    return Number.isNaN(date.getTime())
      ? "Not scheduled"
      : date.toLocaleDateString();
  };

  const formatPickupTime = (scheduledTime) => {
    if (!scheduledTime) return "Not scheduled";
    const date = new Date(scheduledTime);
    return Number.isNaN(date.getTime())
      ? "Not scheduled"
      : date.toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        });
  };

  // =====================================================
  // LOAD DATA
  // =====================================================

  useEffect(() => {
    fetchMyDonations();
  }, []);

  // =====================================================
  // EDIT / DELETE PENDING DONATION
  // =====================================================

  const handleDeleteDonation = async (donationId) => {
    const donation = donations.find(
      (item) => item.id === donationId
    );

    const status = (
      donation?.status || "Pending"
    ).toLowerCase();

    // Accepted/Collected donations are locked. This frontend check improves
    // the UX, while the backend must enforce the same rule for security.
    if (
      status === "accepted" ||
      status === "collected"
    ) {
      alert(
        "This donation cannot be deleted because it has already been accepted by the NGO."
      );
      return;
    }

    if (status !== "pending" && status !== "rejected") {
      alert(
        "This donation cannot be deleted in its current status."
      );
      return;
    }

    const confirmed = window.confirm(
      status === "rejected"
        ? "Are you sure you want to delete this rejected donation?"
        : "Are you sure you want to delete this pending donation?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await api.delete(`donation/${donationId}/`);

      alert("Donation deleted successfully.");

      await fetchMyDonations();
    } catch (error) {
      console.error(
        "DELETE DONATION ERROR:",
        error.response?.data || error
      );

      alert(
        error.response?.data?.detail ||
          error.response?.data?.message ||
          "Unable to delete donation."
      );
    }
  };

  // =====================================================
  // STATUS CLASS
  // =====================================================

  const getStatusClass = (status) => {
    const value = (
      status || "Pending"
    ).toLowerCase();

    return `donation-status status-${value}`;
  };

  // =====================================================
  // STATUS TIMELINE
  // =====================================================

  const renderTimeline = (status) => {
    const currentStatus = status || "Pending";

    // ---------------------------------------------------
    // REJECTED
    // ---------------------------------------------------

    if (currentStatus === "Rejected") {
      return (
        <div className="status-timeline rejected-timeline">

          <div className="timeline-step active">
            <span>1</span>
            <small>Pending</small>
          </div>

          <div className="timeline-line active-line" />

          <div className="timeline-step rejected-step active">
            <span>✕</span>
            <small>Rejected</small>
          </div>

        </div>
      );
    }

    // ---------------------------------------------------
    // NORMAL FLOW
    // Pending → Accepted → Collected
    // ---------------------------------------------------

    const pendingActive =
      currentStatus === "Pending" ||
      currentStatus === "Accepted" ||
      currentStatus === "Collected";

    const acceptedActive =
      currentStatus === "Accepted" ||
      currentStatus === "Collected";

    const collectedActive =
      currentStatus === "Collected";

    return (
      <div className="status-timeline">

        {/* PENDING */}

        <div
          className={
            pendingActive
              ? "timeline-step active"
              : "timeline-step"
          }
        >
          <span>1</span>

          <small>
            Pending
          </small>
        </div>

        {/* LINE */}

        <div
          className={
            acceptedActive
              ? "timeline-line active-line"
              : "timeline-line"
          }
        />

        {/* ACCEPTED */}

        <div
          className={
            acceptedActive
              ? "timeline-step active"
              : "timeline-step"
          }
        >
          <span>2</span>

          <small>
            Accepted
          </small>
        </div>

        {/* LINE */}

        <div
          className={
            collectedActive
              ? "timeline-line active-line"
              : "timeline-line"
          }
        />

        {/* COLLECTED */}

        <div
          className={
            collectedActive
              ? "timeline-step active"
              : "timeline-step"
          }
        >
          <span>3</span>

          <small>
            Collected
          </small>
        </div>

      </div>
    );
  };

  // =====================================================
  // LOADING
  // =====================================================

  if (loading) {
    return (
      <div className="my-donations-loading">

        <div className="loading-icon">
          📦
        </div>

        <h2>
          Loading your donations...
        </h2>

        <p>
          Please wait while we fetch your donation history.
        </p>

      </div>
    );
  }

  // =====================================================
  // PAGE
  // =====================================================

  return (
    <div className="my-donations-page">

      {/* =================================================
          HEADER
      ================================================= */}

      <div className="my-donations-header">

        <span className="my-donations-badge">
          DONOR DASHBOARD
        </span>

        <h1>
          My Donations
        </h1>

        <p>
          Track all the items you have donated.
        </p>

        <button
          className="refresh-donations-button"
          onClick={fetchMyDonations}
        >
          🔄 Refresh
        </button>

      </div>


      {/* =================================================
          ERROR
      ================================================= */}

      {error && (
        <div className="donations-error">

          <span>
            ⚠️
          </span>

          <p>
            {error}
          </p>

          <button
            onClick={fetchMyDonations}
          >
            Try Again
          </button>

        </div>
      )}


      {/* =================================================
          EMPTY STATE
      ================================================= */}

      {!error && donations.length === 0 && (

        <div className="empty-donations">

          <div className="empty-icon">
            📦
          </div>

          <h2>
            No donations yet
          </h2>

          <p>
            Your donated items will appear here.
          </p>

        </div>

      )}


      {/* =================================================
          DONATION LIST
      ================================================= */}

      {donations.length > 0 && (

        <div className="my-donations-list">

          {donations.map((donation) => (

            <div
              className="my-donation-card"
              key={donation.id}
            >

              {/* =================================================
                  IMAGE
               ================================================= */}

              {/* <div className="my-donation-image-container">

                {donation.item_image ? (

                  <img
                    src={donation.item_image}
                    alt={donation.item_name}
                    className="my-donation-image"
                  />

                ) : (

                  <div className="no-donation-image">
                    📦
                  </div>

                )}

              </div> */}


              {/* =================================================
                  CONTENT
              ================================================= */}

              <div className="my-donation-content">

                {/* TITLE */}

                <div className="my-donation-title">

                  <h2>
                    {donation.item_name}
                  </h2>

                  <span
                    className={getStatusClass(
                      donation.status
                    )}
                  >
                    {donation.status || "Pending"}
                  </span>

                </div>


                {/* NGO */}

                <div className="donation-info">

                  <p>
                    <strong>
                      🏢 NGO:
                    </strong>{" "}
                    {donation.ngo_name ||
                      "Not available"}
                  </p>

                  <p>
                    <strong>
                      📂 Category:
                    </strong>{" "}
                    {donation.category ||
                      "Not available"}
                  </p>

                  <p>
                    <strong>
                      🔢 Quantity:
                    </strong>{" "}
                    {donation.quantity}
                  </p>

                  <p>
                    <strong>
                      ✨ Condition:
                    </strong>{" "}
                    {donation.condition ||
                      "Not available"}
                  </p>

                  <p>
                    <strong>
                      📍 Location:
                    </strong>{" "}
                    {donation.location ||
                      "Not available"}
                  </p>

                  <p>
                    <strong>
                      📝 Description:
                    </strong>{" "}
                    {donation.description ||
                      "No description"}
                  </p>

                </div>


                {/* =================================================
                    DONATION DATE
                ================================================= */}

                {donation.donation_date && (

                  <p className="donation-date">

                    📅 Donated on:{" "}

                    {new Date(
                      donation.donation_date
                    ).toLocaleString()}

                  </p>

                )}


                {/* =================================================
                    PICKUP DETAILS
                ================================================= */}

                {(() => {
                  const pickup = getPickupForDonation(donation);

                  return (
                    <div className="donor-pickup-section">

                      <div className="donor-pickup-header">
                        <div>
                          <span className="pickup-section-label">
                            🚚 PICKUP DETAILS
                          </span>
                          <h3>
                            {pickup
                              ? "Pickup Scheduled"
                              : "Pickup Not Scheduled"}
                          </h3>
                        </div>

                        <span className="pickup-status-badge">
                          {pickup?.status || "Not Scheduled"}
                        </span>
                      </div>

                      <div className="donor-pickup-details">
                        <p>
                          <strong>📍 Location:</strong>{" "}
                          {pickup?.pickup_address ||
                            donation.location ||
                            "Not scheduled"}
                        </p>
                        <p>
                          <strong>📅 Pickup Date:</strong>{" "}
                          {formatPickupDate(pickup?.scheduled_time)}
                        </p>
                        <p>
                          <strong>🕐 Pickup Time:</strong>{" "}
                          {formatPickupTime(pickup?.scheduled_time)}
                        </p>

                        {!pickup && (
                          <p className="pickup-waiting-message">
                            ⏳ Pickup has not been scheduled yet.
                          </p>
                        )}
                      </div>


                    </div>
                  );
                })()}

                {/* =================================================
                    STATUS TIMELINE
                ================================================= */}

                {renderTimeline(
                  donation.status
                )}

                {/* =================================================
                    EDIT / DELETE ACTIONS
                    Only available for Pending donations
                ================================================= */}

                {["pending", "rejected"].includes(
                  (
                    donation.status || "Pending"
                  ).toLowerCase()
                ) && (
                  <div className="donation-actions">

                    <button
                      type="button"
                      className="edit-donation-button"
                      onClick={() =>
                        navigate(
                          `/edit-donation/${donation.id}`
                        )
                      }
                    >
                      ✏️ Edit
                    </button>

                    <button
                      type="button"
                      className="delete-donation-button"
                      onClick={() =>
                        handleDeleteDonation(
                          donation.id
                        )
                      }
                    >
                      🗑️ Delete
                    </button>

                  </div>
                )}

              </div>

            </div>

          ))}

        </div>

      )}


    </div>
  );
}

export default MyDonations;