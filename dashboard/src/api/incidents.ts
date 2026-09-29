import apiClient from './client';
import { HazardResponse, IncidentEvidenceResponse } from '../types';

export interface IncidentFilterParams {
  incident_type?: string;
  status?: string;
  severity_min?: number;
  priority_min?: number;
  waterlogging_severity?: string;
  is_simulated?: boolean;
}

export const getIncidents = async (params?: IncidentFilterParams): Promise<HazardResponse[]> => {
  const response = await apiClient.get<HazardResponse[]>('/incidents', { params });
  return response.data;
};

export const getIncidentById = async (id: number): Promise<HazardResponse> => {
  const response = await apiClient.get<HazardResponse>('/incidents/' + id);
  return response.data;
};

export const getIncidentEvidence = async (id: number): Promise<IncidentEvidenceResponse> => {
  const response = await apiClient.get<IncidentEvidenceResponse>('/incidents/' + id + '/evidence');
  return response.data;
};

export const updateIncidentStatus = async (id: number, status: string): Promise<HazardResponse> => {
  const response = await apiClient.patch<HazardResponse>('/incidents/' + id + '/status', { status });
  return response.data;
};

export const getWaterloggingAlerts = async (): Promise<HazardResponse[]> => {
  const response = await apiClient.get<HazardResponse[]>('/incidents/waterlogging-alerts');
  return response.data;
};

export const triggerFusionCycle = async (simulationRunId?: string): Promise<any> => {
  const response = await apiClient.post('/incidents/fuse', null, {
    params: simulationRunId ? { simulation_run_id: simulationRunId } : undefined,
  });
  return response.data;
};
