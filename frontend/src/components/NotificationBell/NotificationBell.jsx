import { useCallback, useEffect, useRef, useState } from "react";
import { FiBell, FiCheck, FiTrash2 } from "react-icons/fi";
import { useNavigate } from "react-router-dom";

import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
} from "../../services/notificationService";

import "./NotificationBell.css";

const iconFor = (type) => {
  if (type?.includes("MATCH")) return "🤖";
  if (type?.includes("PICKUP")) return "🚚";
  if (type?.includes("ALLOCATED")) return "📦";
  if (type?.includes("APPROVED")) return "✅";
  if (type?.includes("REJECTED") || type?.includes("CANCELLED")) return "❌";
  if (type?.includes("DELIVERED") || type?.includes("COLLECTED")) return "✅";
  if (type?.includes("REQUEST")) return "📋";
  return "🎁";
};

const timeAgo = (value) => {
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
    return `${minutes}m ago`;
  }

  const hours = Math.floor(minutes / 60);

  if (hours < 24) {
    return `${hours}h ago`;
  }

  const days = Math.floor(hours / 24);

  if (days < 7) {
    return `${days}d ago`;
  }

  return date.toLocaleDateString();
};

export function NotificationBell({
  route = "/notifications",
  className = "",
}) {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [actionId, setActionId] = useState(null);
  const [error, setError] = useState("");

  const ref = useRef(null);
  const navigate = useNavigate();

  const refreshCount = useCallback(async () => {
    if (!localStorage.getItem("access")) return;

    try {
      const unreadCount = await getUnreadCount();
      setCount(unreadCount);
    } catch {
      // Existing API interceptor handles authentication failures.
    }
  }, []);

  const loadRecent = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getNotifications();

      setItems(data.slice(0, 6));

      await refreshCount();
    } catch {
      setError("Unable to load notifications.");
    } finally {
      setLoading(false);
    }
  }, [refreshCount]);

  useEffect(() => {
    refreshCount();

    const timer = window.setInterval(
      refreshCount,
      30000
    );

    return () => window.clearInterval(timer);
  }, [refreshCount]);

  useEffect(() => {
    const close = (event) => {
      if (
        ref.current &&
        !ref.current.contains(event.target)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", close);

    return () => {
      document.removeEventListener("mousedown", close);
    };
  }, []);

  const toggle = async () => {
    const next = !open;

    setOpen(next);

    if (next) {
      await loadRecent();
    }
  };

  const markRead = async (item) => {
    if (
      item.is_read ||
      actionId === item.id
    ) {
      return;
    }

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

      setCount((current) =>
        Math.max(0, current - 1)
      );
    } catch {
      setError(
        "Unable to update this notification."
      );
    } finally {
      setActionId(null);
    }
  };

  /*
   * Handle notification click.
   *
   * 1. Mark notification as read.
   * 2. Navigate to the most relevant existing page.
   */
  const handleNotificationClick = async (item) => {
    try {
      await markRead(item);

      /*
       * DONOR NOTIFICATIONS
       */
      switch (item.notification_type) {
        case "DONATION_SUBMITTED":
        case "DONATION_APPROVED":
        case "DONATION_REJECTED":
        case "DONATION_COLLECTED":
        case "DONATION_MATCHED":
          navigate("/my-donations");
          break;

        /*
         * NGO REQUIREMENT MATCH
         */
        case "REQUEST_MATCHED":
          navigate("/ngo-requirements");
          break;

        /*
         * RESOURCE ALLOCATION
         */
        case "RESOURCE_ALLOCATED":
          navigate("/ngo-allocations");
          break;

        /*
         * PICKUP RELATED
         */
        case "PICKUP_CREATED":
        case "PICKUP_CONFIRMED":
        case "PICKUP_DISPATCHED":
        case "DONATION_DELIVERED":
        case "PICKUP_CANCELLED":
          navigate("/my-activity");
          break;

        /*
         * Fallback
         */
        default:
          navigate(route);
          break;
      }

      setOpen(false);
    } catch (error) {
      console.error(
        "Unable to open notification:",
        error
      );
    }
  };

  const markAll = async () => {
    setActionId("all");

    try {
      await markAllNotificationsRead();

      setItems((current) =>
        current.map((item) => ({
          ...item,
          is_read: true,
        }))
      );

      setCount(0);
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
      await deleteNotification(id);

      setItems((current) =>
        current.filter(
          (item) => item.id !== id
        )
      );

      await refreshCount();
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
      className={`notification-bell-wrap ${className}`}
      ref={ref}
    >
      <button
        type="button"
        className="notification-bell-button"
        aria-label={`Notifications${
          count
            ? `, ${count} unread`
            : ""
        }`}
        aria-expanded={open}
        onClick={toggle}
      >
        <FiBell />

        {count > 0 && (
          <span className="notification-bell-count">
            {count > 99 ? "99+" : count}
          </span>
        )}
      </button>

      {open && (
        <div className="notification-popover">
          <div className="notification-popover-header">
            <div>
              <strong>
                Notifications
              </strong>

              <span>
                {count
                  ? `${count} unread`
                  : "All caught up"}
              </span>
            </div>

            {count > 0 && (
              <button
                type="button"
                className="notification-text-action"
                onClick={markAll}
                disabled={actionId === "all"}
              >
                <FiCheck />
                Mark all read
              </button>
            )}
          </div>

          {loading ? (
            <div className="notification-state">
              Loading notifications…
            </div>
          ) : error ? (
            <div className="notification-state notification-error">
              {error}
            </div>
          ) : items.length ? (
            <div className="notification-popover-list">
              {items.map((item) => (
                <article
                  className={`notification-popover-item ${
                    item.is_read
                      ? "read"
                      : "unread"
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

                      handleNotificationClick(
                        item
                      );
                    }
                  }}
                >
                  <div className="notification-popover-icon">
                    {iconFor(
                      item.notification_type
                    )}
                  </div>

                  <div className="notification-popover-copy">
                    <strong>
                      {item.title}
                    </strong>

                    <p>
                      {item.message}
                    </p>

                    <small>
                      {timeAgo(
                        item.created_at
                      )}
                    </small>
                  </div>

                  <button
                    type="button"
                    className="notification-delete"
                    aria-label={`Delete ${item.title}`}
                    onClick={(event) => {
                      event.stopPropagation();

                      remove(item.id);
                    }}
                    disabled={
                      actionId === item.id
                    }
                  >
                    <FiTrash2 />
                  </button>

                  {!item.is_read && (
                    <span className="notification-unread-dot" />
                  )}
                </article>
              ))}
            </div>
          ) : (
            <div className="notification-state">
              <FiBell />

              <strong>
                No notifications yet
              </strong>

              <span>
                Donation and activity updates
                will appear here.
              </span>
            </div>
          )}

          <button
            type="button"
            className="notification-view-all"
            onClick={() => {
              setOpen(false);
              navigate(route);
            }}
          >
            View all notifications
          </button>
        </div>
      )}
    </div>
  );
}