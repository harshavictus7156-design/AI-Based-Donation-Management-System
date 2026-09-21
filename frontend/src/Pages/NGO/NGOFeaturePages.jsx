import NotificationsPage from "../../components/NotificationsPage/NotificationsPage";
// ============================================================
// NGO FEATURE PAGES
// Donations | Requirements | Allocations | Pickups
// Analytics | Impact | Notifications | Settings
// ============================================================

import { useEffect, useState } from "react";
import api from "../../services/api";
import ThemeToggle from "../../components/ThemeToggle/ThemeToggle";
import "./NGOFeaturePages.css";

// ============================================================
// HELPER FUNCTIONS
// ============================================================

const getList = (data) => {
  if (Array.isArray(data)) {
    return data;
  }

  return (
    data?.results ||
    data?.donations ||
    data?.requirements ||
    data?.allocations ||
    data?.pickups ||
    []
  );
};

const getValue = (...values) => {
  const value = values.find(
    (item) =>
      item !== undefined &&
      item !== null &&
      item !== ""
  );

  return value ?? "Not available";
};

const formatDateTime = (value) => {
  if (!value) {
    return "Not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const formatDate = (value) => {
  if (!value) {
    return "Not scheduled";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleDateString([], {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
};

const getStatusClass = (status) => {
  return String(status || "pending")
    .toLowerCase()
    .replace(/\s+/g, "-");
};

// ============================================================
// GENERIC GET HOOK
// ============================================================

function useGet(url, key) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    try {
      setLoading(true);

      const response = await api.get(url);

      setItems(getList(response.data));
    } catch (error) {
      console.error(`Failed to load ${key}:`, error);
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [url]);

  return {
    items,
    loading,
    reload: load,
    setItems,
  };
}

// ============================================================
// NGO DONATIONS
// ============================================================

export function NGODonations() {
  const [donations, setDonations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedDonation, setSelectedDonation] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // ----------------------------------------------------------
  // Fetch Donations
  // ----------------------------------------------------------

  const fetchDonations = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await api.get("ngo/donations/");

      setDonations(getList(response.data));
    } catch (err) {
      console.error(
        "Failed to fetch NGO donations:",
        err
      );

      setError(
        "Unable to load donations. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDonations();
  }, []);

  // ----------------------------------------------------------
  // Open Donation Details
  // ----------------------------------------------------------

  const openDonationDetails = async (donation) => {
    setSelectedDonation(donation);

    if (!donation?.id) {
      return;
    }

    try {
      const response = await api.get(
        `donation/${donation.id}/`
      );

      setSelectedDonation(
        response.data || donation
      );
    } catch (err) {
      console.warn(
        "Detailed donation information unavailable:",
        err
      );
    }
  };

  // ----------------------------------------------------------
  // Update Donation Status
  // ----------------------------------------------------------

  const updateDonationStatus = async (
    donation,
    newStatus
  ) => {
    if (!donation?.id) {
      return;
    }

    try {
      setActionLoading(true);

      await api.patch(
        `donation/${donation.id}/status/`,
        {
          status: newStatus,
        }
      );

      await fetchDonations();

      setSelectedDonation(null);
    } catch (err) {
      console.error(
        "Failed to update donation status:",
        err
      );

      alert(
        err?.response?.data
          ? JSON.stringify(err.response.data)
          : "Unable to update donation status."
      );
    } finally {
      setActionLoading(false);
    }
  };

  // ----------------------------------------------------------
  // Loading
  // ----------------------------------------------------------

  if (loading) {
    return (
      <div className="ngo-feature-page">
        <div className="ngo-page-header">
          <div>
            <span className="ngo-eyebrow">
              NGO MANAGEMENT
            </span>

            <h1>Donations</h1>

            <p>
              Review and manage incoming donations.
            </p>
          </div>
        </div>

        <div className="ngo-empty-state">
          Loading donations...
        </div>
      </div>
    );
  }

  // ----------------------------------------------------------
  // Render
  // ----------------------------------------------------------

  return (
    <div className="ngo-feature-page">

      <div className="ngo-page-header">
        <div>
          <span className="ngo-eyebrow">
            NGO MANAGEMENT
          </span>

          <h1>Donations</h1>

          <p>
            Review incoming donations and manage their
            status.
          </p>
        </div>

        <button
          type="button"
          className="ngo-refresh-button"
          onClick={fetchDonations}
        >
          ↻ Refresh
        </button>
      </div>

      {error && (
        <div className="ngo-error-message">
          {error}

          <button
            type="button"
            onClick={fetchDonations}
          >
            Retry
          </button>
        </div>
      )}

      <div className="ngo-donation-list">

        {donations.length === 0 ? (
          <div className="ngo-empty-state">
            <div className="ngo-empty-icon">
              📦
            </div>

            <h3>
              No donations available
            </h3>

            <p>
              New donor submissions will appear here.
            </p>
          </div>
        ) : (
          donations.map((donation) => {
            const status =
              donation.status || "Pending";

            const itemName = getValue(
              donation.item_name,
              donation.item,
              "Donation"
            );

            const quantity = getValue(
              donation.quantity,
              donation.required_quantity
            );

            const donorName = getValue(
              donation.donor_name,
              donation.donor?.name,
              donation.donor?.username
            );

            const donatedDate = getValue(
              donation.created_at,
              donation.donated_at,
              donation.donation_date
            );

            return (
              <article
                key={donation.id}
                className="ngo-donation-card"
              >

                <div
                  className="ngo-donation-content"
                  onClick={() =>
                    openDonationDetails(donation)
                  }
                >

                  <div className="ngo-donation-top">

                    <div>
                      <span className="ngo-eyebrow">
                        {donation.category ||
                          "DONATION"}
                      </span>

                      <h3>
                        {itemName}
                      </h3>
                    </div>

                    <span
                      className={`ngo-status ${getStatusClass(
                        status
                      )}`}
                    >
                      {status}
                    </span>

                  </div>

                  <div className="ngo-donation-summary">

                    <div>
                      <span>Donor</span>
                      <strong>
                        {donorName}
                      </strong>
                    </div>

                    <div>
                      <span>Quantity</span>
                      <strong>
                        {quantity}
                      </strong>
                    </div>

                    <div>
                      <span>Donated</span>
                      <strong>
                        {formatDateTime(
                          donatedDate
                        )}
                      </strong>
                    </div>

                  </div>

                  <button
                    type="button"
                    className="ngo-view-details"
                    onClick={(event) => {
                      event.stopPropagation();

                      openDonationDetails(
                        donation
                      );
                    }}
                  >
                    View Full Details →
                  </button>

                </div>

                <div className="ngo-donation-actions">

                  {status === "Pending" && (
                    <>
                      <button
                        type="button"
                        className="ngo-accept-button"
                        disabled={actionLoading}
                        onClick={() =>
                          updateDonationStatus(
                            donation,
                            "Accepted"
                          )
                        }
                      >
                        ✓ Accept
                      </button>

                      <button
                        type="button"
                        className="ngo-reject-button"
                        disabled={actionLoading}
                        onClick={() =>
                          updateDonationStatus(
                            donation,
                            "Rejected"
                          )
                        }
                      >
                        ✕ Reject
                      </button>
                    </>
                  )}

                  {status === "Accepted" && (
                    <button
                      type="button"
                      className="ngo-collect-button"
                      disabled={actionLoading}
                      onClick={() =>
                        updateDonationStatus(
                          donation,
                          "Collected"
                        )
                      }
                    >
                      🚚 Mark Collected
                    </button>
                  )}

                  {status === "Rejected" && (
                    <span className="ngo-completed-label">
                      Donation Rejected
                    </span>
                  )}

                  {status === "Collected" && (
                    <span className="ngo-completed-label">
                      ✓ Donation Collected
                    </span>
                  )}

                </div>

              </article>
            );
          })
        )}

      </div>

      {selectedDonation && (
        <DonationDetailsModal
          donation={selectedDonation}
          loading={actionLoading}
          onClose={() =>
            setSelectedDonation(null)
          }
          onUpdateStatus={updateDonationStatus}
        />
      )}

    </div>
  );
}

// ============================================================
// DONATION DETAILS MODAL
// ============================================================

function DonationDetailsModal({
  donation,
  loading,
  onClose,
  onUpdateStatus,
}) {
  const status =
    donation.status || "Pending";

  const pickup =
    donation.pickup_details ||
    donation.pickup ||
    {};

  const donor =
    donation.donor ||
    {};

  const itemName = getValue(
    donation.item_name,
    donation.item,
    "Donation"
  );

  const category = getValue(
    donation.category
  );

  const quantity = getValue(
    donation.quantity,
    donation.required_quantity
  );

  const description = getValue(
    donation.description
  );

  const submittedDate = getValue(
    donation.created_at,
    donation.donated_at,
    donation.donation_date
  );

  const donorName = getValue(
    donation.donor_name,
    donor.name,
    donor.username
  );

  const donorEmail = getValue(
    donation.donor_email,
    donor.email
  );

  const donorPhone = getValue(
    donation.donor_phone,
    donor.phone
  );

  const pickupDate = getValue(
    donation.pickup_date,
    donation.scheduled_date,
    pickup.pickup_date,
    pickup.scheduled_date
  );

  const pickupTime = getValue(
    donation.pickup_time,
    donation.scheduled_time,
    pickup.pickup_time,
    pickup.scheduled_time,
    pickup.time
  );

  const pickupAddress = getValue(
    donation.pickup_address,
    donation.address,
    pickup.address,
    pickup.pickup_address
  );

  const pickupStatus = getValue(
    donation.pickup_status,
    pickup.status,
    status === "Accepted"
      ? "Not scheduled"
      : status
  );

  const pickupNotes = getValue(
    donation.pickup_notes,
    pickup.notes
  );

  return (
    <div
      className="ngo-detail-overlay"
      role="dialog"
      aria-modal="true"
    >
      <div className="ngo-detail-modal">

        <div className="ngo-detail-header">

          <div>
            <span className="ngo-eyebrow">
              DONATION DETAILS
            </span>

            <h2>
              {itemName}
            </h2>

            <span
              className={`ngo-status ${getStatusClass(
                status
              )}`}
            >
              {status}
            </span>
          </div>

          <button
            type="button"
            className="ngo-close-button"
            onClick={onClose}
            aria-label="Close donation details"
          >
            ×
          </button>

        </div>

        <div className="ngo-details-grid">

          <DetailSection title="Donation Information">

            <DetailRow
              label="Donation ID"
              value={getValue(donation.id)}
            />

            <DetailRow
              label="Category"
              value={category}
            />

            <DetailRow
              label="Quantity"
              value={quantity}
            />

            <DetailRow
              label="Submitted"
              value={formatDateTime(
                submittedDate
              )}
            />

            <DetailRow
              label="Description"
              value={description}
            />

          </DetailSection>

          <DetailSection title="Donor Information">

            <DetailRow
              label="Name"
              value={donorName}
            />

            <DetailRow
              label="Email"
              value={donorEmail}
            />

            <DetailRow
              label="Phone"
              value={donorPhone}
            />

          </DetailSection>

          <DetailSection title="Pickup Information">

            <DetailRow
              label="Status"
              value={pickupStatus}
            />

            <DetailRow
              label="Pickup Date"
              value={formatDate(pickupDate)}
            />

            <DetailRow
              label="Pickup Time"
              value={pickupTime}
            />

            <DetailRow
              label="Location"
              value={pickupAddress}
            />

            <DetailRow
              label="Notes"
              value={pickupNotes}
            />

          </DetailSection>

          <DetailSection title="Donation Timeline">

            <DonationTimeline
              donation={donation}
              pickup={pickup}
            />

          </DetailSection>

        </div>

        <div className="ngo-detail-actions">

          {status === "Pending" && (
            <>
              <button
                type="button"
                className="ngo-accept-button"
                disabled={loading}
                onClick={() =>
                  onUpdateStatus(
                    donation,
                    "Accepted"
                  )
                }
              >
                ✓ Accept Donation
              </button>

              <button
                type="button"
                className="ngo-reject-button"
                disabled={loading}
                onClick={() =>
                  onUpdateStatus(
                    donation,
                    "Rejected"
                  )
                }
              >
                ✕ Reject Donation
              </button>
            </>
          )}

          {status === "Accepted" && (
            <button
              type="button"
              className="ngo-collect-button"
              disabled={loading}
              onClick={() =>
                onUpdateStatus(
                  donation,
                  "Collected"
                )
              }
            >
              🚚 Mark Collected
            </button>
          )}

          <button
            type="button"
            className="ngo-secondary-button"
            onClick={onClose}
          >
            Close
          </button>

        </div>

      </div>
    </div>
  );
}

// ============================================================
// DONATION TIMELINE
// ============================================================

function DonationTimeline({
  donation,
  pickup,
}) {
  const status =
    donation.status || "Pending";

  const submittedAt = getValue(
    donation.created_at,
    donation.donated_at,
    donation.donation_date
  );

  const acceptedAt = getValue(
    donation.accepted_at,
    donation.approved_at
  );

  const pickupDate = getValue(
    donation.pickup_date,
    pickup.pickup_date,
    pickup.scheduled_date
  );

  const collectedAt = getValue(
    donation.collected_at,
    pickup.collected_at
  );

  const timeline = [
    {
      title: "Donation Submitted",
      date: submittedAt,
      completed: true,
    },
    {
      title: "Accepted by NGO",
      date: acceptedAt,
      completed:
        status === "Accepted" ||
        status === "Collected",
    },
    {
      title: "Pickup Scheduled",
      date: pickupDate,
      completed:
        pickupDate !== "Not available",
    },
    {
      title: "Donation Collected",
      date: collectedAt,
      completed:
        status === "Collected",
    },
  ];

  return (
    <div className="ngo-timeline">

      {timeline.map((step) => (
        <div
          key={step.title}
          className={`ngo-timeline-item ${
            step.completed
              ? "completed"
              : ""
          }`}
        >

          <div className="ngo-timeline-icon">
            {step.completed
              ? "✓"
              : "○"}
          </div>

          <div className="ngo-timeline-content">

            <strong>
              {step.title}
            </strong>

            <span>
              {formatDateTime(step.date)}
            </span>

          </div>

        </div>
      ))}

    </div>
  );
}

// ============================================================
// NGO REQUIREMENTS
// ============================================================

export function NGORequirements() {
  const {
    items,
    loading,
    reload,
  } = useGet(
    "ngo/requirements/",
    "requirements"
  );

  const [form, setForm] = useState({
    item_name: "",
    category: "Food",
    required_quantity: "",
    priority: "Medium",
    description: "",
  });

  const [edit, setEdit] = useState(null);

  const resetForm = () => {
    setForm({
      item_name: "",
      category: "Food",
      required_quantity: "",
      priority: "Medium",
      description: "",
    });

    setEdit(null);
  };

  const save = async (event) => {
    event.preventDefault();

    try {
      const payload = {
        ...form,
        required_quantity: Number(
          form.required_quantity
        ),
      };

      if (edit) {
        await api.put(
          `ngo/requirements/${edit}/`,
          payload
        );
      } else {
        await api.post(
          "ngo/requirements/",
          payload
        );
      }

      resetForm();
      await reload();
    } catch (error) {
      alert(
        error?.response?.data
          ? JSON.stringify(
              error.response.data
            )
          : "Unable to save requirement."
      );
    }
  };

  const remove = async (id) => {
    if (
      !window.confirm(
        "Delete this requirement?"
      )
    ) {
      return;
    }

    try {
      await api.delete(
        `ngo/requirements/${id}/`
      );

      await reload();
    } catch (error) {
      alert(
        "Unable to delete requirement."
      );
    }
  };

  return (
    <Page
      title="Requirements"
      action={
        <button onClick={reload}>
          🔄 Refresh
        </button>
      }
    >

      <div className="ngo-two-col">

        <form
          className="ngo-form-card"
          onSubmit={save}
        >

          <span className="ngo-item-label">
            {edit
              ? "EDIT REQUIREMENT"
              : "ADD REQUIREMENT"}
          </span>

          <h3>
            {edit
              ? "Update requirement"
              : "What does your NGO need?"}
          </h3>

          <input
            placeholder="Item name"
            value={form.item_name}
            onChange={(event) =>
              setForm({
                ...form,
                item_name:
                  event.target.value,
              })
            }
            required
          />

          <select
            value={form.category}
            onChange={(event) =>
              setForm({
                ...form,
                category:
                  event.target.value,
              })
            }
          >
            <option>Food</option>
            <option>Clothing</option>
            <option>Education</option>
            <option>Electronics</option>
            <option>Other</option>
          </select>

          <input
            type="number"
            min="1"
            placeholder="Required quantity"
            value={
              form.required_quantity
            }
            onChange={(event) =>
              setForm({
                ...form,
                required_quantity:
                  event.target.value,
              })
            }
            required
          />

          <select
            value={form.priority}
            onChange={(event) =>
              setForm({
                ...form,
                priority:
                  event.target.value,
              })
            }
          >
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
            <option>Urgent</option>
          </select>

          <textarea
            placeholder="Description"
            value={form.description}
            onChange={(event) =>
              setForm({
                ...form,
                description:
                  event.target.value,
              })
            }
          />

          <div>

            <button
              className="primary"
              type="submit"
            >
              {edit
                ? "Update Requirement"
                : "Add Requirement"}
            </button>

            {edit && (
              <button
                type="button"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

        <div>

          <div className="ngo-section-title">
            <span>ACTIVE NEEDS</span>
            <h3>Your requirements</h3>
          </div>

          {loading ? (
            <Loading />
          ) : items.length ? (
            items.map((requirement) => (
              <article
                className="ngo-item-card"
                key={requirement.id}
              >

                <div>

                  <span className="ngo-item-label">
                    {requirement.priority ||
                      "MEDIUM"}
                  </span>

                  <h3>
                    {requirement.item_name}
                  </h3>

                  <p>
                    Required:{" "}
                    {
                      requirement.required_quantity
                    }
                  </p>

                  <p>
                    {requirement.description ||
                      "No description provided."}
                  </p>

                </div>

                <div className="ngo-item-actions">

                  <button
                    onClick={() => {
                      setEdit(
                        requirement.id
                      );

                      setForm({
                        item_name:
                          requirement.item_name ||
                          "",
                        category:
                          requirement.category ||
                          "Food",
                        required_quantity:
                          requirement.required_quantity ||
                          "",
                        priority:
                          requirement.priority ||
                          "Medium",
                        description:
                          requirement.description ||
                          "",
                      });
                    }}
                  >
                    Edit
                  </button>

                  <button
                    className="bad"
                    onClick={() =>
                      remove(requirement.id)
                    }
                  >
                    Delete
                  </button>

                </div>

              </article>
            ))
          ) : (
            <Empty
              text="No requirements added yet."
            />
          )}

        </div>

      </div>

    </Page>
  );
}

// ============================================================
// NGO ALLOCATIONS
// ============================================================

export function NGOAllocations() {
  const {
    items,
    loading,
    reload,
  } = useGet(
    "ngo/allocations/",
    "allocations"
  );

  return (
    <Page
      title="Allocations"
      action={
        <button onClick={reload}>
          🔄 Refresh
        </button>
      }
    >

      {loading ? (
        <Loading />
      ) : (
        <div className="ngo-list">

          {items.length ? (
            items.map((allocation, index) => (
              <article
                className="ngo-item-card"
                key={
                  allocation.id ||
                  index
                }
              >

                <div>

                  <span className="ngo-item-label">
                    ALLOCATION
                  </span>

                  <h3>
                    {allocation.item_name ||
                      allocation.donation_item ||
                      allocation.donation
                        ?.item_name ||
                      "Donation"}
                  </h3>

                  <p>
                    Quantity:{" "}
                    {allocation.quantity ??
                      allocation.allocated_quantity ??
                      "Not available"}
                  </p>

                  <p>
                    Status:{" "}
                    <strong>
                      {allocation.status ||
                        "Allocated"}
                    </strong>
                  </p>

                </div>

              </article>
            ))
          ) : (
            <Empty
              text="No allocations found."
            />
          )}

        </div>
      )}

    </Page>
  );
}

// ============================================================
// NGO PICKUPS
// ============================================================

export function NGOPickups() {
  const {
    items,
    loading,
    reload,
  } = useGet(
    "pickup/ngo/",
    "pickups"
  );

  return (
    <Page
      title="Pickups"
      action={
        <button onClick={reload}>
          🔄 Refresh
        </button>
      }
    >

      {loading ? (
        <Loading />
      ) : (
        <div className="ngo-list">

          {items.length ? (
            items.map((pickup, index) => {

              // ------------------------------------------------
              // Pickup / Donation nested information
              // ------------------------------------------------

              const pickupDetails =
                pickup.pickup_details ||
                pickup.pickup ||
                {};

              const donation =
                pickup.donation ||
                {};

              // ------------------------------------------------
              // Item Name
              // ------------------------------------------------

              const itemName = getValue(
                pickup.item_name,
                pickup.donation_item,
                pickupDetails.item_name,
                donation.item_name,
                donation.item,
                "Donation pickup"
              );

              // ------------------------------------------------
              // Pickup Date
              // ------------------------------------------------

              const pickupDate = getValue(
                pickup.pickup_date,
                pickup.scheduled_date,
                pickupDetails.pickup_date,
                pickupDetails.scheduled_date,
                donation.pickup_date,
                donation.scheduled_date
              );

              // ------------------------------------------------
              // Pickup Status
              // ------------------------------------------------

              const pickupStatus = getValue(
                pickup.status,
                pickup.pickup_status,
                pickupDetails.status,
                "Pending"
              );

              // ------------------------------------------------
              // Pickup Location
              // ------------------------------------------------

              const pickupLocation = getValue(
                pickup.pickup_address,
                pickup.address,
                pickup.location,
                pickup.pickup_location,

                pickupDetails.pickup_address,
                pickupDetails.address,
                pickupDetails.location,
                pickupDetails.pickup_location,

                donation.pickup_address,
                donation.address,
                donation.location
              );

              // ------------------------------------------------
              // Pickup Time
              // ------------------------------------------------

              const pickupTime = getValue(
                pickup.pickup_time,
                pickup.scheduled_time,
                pickupDetails.pickup_time,
                pickupDetails.scheduled_time,
                donation.pickup_time,
                donation.scheduled_time
              );

              return (
                <article
                  className="ngo-item-card"
                  key={pickup.id || index}
                >

                  <div>

                    <span className="ngo-item-label">
                      PICKUP
                    </span>

                    <h3>
                      {itemName}
                    </h3>

                    <p>
                      Date:{" "}
                      {pickupDate}
                    </p>

                    <p>
                      Time:{" "}
                      {pickupTime}
                    </p>

                    <p>
                      Status:{" "}
                      <strong>
                        {pickupStatus}
                      </strong>
                    </p>

                    {/* LOCATION */}

                    <p>
                      📍 <strong>Location:</strong>{" "}
                      {pickupLocation}
                    </p>

                  </div>

                </article>
              );
            })
          ) : (
            <Empty
              text="No pickup requests found."
            />
          )}

        </div>
      )}

    </Page>
  );
}
// ============================================================
// NGO ANALYTICS
// ============================================================

export function NGOAnalytics() {
  const {
    items,
    loading,
  } = useGet(
    "ngo/donations/",
    "analytics"
  );

  const statuses = [
    "Pending",
    "Accepted",
    "Rejected",
    "Collected",
  ];

  return (
    <Page title="Analytics">

      <div className="ngo-clean-stats">

        {statuses.map((status) => (
          <article key={status}>

            <b>
              {status === "Pending"
                ? "⏳"
                : status === "Accepted"
                ? "✅"
                : status === "Rejected"
                ? "❌"
                : "🚚"}
            </b>

            <div>

              <small>
                {status}
              </small>

              <strong>
                {loading
                  ? "…"
                  : items.filter(
                      (item) =>
                        item.status ===
                        status
                    ).length}
              </strong>

            </div>

          </article>
        ))}

      </div>

    </Page>
  );
}

// ============================================================
// NGO IMPACT
// ============================================================

export function NGOImpact() {
  const {
    items,
    loading,
  } = useGet(
    "ngo/donations/",
    "impact"
  );

  const collected = items.filter(
    (item) =>
      item.status === "Collected"
  ).length;

  return (
    <Page title="Impact">

      <div className="ngo-impact-card">

        <span>
          COMPLETED OUTCOME
        </span>

        <strong>
          {loading
            ? "…"
            : collected}
        </strong>

        <h3>
          Donations collected
        </h3>

        <p>
          This count is derived from the
          donations available to your NGO.
          No fabricated impact numbers are
          shown.
        </p>

      </div>

    </Page>
  );
}

// ============================================================
// NGO NOTIFICATIONS
// ============================================================

export function NGONotifications() {
  return <NotificationsPage role="ngo" />;
}

// ============================================================
// NGO SETTINGS
// Organization | Notifications | Appearance | Security
// Preferences | Account Management
// ============================================================

export function NGOSettings() {
  return (
    <Page title="Settings">

      {/* ======================================================
          ORGANIZATION ACCOUNT
          ====================================================== */}

      <section className="ngo-settings-card">

        <div className="ngo-settings-section-heading">

          <div className="ngo-settings-section-icon coral">
            🏢
          </div>

          <div>
            <span>ORGANIZATION</span>
            <h3>Organization Account</h3>
          </div>

        </div>


        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            🏢
          </div>

          <div className="ngo-settings-row-content">

            <strong>Organization Profile</strong>

            <p>
              Manage your NGO information and
              organization details.
            </p>

          </div>

          <button
            type="button"
            className="ngo-settings-action-button"
          >
            Edit
          </button>

        </div>

      </section>


      {/* ======================================================
          NOTIFICATIONS
          ====================================================== */}

      <section className="ngo-settings-card">

        <div className="ngo-settings-section-heading">

          <div className="ngo-settings-section-icon coral">
            🔔
          </div>

          <div>
            <span>COMMUNICATION</span>
            <h3>Notifications</h3>
          </div>

        </div>


        {/* Donation Updates */}

        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            🔔
          </div>

          <div className="ngo-settings-row-content">

            <strong>Donation updates</strong>

            <p>
              Receive notifications when new donations
              are received or their status changes.
            </p>

          </div>

          <span className="ngo-settings-status active">
            ON
          </span>

        </div>


        {/* Requirement Alerts */}

        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            📦
          </div>

          <div className="ngo-settings-row-content">

            <strong>Requirement alerts</strong>

            <p>
              Receive updates related to your
              active NGO requirements.
            </p>

          </div>

          <span className="ngo-settings-status active">
            ON
          </span>

        </div>


        {/* Pickup Updates */}

        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            🚚
          </div>

          <div className="ngo-settings-row-content">

            <strong>Pickup updates</strong>

            <p>
              Receive notifications about scheduled
              and completed donation pickups.
            </p>

          </div>

          <span className="ngo-settings-status active">
            ON
          </span>

        </div>

      </section>


      {/* ======================================================
          APPEARANCE
          ====================================================== */}

      <section className="ngo-settings-card">

        <div className="ngo-settings-section-heading">

          <div className="ngo-settings-section-icon blue">
            🎨
          </div>

          <div>
            <span>INTERFACE</span>
            <h3>Appearance</h3>
          </div>

        </div>


        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            🌙
          </div>

          <div className="ngo-settings-row-content">

            <strong>Theme</strong>

            <p>
              Switch between light and dark mode
              for your workspace.
            </p>

          </div>

          {/* Existing project theme control */}
          <div className="ngo-settings-theme-control">
            <ThemeToggle />
          </div>

        </div>

      </section>


      {/* ======================================================
          SECURITY
          ====================================================== */}

      <section className="ngo-settings-card">

        <div className="ngo-settings-section-heading">

          <div className="ngo-settings-section-icon green">
            🔐
          </div>

          <div>
            <span>SECURITY</span>
            <h3>Security</h3>
          </div>

        </div>


        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            🔐
          </div>

          <div className="ngo-settings-row-content">

            <strong>Password &amp; Security</strong>

            <p>
              Manage your password and protect
              your organization account.
            </p>

          </div>

          <button
            type="button"
            className="ngo-settings-action-button"
          >
            Manage
          </button>

        </div>

      </section>


      {/* ======================================================
          ORGANIZATION PREFERENCES
          ====================================================== */}

      <section className="ngo-settings-card">

        <div className="ngo-settings-section-heading">

          <div className="ngo-settings-section-icon blue">
            📍
          </div>

          <div>
            <span>OPERATIONS</span>
            <h3>Organization Preferences</h3>
          </div>

        </div>


        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            📍
          </div>

          <div className="ngo-settings-row-content">

            <strong>Pickup Preferences</strong>

            <p>
              Manage pickup availability and
              organization operating preferences.
            </p>

          </div>

          <button
            type="button"
            className="ngo-settings-action-button"
          >
            Manage
          </button>

        </div>

      </section>


      {/* ======================================================
          ACCOUNT MANAGEMENT
          ====================================================== */}

      <section className="ngo-settings-card ngo-settings-danger-card">

        <div className="ngo-settings-section-heading">

          <div className="ngo-settings-section-icon danger">
            🛡️
          </div>

          <div>
            <span>ACCOUNT</span>
            <h3>Account Management</h3>
          </div>

        </div>


        <div className="ngo-settings-row">

          <div className="ngo-settings-row-icon">
            🛡️
          </div>

          <div className="ngo-settings-row-content">

            <strong>Organization account actions</strong>

            <p>
              Manage your organization account or
              sign out from the NGO workspace.
            </p>

          </div>

          <button
            type="button"
            className="ngo-settings-logout-button"
          >
            Logout
          </button>

        </div>

      </section>

    </Page>
  );
}
// ============================================================
// SHARED PAGE COMPONENT
// ============================================================

function Page({
  title,
  action,
  children,
}) {
  return (
    <div className="ngo-feature">

      <div className="ngo-feature-head">

        <div>

          <span>
            NGO MANAGEMENT
          </span>

          <h2>
            {title}
          </h2>

        </div>

        {action}

      </div>

      {children}

    </div>
  );
}

// ============================================================
// LOADING
// ============================================================

function Loading() {
  return (
    <div className="ngo-empty">
      Loading...
    </div>
  );
}

// ============================================================
// EMPTY
// ============================================================

function Empty({ text }) {
  return (
    <div className="ngo-empty">
      {text}
    </div>
  );
}

// ============================================================
// DETAIL SECTION
// ============================================================

function DetailSection({
  title,
  children,
}) {
  return (
    <section className="ngo-detail-section">

      <h3>
        {title}
      </h3>

      <div className="ngo-detail-section-content">
        {children}
      </div>

    </section>
  );
}

// ============================================================
// DETAIL ROW
// ============================================================

function DetailRow({
  label,
  value,
}) {
  return (
    <div className="ngo-detail-row">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}