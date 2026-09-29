import apiClient from './client';
import { RoadHealthOverviewResponse } from '../types';

export const getRoadHealthOverview = async (simulationRunId?: string): Promise<RoadHealthOverviewResponse> => {
  const response = await apiClient.get<RoadHealthOverviewResponse>('/road-health', {
    params: simulationRunId ? { simulation_run_id: simulationRunId } : undefined,
  });
  return response.data;
};

export const calculateRoadHealth = async (simulationRunId?: string): Promise<RoadHealthOverviewResponse> => {
  const response = await apiClient.post<RoadHealthOverviewResponse>('/road-health/calculate', null, {
    params: simulationRunId ? { simulation_run_id: simulationRunId } : undefined,
  });
  return response.data;
};
