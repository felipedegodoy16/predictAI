import api from './api'

export const getWorkOrders = (options = {}) => api.get('work-orders/', options)

export const createWorkOrder = (data, options = {}) => api.post('work-orders/', data, options)

export const updateWorkOrder = (id, data, options = {}) => api.patch(`work-orders/${id}/`, data, options)

export const moveWorkOrderStatus = (id, newStatusId) =>
  api.patch(`work-orders/${id}/move_status/`, { status: newStatusId }, { headers: { 'X-Silent': 'true' } })

export const deleteWorkOrder = (id, options = {}) => api.delete(`work-orders/${id}/`, options)

export const getStatuses = (options = {}) => api.get('work-orders/status/', options)

