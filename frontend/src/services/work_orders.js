import api from './api'

export const getWorkOrders = () => {
  return api.get('work-orders/')
}

export const createWorkOrder = (data) => {
  return api.post('work-orders/', data)
}

export const updateWorkOrder = (id, data) => {
  return api.patch(`work-orders/${id}/`, data)
}

export const deleteWorkOrder = (id) => {
  return api.delete(`work-orders/${id}/`)
}

export const getStatuses = () => {
  return api.get('work-orders/status/')
}

export const getErrorTypes = () => {
  return api.get('work-orders/error-types/')
}
