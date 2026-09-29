import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  ShieldCheck, 
  Camera, 
  Activity, 
  MapPin, 
  Calendar, 
  CheckCircle2, 
  AlertTriangle, 
  Layers, 
  Wrench,
  Flame,
  Radio,
  FileText
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getIncidentById, getIncidentEvidence, updateIncidentStatus } from '../api/incidents';
import { createWorkOrder } from '../api/workOrders';
import { HazardResponse, IncidentEvidenceResponse, EvidenceItemResponse } from '../types';

export const IncidentDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<HazardResponse | null>(null);
  const [evidenceData, setEvidenceData] = useState<IncidentEvidenceResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  const fetchDetails = async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const incId = parseInt(id, 10);
      const [inc, ev] = await Promise.all([
        getIncidentById(incId),
        getIncidentEvidence(incId),
      ]);
      setIncident(inc);
      setEvidenceData(ev);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load incident forensics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleStatusChange = async (newStatus: string) => {
    if (!incident) return;
    try {
      setIsUpdating(true);
      setActionMessage(null);
      await updateIncidentStatus(incident.id, newStatus);
      setActionMessage(`Status transitioned to: ${newStatus}`);
      await fetchDetails();
    } catch (err: any) {
      setActionMessage(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleCreateWorkOrder = async () => {
    if (!incident) return;
    try {
      setIsUpdating(true);
      setActionMessage(null);
      await createWorkOrder({
        incident_id: incident.id,
        title: `Municipal Repair: ${incident.hazard_type} at ${incident.address_hint || 'Vadodara'}`,
        department: 'VMC Roads & Infrastructure',
        assigned_to: 'Rapid Maintenance Squad 2',
        priority: incident.priority_score > 75 ? 'CRITICAL' : 'HIGH',
      });
      setActionMessage('Work order dispatched successfully to VMC Maintenance Crew');
      await fetchDetails();
    } catch (err: any) {
      setActionMessage(`Error creating work order: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={3} />
        <LoadingSkeleton rows={10} />
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="space-y-4">
        <Link to="/incidents" className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Incidents</span>
        </Link>
        <ErrorMessage message={error || 'Incident not found'} onRetry={fetchDetails} />
      </div>
    );
  }

  // Parse explanation if object or string
  const explanation = typeof incident.priority_explanation === 'object' && incident.priority_explanation !== null
    ? incident.priority_explanation
    : null;

  const isMultiSensor = Array.isArray(incident.sources) && incident.sources.length > 1;
  const isCorroborated = incident.distinct_bus_count > 1;
  const isDisaster = incident.status === 'ESCALATED_DISASTER' || incident.hazard_type === 'WATERLOGGING_CRITICAL';

  // Lifecycle steps
  const steps = [
    { key: 'reported', label: 'DETECTED' },
    { key: 'confirmed', label: 'CONFIRMED' },
    { key: 'in_progress', label: 'WORK ORDER / IN REPAIR' },
    { key: 'resolved', label: 'RESOLVED' },
    { key: 'verified_closed', label: 'VERIFIED CLOSED' },
  ];

  const currentStatus = incident.status.toLowerCase();
  const getStepIndex = () => {
    if (currentStatus === 'reported') return 0;
    if (currentStatus === 'confirmed') return 1;
    if (currentStatus === 'in_progress') return 2;
    if (currentStatus === 'resolved') return 3;
    if (currentStatus === 'verified_closed') return 4;
    if (currentStatus === 'escalated_disaster') return 1;
    return 0;
  };
  const activeStepIdx = getStepIndex();

  return (
    <div className="space-y-6">
      {/* Back link & Top Banner */}
      <div className="flex items-center justify-between">
        <Link
          to="/incidents"
          className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Return to Incident Inventory</span>
        </Link>

        <div className="flex items-center gap-2">
          {incident.is_simulated ? (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
              SIMULATED TELEMETRY
            </span>
          ) : (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
              FIELD SENSOR TELEMETRY
            </span>
          )}
        </div>
      </div>

      {/* Hero Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="text-xs font-mono text-slate-400">INCIDENT ID #{incident.id}</span>
              <StatusBadge status={incident.status} />
              {isDisaster && (
                <span className="text-[11px] font-bold text-rose-300 bg-rose-950/80 border border-rose-700 px-2 py-0.5 rounded-full flex items-center gap-1 animate-pulse">
                  <Flame className="w-3 h-3 text-rose-400" />
                  <span>ESCALATED TO DISASTER MANAGEMENT</span>
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white capitalize">
              {incident.hazard_type.replace(/_/g, ' ')}
            </h1>
            <div className="flex items-center gap-4 text-xs text-slate-400 mt-2 font-mono">
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-500" />
                <span>{incident.address_hint || `Coordinates: ${incident.lat.toFixed(5)}, ${incident.lon.toFixed(5)}`}</span>
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5 text-slate-500" />
                <span>Detected: {new Date(incident.first_detected_at).toLocaleString()}</span>
              </span>
            </div>
          </div>

          <div className="flex flex-col md:items-end gap-2 shrink-0">
            <div className="text-xs uppercase font-mono tracking-wider text-slate-400">
              Dynamic Priority Rating
            </div>
            <PriorityBadge score={incident.priority_score} size="md" />
          </div>
        </div>

        {/* Forensic Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6">
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-mono">Multi-Sensor Fusion</div>
            <div className="mt-1 flex items-center gap-1.5 font-bold text-sm text-cyan-400">
              <ShieldCheck className="w-4 h-4" />
              <span>{isMultiSensor ? 'CONFIRMED (2 MODALITIES)' : 'SINGLE MODALITY'}</span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-mono">Corroboration</div>
            <div className="mt-1 flex items-center gap-1.5 font-bold text-sm text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <span>{isCorroborated ? `CORROBORATED (${incident.distinct_bus_count} BUSES)` : '1 BUS TRANSIT'}</span>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-mono">Confidence Level</div>
            <div className="mt-1 text-sm font-bold text-white font-mono">
              {(incident.confidence * 100).toFixed(1)}% AI Certainty
            </div>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-mono">Structural Severity</div>
            <div className="mt-1 text-sm font-bold text-amber-400 font-mono">
              {incident.severity.toFixed(1)} / 5.0 Rating
            </div>
          </div>
        </div>
      </div>

      {/* Incident Lifecycle Timeline */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 font-mono">
          Municipal Resolution Lifecycle
        </h2>
        <div className="grid grid-cols-5 gap-2 relative">
          {steps.map((step, idx) => {
            const isCompleted = idx <= activeStepIdx;
            const isCurrent = idx === activeStepIdx;

            return (
              <div key={step.key} className="text-center">
                <div
                  className={`h-2 rounded-full mb-2 transition-all ${
                    isCompleted
                      ? 'bg-blue-500 shadow-md shadow-blue-500/30'
                      : 'bg-slate-800'
                  }`}
                />
                <div
                  className={`text-[11px] font-mono tracking-wider uppercase font-semibold ${
                    isCurrent
                      ? 'text-blue-400'
                      : isCompleted
                      ? 'text-slate-300'
                      : 'text-slate-600'
                  }`}
                >
                  {step.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Priority Explainability Breakdown */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-amber-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Explainable Priority Formula Breakdown
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Dynamic Score: {incident.priority_score.toFixed(1)} / 100.0
          </span>
        </div>

        {explanation ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">Base Severity Factor</div>
              <div className="text-lg font-bold text-white font-mono mt-1">
                {(explanation.base_severity || explanation.severity_component || 0).toFixed(1)} pts
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Structural depth/area</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">AI Confidence Multiplier</div>
              <div className="text-lg font-bold text-blue-400 font-mono mt-1">
                {(explanation.confidence_multiplier || explanation.confidence_component || 0).toFixed(1)} pts
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Model certainty penalty</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">Multi-Bus Corroboration</div>
              <div className="text-lg font-bold text-emerald-400 font-mono mt-1">
                {(explanation.multi_bus_component || 0).toFixed(1)} pts
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Independent passes</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">Multi-Sensor Agreement</div>
              <div className="text-lg font-bold text-cyan-400 font-mono mt-1">
                {(explanation.multi_sensor_component || 0).toFixed(1)} pts
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Camera + IMU alignment</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
              <div className="text-[11px] text-slate-400">Emergency / Waterlogging</div>
              <div className="text-lg font-bold text-rose-400 font-mono mt-1">
                {(explanation.waterlogging_bonus || 0).toFixed(1)} pts
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Fast-path disaster bonus</div>
            </div>
          </div>
        ) : (
          <div className="text-xs text-slate-400 py-3">
            Priority score computed natively by the backend sensor fusion engine based on multi-corridor transit density.
          </div>
        )}
      </div>

      {/* Forensic Evidence Trail */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Sensor Evidence Trail & Raw AI Observations ({evidenceData?.observations_count || 0} Linked)
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Source: Edge Telemetry Buffer
          </span>
        </div>

        {evidenceData && evidenceData.evidence && evidenceData.evidence.length > 0 ? (
          <div className="space-y-3">
            {evidenceData.evidence.map((obs) => {
              const isCamera = obs.observation_type.includes('CV') || obs.observation_type.includes('CAMERA');
              const isImu = obs.observation_type.includes('IMU');
              const isWater = obs.observation_type.includes('WATER');

              return (
                <div
                  key={obs.observation_id}
                  className="p-4 rounded-lg bg-slate-950/70 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4"
                >
                  <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-white">
                        Observation #{obs.observation_id}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 uppercase">
                        {obs.observation_type}
                      </span>
                      <span className="text-[10px] font-mono text-blue-400">
                        Bus: {obs.bus_id}
                      </span>
                    </div>

                    <div className="text-xs text-slate-300 font-sans">
                      Detected Class: <strong className="text-white">{obs.hazard_class}</strong> • Confidence: <strong className="text-emerald-400">{(obs.confidence * 100).toFixed(1)}%</strong>
                    </div>

                    {isCamera && obs.bounding_box && (
                      <div className="text-[11px] font-mono text-slate-400 bg-slate-900 p-2 rounded border border-slate-800 inline-block">
                        Bounding Box: {JSON.stringify(obs.bounding_box)}
                        {obs.evidence_ref && <span className="ml-3 text-cyan-400">Ref: {obs.evidence_ref}</span>}
                      </div>
                    )}

                    {isImu && obs.signal_features && (
                      <div className="text-[11px] font-mono text-slate-400 bg-slate-900 p-2 rounded border border-slate-800 inline-flex gap-4">
                        <span>Peak Accel: <strong className="text-white">{obs.signal_features.peak_z_g || obs.signal_features.peak_z || '--'} g</strong></span>
                        <span>RMS: <strong className="text-white">{obs.signal_features.rms_z?.toFixed(2) || '--'}</strong></span>
                        <span>Variance: <strong className="text-white">{obs.signal_features.variance_z?.toFixed(2) || '--'}</strong></span>
                      </div>
                    )}

                    {isWater && obs.signal_features && (
                      <div className="text-[11px] font-mono text-slate-400 bg-slate-900 p-2 rounded border border-slate-800 inline-flex gap-4">
                        <span>Reflection: <strong className="text-white">{obs.signal_features.water_reflection_ratio?.toFixed(2) || '--'}</strong></span>
                        <span>Surface Drag: <strong className="text-white">{obs.signal_features.surface_drag_index?.toFixed(2) || '--'}</strong></span>
                      </div>
                    )}
                  </div>

                  <div className="text-right text-[11px] font-mono text-slate-500 shrink-0">
                    <div>Model: {obs.model_name} (v{obs.model_version})</div>
                    <div>Offset: {obs.distance_to_centroid_meters.toFixed(1)}m from centroid</div>
                    <div>{new Date(obs.timestamp).toLocaleTimeString()}</div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-6 text-center text-xs text-slate-500 font-sans">
            Underlying sensor evidence items archived or running initial ingestion.
          </div>
        )}
      </div>

      {/* Officer Command Actions Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              Municipal Officer Action Dispatch
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Dispatch repair crew or trigger field pass-by verification
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={handleCreateWorkOrder}
              disabled={isUpdating}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition-colors"
            >
              <Wrench className="w-3.5 h-3.5" />
              <span>Create Work Order</span>
            </button>

            <button
              onClick={() => handleStatusChange('in_progress')}
              disabled={isUpdating || currentStatus === 'in_progress'}
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium border border-slate-700 transition-colors"
            >
              Mark In Progress
            </button>

            <button
              onClick={() => handleStatusChange('resolved')}
              disabled={isUpdating || currentStatus === 'resolved'}
              className="px-3 py-1.5 rounded-lg bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-300 text-xs font-medium border border-emerald-800/80 transition-colors"
            >
              Mark Repaired
            </button>

            <button
              onClick={() => handleStatusChange('verified_closed')}
              disabled={isUpdating || currentStatus === 'verified_closed'}
              className="px-3 py-1.5 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/80 text-indigo-300 text-xs font-medium border border-indigo-800/80 transition-colors"
            >
              Verify & Close Defect
            </button>
          </div>
        </div>

        {actionMessage && (
          <div className="mt-3 p-2.5 rounded bg-slate-950 border border-slate-800 text-xs font-mono text-slate-300 flex items-center gap-2">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{actionMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
};
