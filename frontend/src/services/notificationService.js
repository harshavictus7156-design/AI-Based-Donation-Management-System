import api from "./api";

const normalizeList = (data) => {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.notifications)) return data.notifications;
  return [];
};

const getNotifications = async () => {
  const response = await api.get("notifications/");
  return normalizeList(response.data);
};

const getUnreadCount = async () => {
  const response = await api.get("notifications/unread-count/");
  return Number(response.data?.count ?? 0);
};

const markNotificationRead = async (id) => {
  const response = await api.patch(`notifications/${id}/read/`);
  return response.data;
};

const markAllNotificationsRead = async () => {
  const response = await api.patch("notifications/read-all/");
  return response.data;
};

const deleteNotification = async (id) => {
  await api.delete(`notifications/${id}/`);
};

export {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllNotificationsRead,
  deleteNotification,
};
