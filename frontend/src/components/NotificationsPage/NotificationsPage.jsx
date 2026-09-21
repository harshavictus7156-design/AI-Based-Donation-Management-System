import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FiBell,
  FiCheck,
  FiCheckCircle,
  FiTrash2,
  FiTruck,
  FiZap,
  FiPackage,
  FiX,
  FiFileText,
} from "react-icons/fi";

import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
} from "../../services/notificationService";

import "./NotificationsPage.css";

const iconFor = (type) => {
  if (type?.includes("MATCH")) return FiZap;
  if (type?.includes("PICKUP")) return FiTruck;
  if (type?.includes("ALLOCATED")) return FiPackage;
  if (type?.includes("APPROVED")) return FiCheckCircle;
  if (type?.includes("REJECTED") || type?.includes("CANCELLED")) return FiX;
  if (type?.includes("REQUEST")) return FiFileText;
  return FiBell;
};

const toneFor = (type) => {
  if (type?.includes("MATCH")) return "ai";

  if (
    type?.includes("REJECTED") ||
    type?.includes("CANCELLED")
  ) {
    return "danger";
  }

  if (
    type?.includes("APPROVED") ||
    type?.includes("DELIVERED") ||
    type?.includes("COLLECTED")
  ) {
    return "success";
  }

  if (
    type?.includes("PICKUP") ||
    type?.includes("ALLOCATED")
  ) {
    return "blue";
  }

  return "default";
};

const timeLabel = (value) => {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "";

  const seconds = Math.max(
    0,
    Math.floor((Date.now() - date.getTime()) / 1000)
  );

  if (seconds < 60) return "Just now";

  const minutes = Math.floor(seconds / 60);

  if (minutes < 60) {
    return `${minutes} min ago`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours} hr ago`;
  }

  const days = Math.floor(hours / 24);

  if (days < 7) {
    return `${days} days ago`;
  }

  return date.toLocaleDateString();
};

export default function NotificationsPage({ role = "donor" }) {
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionId, setActionId] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [notifications, count] = await Promise.all([
        getNotifications(),
        getUnreadCount(),
      ]);

      setItems(notifications);
      setUnread(count);
    } catch {
      setError(
        "Unable to load notifications. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const markRead = async (item) => {
    if (item.is_read) return;

    setActionId(item.id);

    try {
      await markNotificationRead(item.id);

      setItems((current) =>
        current.map((notification) =>
          notification.id === item.id
            ? {
                ...notification,
                is_read: true,
              }
            : notification
        )
      );

      setUnread((current) =>
        Math.max(0, current - 1)
      );
    } catch {
      setError(
        "Unable to mark this notification as read."
      );
    } finally {
      setActionId(null);
    }
  };

  /*
   * Navigate the user to the most relevant existing page
   * after clicking a notification.
   *
   * The notification is marked as read first.
   */
  const handleNotificationClick = async (item) => {
    await markRead(item);

    switch (item.notification_type) {
      /*
       * Donor donation related notifications
       */
      case "DONATION_SUBMITTED":
      case "DONATION_APPROVED":
      case "DONATION_REJECTED":
      case "DONATION_COLLECTED":
      case "DONATION_MATCHED":
        if (role === "donor") {
          navigate("/my-donations");
        } else {
          navigate("/ngo-donations");
        }
        break;

      /*
       * NGO requirement matching
       */
      case "REQUEST_MATCHED":
        if (role === "ngo") {
          navigate("/ngo-requirements");
        } else {
          navigate("/my-donations");
        }
        break;

      /*
       * Resource allocation
       */
      case "RESOURCE_ALLOCATED":
        if (role === "ngo") {
          navigate("/ngo-allocations");
        } else {
          navigate("/my-donations");
        }
        break;

      /*
       * Pickup related notifications
       */
      case "PICKUP_CREATED":
      case "PICKUP_CONFIRMED":
      case "PICKUP_DISPATCHED":
      case "DONATION_DELIVERED":
      case "PICKUP_CANCELLED":
        if (role === "ngo") {
          navigate("/ngo-pickups");
        } else {
          navigate("/my-activity");
        }
        break;

      /*
       * Fallback
       */
      default:
        navigate(
          role === "ngo"
            ? "/ngo-notifications"
            : "/notifications"
        );
        break;
    }
  };

  const markAll = async () => {
    setActionId("all");

    try {
      await markAllNotificationsRead();

      setItems((current) =>
        current.map((notification) => ({
          ...notification,
          is_read: true,
        }))
      );

      setUnread(0);
    } catch {
      setError(
        "Unable to mark notifications as read."
      );
    } finally {
      setActionId(null);
    }
  };

  const remove = async (id) => {
    setActionId(id);

    try {
      /*
       * Get the notification before removing it so we can
       * correctly update the unread count.
       */
      const deletedNotification = items.find(
        (notification) => notification.id === id
      );

      await deleteNotification(id);

      setItems((current) =>
        current.filter(
          (notification) => notification.id !== id
        )
      );

      if (
        deletedNotification &&
        !deletedNotification.is_read
      ) {
        setUnread((current) =>
          Math.max(0, current - 1)
        );
      }
    } catch {
      setError(
        "Unable to delete this notification."
      );
    } finally {
      setActionId(null);
    }
  };

  return (
    <div
      className={`notifications-page notifications-${role}`}
    >
      <header className="notifications-page-header">
        <span>
          <FiBell /> COMMUNICATION
        </span>

        <div className="notifications-title-row">
          <div>
            <h2>Notifications</h2>

            <p>
              Keep track of donation, pickup, matching and
              resource updates.
            </p>
          </div>

          {unread > 0 && (
            <button
              type="button"
              className="notifications-mark-all"
              onClick={markAll}
              disabled={actionId === "all"}
            >
              <FiCheck />
              Mark all as read
            </button>
          )}
        </div>
      </header>

      {error && (
        <div className="notifications-error">
          {error}
        </div>
      )}

      <section className="notifications-list-card">
        {loading ? (
          <div className="notifications-empty">
            <span className="notifications-loader" />

            <strong>
              Loading notifications…
            </strong>
          </div>
        ) : items.length ? (
          items.map((item) => {
            const Icon = iconFor(
              item.notification_type
            );

            return (
              <article
                className={`notifications-list-row ${
                  item.is_read
                    ? "is-read"
                    : "is-unread"
                }`}
                key={item.id}
                onClick={() =>
                  handleNotificationClick(item)
                }
                role="button"
                tabIndex={0}
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    event.preventDefault();
                    handleNotificationClick(item);
                  }
                }}
              >
                <div
                  className={`notifications-list-icon ${toneFor(
                    item.notification_type
                  )}`}
                >
                  <Icon />
                </div>

                <div className="notifications-list-copy">
                  <div className="notifications-list-heading">
                    <strong>
                      {item.title}
                    </strong>

                    {!item.is_read && (
                      <span className="notifications-unread-label">
                        NEW
                      </span>
                    )}
                  </div>

                  <p>{item.message}</p>

                  <time dateTime={item.created_at}>
                    {timeLabel(item.created_at)}
                  </time>
                </div>

                <button
                  type="button"
                  className="notifications-delete"
                  aria-label={`Delete ${item.title}`}
                  onClick={(event) => {
                    event.stopPropagation();
                    remove(item.id);
                  }}
                  disabled={actionId === item.id}
                >
                  <FiTrash2 />
                </button>
              </article>
            );
          })
        ) : (
          <div className="notifications-empty">
            <div className="notifications-empty-icon">
              <FiBell />
            </div>

            <strong>
              No notifications yet
            </strong>

            <p>
              When donation activity changes, your
              updates will appear here.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}