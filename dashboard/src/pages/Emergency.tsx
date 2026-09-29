import React, { useState, useEffect } from 'react';
import { 
  Flame, 
  AlertTriangle, 
  MapPin, 
  Clock, 
  PhoneCall, 
  ShieldAlert, 
  Layers, 
  Radio, 
  ArrowRight,
  Droplets
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { CommandMap } from '../components/maps/CommandMap';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getWaterloggingAlerts } from '../api/incidents';
import { triggerScenario } from '../api/simulation';
import { HazardResponse } from '../types';

interface EmergencyPageProps {
  subscribeWs: (eventType: string, handler: (envelope: any) => void) => () => void;
}

export const Emergency: React.FC<EmergencyPageProps> = ({ subscribeWs }) => {
  const [alerts, setAlerts] = useState<HazardResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isSimulatingFlood, setIsSimulatingFlood] = useState<boolean>(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const fetchAlerts = async () => {
    try {
      setError(null);
      const data = await getWaterloggingAlerts();
      setAlerts(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to connect to Disaster Management feed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();

    const unsubAlert = subscribeWs('waterlogging_alert', () => {
      fetchAlerts();
    });

    return () => {
      unsubAlert();
    };
  }, [subscribeWs]);

  const handleTriggerMonsoonFlood = async () => {
    try {
      setIsSimulatingFlood(true);
      setActionNotice(null);
      await triggerScenario('monsoon_flood', { intensity: 1.5 });
      setActionNotice('Simulated monsoon flash-flood triggered on Akota Underpass');
      await fetchAlerts();
    } catch (err: any) {
      setActionNotice(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsSimulatingFlood(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={2} />
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchAlerts} />;
  }

  return (
    <div className="space-y-6">
      {/* Emergency Flash Header */}
      <div className="p-6 rounded-xl border border-rose-800 bg-gradient-to-r from-rose-950/80 via-slate-950 to-slate-900 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-mono font-bold text-rose-400 uppercase tracking-widest mb-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>
            <span>VMC Disaster Management Command Center</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Flame className="w-6 h-6 text-rose-500 animate-pulse" />
            <span>Critical Urban Waterlogging Emergency Console</span>
          </h1>
          <p className="text-xs text-rose-200/80 mt-1 max-w-2xl font-sans">
            Autonomous multi-modal detection of flash flooding, road submersion, and hydroplaning hazards via public transit fleet cameras and optical sensors.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0">
          <button
            onClick={handleTriggerMonsoonFlood}
            disabled={isSimulatingFlood}
            className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold shadow-lg shadow-rose-900/40 transition-colors"
          >
            <Droplets className="w-4 h-4" />
            <span>{isSimulatingFlood ? 'Simulating Flood...' : 'Simulate Monsoon Flood'}</span>
          </button>
        </div>
      </div>

      {actionNotice && (
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300">
          {actionNotice}
        </div>
      )}

      {/* Main Map + Alert Queue */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-200 flex items-center gap-2 font-mono">
              <Radio className="w-4 h-4 text-rose-400 animate-pulse" />
              <span>Vadodara Flood Zone Telemetry Map</span>
            </h2>
            <span className="text-xs text-rose-300 font-mono font-semibold bg-rose-950/80 px-2 py-0.5 rounded border border-rose-800">
              {alerts.length} Critical Submersion Zones
            </span>
          </div>

          <div className="rounded-xl overflow-hidden border border-rose-900/60 shadow-2xl bg-[#060a12] tactical-border-rose">
            <CommandMap
              incidents={alerts}
              height="540px"
            />
          </div>
        </div>

        {/* Emergency Alerts Column */}
        <div className="space-y-4">
          <div className="bg-slate-900/90 border border-rose-900/40 rounded-xl p-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-xs font-bold uppercase tracking-widest text-rose-400 flex items-center gap-2 font-mono">
                <ShieldAlert className="w-4 h-4" />
                <span>Escalated Disasters</span>
              </h2>
              <span className="text-[10px] font-mono font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                Priority &ge; 90
              </span>
            </div>

            <div className="mt-3 space-y-3 max-h-[460px] overflow-y-auto pr-1">
              {alerts.length === 0 ? (
                <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl text-slate-400 text-xs font-sans">
                  No active critical waterlogging emergencies reported. All underpasses and low-lying transit corridors operating nominally.
                </div>
              ) : (
                alerts.map((al) => (
                  <div
                    key={al.id}
                    className="p-4 rounded-xl bg-gradient-to-b from-rose-950/50 to-slate-950/90 border border-rose-700/80 shadow-lg space-y-2.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-600/30 text-rose-300 border border-rose-600/50 uppercase">
                        {al.status}
                      </span>
                      <PriorityBadge score={al.priority_score} size="sm" />
                    </div>

                    <div>
                      <div className="text-sm font-bold text-white capitalize font-sans">
                        {al.hazard_type.replace(/_/g, ' ')}
                      </div>
                      <div className="text-xs text-slate-300 mt-0.5 font-sans">
                        {al.address_hint || `Coordinates: ${al.lat.toFixed(4)}, ${al.lon.toFixed(4)}`}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400 pt-2 border-t border-rose-900/60">
                      <div>
                        Severity: <strong className="text-rose-300">{al.severity.toFixed(1)}/5.0</strong>
                      </div>
                      <div>
                        Confidence: <strong className="text-white">{(al.confidence * 100).toFixed(0)}%</strong>
                      </div>
                      <div>
                        Corroboration: <strong className="text-emerald-400 font-semibold">{al.distinct_bus_count} Buses</strong>
                      </div>
                      <div>
                        Level: <strong className="text-rose-400">{al.waterlogging_severity || 'CRITICAL'}</strong>
                      </div>
                    </div>

                    <div className="pt-2 flex items-center justify-between border-t border-rose-900/60">
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(al.last_detected_at).toLocaleTimeString()}
                      </span>
                      <Link
                        to={`/incidents/${al.id}`}
                        className="inline-flex items-center gap-1 text-xs text-rose-300 hover:text-white font-semibold transition-colors"
                      >
                        <span>Forensics Dossier</span>
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Standard Operating Procedure Drawer */}
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-2.5">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-1.5">
              <PhoneCall className="w-3.5 h-3.5 text-sky-400" />
              <span>Standard Operating Procedures</span>
            </div>
            <ul className="text-[11px] text-slate-400 space-y-1.5 list-disc pl-4 font-sans">
              <li>Deploy high-capacity de-watering pumps to Akota Underpass</li>
              <li>Coordinate transit route rerouting via VMC Transit Dispatch</li>
              <li>Broadcast flash advisory to Citizen UrbanPulse Mobile App</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

