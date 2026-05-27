import api from './api'

export const getWorkOrders = () => api.get('work-orders/')

export const createWorkOrder = (data) => api.post('work-orders/', data)

export const updateWorkOrder = (id, data) => api.patch(`work-orders/${id}/`, data)

export const deleteWorkOrder = (id) => api.delete(`work-orders/${id}/`)

export const getStatuses = () => api.get('work-orders/status/')
