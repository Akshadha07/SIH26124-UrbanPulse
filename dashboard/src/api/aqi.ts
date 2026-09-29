import apiClient from './client';
import { AQIPointResponse, AQIHeatmapResponse } from '../types';

export const getLiveAQI = async (limit: number = 50): Promise<AQIPointResponse[]> => {
  const response = await apiClient.get<AQIPointResponse[]>('/aqi/live', {
    params: { limit },
  });
  return response.data;
};

export const getAQIGrid = async (): Promise<AQIHeatmapResponse> => {
  const response = await apiClient.get<AQIHeatmapResponse>('/aqi/grid');
  return response.data;
};

export const getAQIHotspots = async (thresholdPm25: number = 100, limit: number = 25): Promise<AQIPointResponse[]> => {
  const response = await apiClient.get<AQIPointResponse[]>('/aqi/hotspots', {
    params: { threshold_pm25: thresholdPm25, limit },
  });
  return response.data;
};
