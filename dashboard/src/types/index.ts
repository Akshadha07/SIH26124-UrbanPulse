export type HazardType = 
  | 'pothole' 
  | 'road_crack' 
  | 'waterlogging' 
  | 'WATERLOGGING_CRITICAL' 
  | 'garbage_dump' 
  | 'debris' 
  | 'street_light_issue';

export type HazardStatus = 
  | 'reported' 
  | 'confirmed' 
  | 'in_progress' 
  | 'resolved' 
  | 'verified_closed'
  | 'ESCALATED_DISASTER';

export interface BusLiveResponse {
  bus_id: string;
  route_id: string;
  route_name: string;
  lat: number;
  lon: number;
  speed: number;
  heading: number;
  occupancy_level: string;
  crowd_count: number;
  capacity: number;
  status: string;
  last_updated: string;
}

export interface Waypoint {
  lat: number;
  lon: number;
  stop_name?: string | null;
}

export interface RouteResponse {
  route_id: string;
  route_name: string;
  color: string;
  stops: Waypoint[];
  coordinates: [number, number][]; // [lat, lon] for Leaflet
}

export interface EvidenceItemResponse {
  observation_id: number;
  observation_type: string;
  hazard_class: string;
  confidence: number;
  severity_score: number;
  bus_id: string;
  model_name: string;
  model_version: string;
  evidence_ref?: string | null;
  bounding_box?: {
    x?: number;
    y?: number;
    w?: number;
    h?: number;
    [key: string]: any;
  } | null;
  signal_features?: {
    peak_z_g?: number;
    rms_z?: number;
    variance_z?: number;
    anomaly_score?: number;
    water_reflection_ratio?: number;
    surface_drag_index?: number;
    rainfall_coincident?: boolean;
    [key: string]: any;
  } | null;
  distance_to_centroid_meters: number;
  timestamp: string;
  raw_event_id?: number | null;
}

export interface PriorityExplanation {
  base_severity?: number;
  confidence_multiplier?: number;
  traffic_multiplier?: number;
  ward_vulnerability?: number;
  repeat_failure_penalty?: number;
  final_priority_score?: number;
  [key: string]: any;
}

export interface HazardResponse {
  id: number;
  hazard_type: string;
  lat: number;
  lon: number;
  severity: number;
  waterlogging_severity?: string | null;
  confidence: number;
  confirmation_count: number;
  distinct_bus_count: number;
  is_confirmed: boolean;
  status: string;
  priority_score: number;
  priority_explanation?: PriorityExplanation | string | null;
  first_detected_at: string;
  last_detected_at: string;
  detected_by_buses: string[];
  sources: string[];
  address_hint?: string | null;
  verification_passes: number;
  resolved_at?: string | null;
  is_simulated: boolean;
  simulation_run_id?: string | null;
}

export interface IncidentEvidenceResponse {
  incident_id: number;
  hazard_type: string;
  lat: number;
  lon: number;
  severity: number;
  confidence: number;
  is_confirmed: boolean;
  status: string;
  priority_score: number;
  priority_explanation?: PriorityExplanation | null;
  distinct_bus_count: number;
  detected_by_buses: string[];
  sources: string[];
  observations_count: number;
  evidence: EvidenceItemResponse[];
}

export interface RoadHealthSegmentOverview {
  segment_code: string;
  corridor_name: string;
  health_score: number;
  rating: string; // Good (80-100), Fair (60-79), Poor (40-59), Critical (<40)
  roughness_index: number;
  defect_density: number;
  confirmed_defects_count: number;
  start_lat: number;
  start_lon: number;
  end_lat: number;
  end_lon: number;
  last_assessed_at: string;
}

export interface RoadHealthOverviewResponse {
  city: string;
  overall_city_index: number;
  total_segments_monitored: number;
  segments: RoadHealthSegmentOverview[];
}

export interface AQIPointResponse {
  id: number;
  bus_id: string;
  lat: number;
  lon: number;
  pm2_5: number;
  pm10?: number | null;
  co2?: number | null;
  aqi_value: number;
  category: string;
  timestamp: string;
}

export interface AQIHeatmapResponse {
  total_points: number;
  city_average_aqi: number;
  overall_category: string;
  readings: AQIPointResponse[];
}

export interface WorkOrderResponse {
  id: number;
  incident_id: number;
  title: string;
  department: string;
  assigned_to: string;
  location_hint?: string | null;
  lat: number;
  lon: number;
  priority: string;
  status: string; // ASSIGNED, IN_REPAIR, RESOLVED, VERIFIED
  notes?: string | null;
  created_at: string;
  updated_at: string;
  is_simulated: boolean;
  simulation_run_id?: string | null;
}

export interface WorkOrderCreate {
  incident_id: number;
  title?: string;
  department?: string;
  assigned_to?: string;
  priority?: string;
  notes?: string;
}

export interface WorkOrderStatusUpdate {
  status: string;
  notes?: string;
}

export interface VerificationAuditResponse {
  id: number;
  work_order_id: number;
  incident_id: number;
  bus_id: string;
  verification_timestamp: string;
  vibration_peak_g: number;
  visual_defect_detected: boolean;
  verdict: string;
  notes?: string | null;
}

export interface SimulationStatusResponse {
  simulation_run_id: string;
  is_running: boolean;
  bus_count: number;
  interval_seconds: number;
  active_scenario?: string | null;
  seed: number;
  total_ticks: number;
}

export interface WebSocketEnvelope<T = any> {
  event_type: 'bus_moved' | 'incident_detected' | 'incident_confirmed' | 'waterlogging_alert' | 'work_order_updated' | 'verification_completed';
  timestamp: string;
  data: T;
}
