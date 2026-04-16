import api from './api'

export const getNotifications = () => {
  return api.get('notifications/')
}

export const markAsRead = (id) => {
  return api.patch(`notifications/${id}/mark_as_read/`)
}
