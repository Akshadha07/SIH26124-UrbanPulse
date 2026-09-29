import apiClient from './client';
import { BusLiveResponse, RouteResponse } from '../types';

export const getLiveFleet = async (): Promise<BusLiveResponse[]> => {
  const response = await apiClient.get<BusLiveResponse[]>('/fleet/live');
  return response.data;
};

export const getFleetRoutes = async (): Promise<RouteResponse[]> => {
  const response = await apiClient.get<RouteResponse[]>('/fleet/routes');
  return response.data;
};

export const getBusById = async (busId: string): Promise<BusLiveResponse> => {
  const response = await apiClient.get<BusLiveResponse>('/fleet/' + busId);
  return response.data;
};
