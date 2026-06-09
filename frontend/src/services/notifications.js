import api from './api'

export const getNotifications = () => {
  return api.get('notifications/', { headers: { 'X-Silent': 'true' } })
}

export const markAsRead = (id) => {
  return api.patch(`notifications/${id}/mark_as_read/`)
}

export const markAllAsRead = () => {
  return api.patch('notifications/mark_all_as_read/', {}, { headers: { 'X-Silent': 'true' } })
}
