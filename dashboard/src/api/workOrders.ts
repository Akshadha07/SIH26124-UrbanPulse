import apiClient from './client';
import { WorkOrderResponse, WorkOrderCreate, WorkOrderStatusUpdate, VerificationAuditResponse } from '../types';

export const getWorkOrders = async (status?: string, priority?: string, incidentId?: number): Promise<WorkOrderResponse[]> => {
  const params: Record<string, any> = {};
  if (status) params.status = status;
  if (priority) params.priority = priority;
  if (incidentId !== undefined) params.incident_id = incidentId;
  const response = await apiClient.get<WorkOrderResponse[]>('/work-orders', { params });
  return response.data;
};

export const createWorkOrder = async (payload: WorkOrderCreate): Promise<WorkOrderResponse> => {
  const response = await apiClient.post<WorkOrderResponse>('/work-orders', payload);
  return response.data;
};

export const updateWorkOrderStatus = async (workOrderId: number, update: WorkOrderStatusUpdate): Promise<WorkOrderResponse> => {
  const response = await apiClient.patch<WorkOrderResponse>('/work-orders/' + workOrderId + '/status', update);
  return response.data;
};

export const getWorkOrderAudits = async (workOrderId: number): Promise<VerificationAuditResponse[]> => {
  const response = await apiClient.get<VerificationAuditResponse[]>('/work-orders/' + workOrderId + '/audit');
  return response.data;
};
