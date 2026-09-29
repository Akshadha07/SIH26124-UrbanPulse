import apiClient from './client';
import { SimulationStatusResponse } from '../types';

export interface ScenarioTriggerPayload {
  intensity?: number;
  corridor?: string;
}

export const getSimulationStatus = async (): Promise<SimulationStatusResponse> => {
  const response = await apiClient.get<SimulationStatusResponse>('/simulate/status');
  return response.data;
};

export const triggerScenario = async (name: string, payload: ScenarioTriggerPayload = { intensity: 1.0 }): Promise<any> => {
  const response = await apiClient.post('/simulate/scenario/' + name, payload);
  return response.data;
};

export const resetSimulation = async (): Promise<any> => {
  const response = await apiClient.post('/simulate/reset');
  return response.data;
};

export const advanceSimulationTick = async (): Promise<any> => {
  const response = await apiClient.post('/simulate/tick');
  return response.data;
};
