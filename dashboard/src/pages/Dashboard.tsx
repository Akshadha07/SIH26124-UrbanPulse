import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Flame, 
  Bus, 
  Activity, 
  Wind, 
  ClipboardList, 
  Radio, 
  ArrowRight,
  TrendingUp
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { KpiCard } from '../components/common/KpiCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { CommandMap } from '../components/maps/CommandMap';
import { DemoControl } from '../components/simulation/DemoControl';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getLiveFleet, getFleetRoutes } from '../api/fleet';
import { getIncidents, getWaterloggingAlerts } from '../api/incidents';
import { getRoadHealthOverview } from '../api/roadHealth';
import { getLiveAQI, getAQIHotspots } from '../api/aqi';
import { getWorkOrders } from '../api/workOrders';
import { getSimulationStatus } from '../api/simulation';
import { 
  BusLiveResponse, 
  HazardResponse, 
  RouteResponse, 
  RoadHealthOverviewResponse, 
  AQIPointResponse, 
  WorkOrderResponse,
  SimulationStatusResponse
} from '../types';

interface DashboardPageProps {
  subscribeWs: (eventType: string, handler: (envelope: any) => void) => () => void;
}

export const Dashboard: React.FC<DashboardPageProps> = ({ subscribeWs }) => {
  const [buses, setBuses] = useState<BusLiveResponse[]>([]);
  const [routes, setRoutes] = useState<RouteResponse[]>([]);
  const [incidents, setIncidents] = useState<HazardResponse[]>([]);
  const [criticalAlerts, setCriticalAlerts] = useState<HazardResponse[]>([]);
  const [roadHealth, setRoadHealth] = useState<RoadHealthOverviewResponse | null>(null);
  const [aqiPoints, setAqiPoints] = useState<AQIPointResponse[]>([]);
  const [workOrders, setWorkOrders] = useState<WorkOrderResponse[]>([]);
  const [simStatus, setSimStatus] = useState<SimulationStatusResponse | null>(null);
  const [activityFeed, setActivityFeed] = useState<Array<{ id: string; time: string; text: string; type: string }>>([]);

  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setError(null);
      const [
        fleetData,
        routesData,
        incidentsData,
        alertsData,
        healthData,
        aqiData,
        ordersData,
        statusData,
      ] = await Promise.all([
        getLiveFleet(),
        getFleetRoutes(),
        getIncidents(),
        getWaterloggingAlerts(),
        getRoadHealthOverview(),
        getLiveAQI(50),
        getWorkOrders(),
        getSimulationStatus(),
      ]);

      setBuses(fleetData);
      setRoutes(routesData);
      setIncidents(incidentsData);
      setCriticalAlerts(alertsData);
      setRoadHealth(healthData);
      setAqiPoints(aqiData);
      setWorkOrders(ordersData);
      setSimStatus(statusData);
    } catch (err: any) {
      console.error('Failed to load dashboard telemetry:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to connect to municipal backend');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    // Subscribe to live WebSocket feeds
    const unsubBus = subscribeWs('bus_moved', (envelope) => {
      if (envelope.data?.active_buses) {
        setBuses((prev) => {
          const updated = [...prev];
          envelope.data.active_buses.forEach((b: any) => {
            const idx = updated.findIndex((x) => x.bus_id === b.bus_id);
            if (idx >= 0) {
              updated[idx] = { ...updated[idx], ...b, last_updated: envelope.timestamp };
            }
          });
          return updated;
        });
      }
    });

    const unsubIncident = subscribeWs('incident_detected', (envelope) => {
      setActivityFeed((prev) => [
        {
          id: Math.random().toString(),
          time: new Date().toLocaleTimeString(),
          text: `New hazard detected: ${envelope.data?.hazard_type || 'Unknown'} by ${envelope.data?.bus_id || 'fleet sensor'}`,
          type: 'incident',
        },
        ...prev.slice(0, 15),
      ]);
      getIncidents().then(setIncidents).catch(() => {});
    });

    const unsubConfirmed = subscribeWs('incident_confirmed', (envelope) => {
      setActivityFeed((prev) => [
        {
          id: Math.random().toString(),
          time: new Date().toLocaleTimeString(),
          text: `Corroborated incident #${envelope.data?.incident_id} (Priority: ${envelope.data?.priority_score || 'N/A'})`,
          type: 'confirmed',
        },
        ...prev.slice(0, 15),
      ]);
      getIncidents().then(setIncidents).catch(() => {});
    });

    const unsubAlert = subscribeWs('waterlogging_alert', (envelope) => {
      setActivityFeed((prev) => [
        {
          id: Math.random().toString(),
          time: new Date().toLocaleTimeString(),
          text: `🚨 CRITICAL WATERLOGGING: Incident #${envelope.data?.incident_id} escalated to Disaster Authority!`,
          type: 'critical',
        },
        ...prev.slice(0, 15),
      ]);
      getWaterloggingAlerts().then(setCriticalAlerts).catch(() => {});
      getIncidents().then(setIncidents).catch(() => {});
    });

    const unsubWo = subscribeWs('work_order_updated', (envelope) => {
      setActivityFeed((prev) => [
        {
          id: Math.random().toString(),
          time: new Date().toLocaleTimeString(),
          text: `Work order #${envelope.data?.work_order_id} status transitioned to ${envelope.data?.status}`,
          type: 'work_order',
        },
        ...prev.slice(0, 15),
      ]);
      getWorkOrders().then(setWorkOrders).catch(() => {});
    });

    const unsubVerify = subscribeWs('verification_completed', (envelope) => {
      setActivityFeed((prev) => [
        {
          id: Math.random().toString(),
          time: new Date().toLocaleTimeString(),
          text: `✅ Pass-by verification: Bus ${envelope.data?.bus_id} verified repair on #${envelope.data?.incident_id}`,
          type: 'verify',
        },
        ...prev.slice(0, 15),
      ]);
      getIncidents().then(setIncidents).catch(() => {});
      getRoadHealthOverview().then(setRoadHealth).catch(() => {});
    });

    return () => {
      unsubBus();
      unsubIncident();
      unsubConfirmed();
      unsubAlert();
      unsubWo();
      unsubVerify();
    };
  }, [subscribeWs]);

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={2} />
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchDashboardData} />;
  }

  const activeIncidents = incidents.filter(
    (i) => i.status !== 'resolved' && i.status !== 'verified_closed'
  );
  const openWorkOrders = workOrders.filter(
    (w) => w.status !== 'RESOLVED' && w.status !== 'VERIFIED'
  );

  const avgAqi = aqiPoints.length > 0
    ? (aqiPoints.reduce((acc, p) => acc + p.aqi_value, 0) / aqiPoints.length).toFixed(0)
    : 'N/A';

  return (
    <div className="space-y-6">
      {/* Top 6 KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        <KpiCard
          title="Active Incidents"
          value={activeIncidents.length}
          subtitle={`${incidents.length} total recorded`}
          icon={AlertTriangle}
          badgeText={activeIncidents.length > 0 ? 'NEEDS ACTION' : 'CLEAR'}
          badgeType={activeIncidents.length > 0 ? 'warning' : 'success'}
        />

        <KpiCard
          title="Critical Alerts"
          value={criticalAlerts.length}
          subtitle="Disaster Management"
          icon={Flame}
          badgeText={criticalAlerts.length > 0 ? 'EMERGENCY' : 'NOMINAL'}
          badgeType={criticalAlerts.length > 0 ? 'danger' : 'success'}
        />

        <KpiCard
          title="Active Buses"
          value={buses.length}
          subtitle="6 Vadodara Corridors"
          icon={Bus}
          badgeText="BEL SENSORS"
          badgeType="info"
        />

        <KpiCard
          title="City Road Health"
          value={roadHealth ? `${roadHealth.overall_city_index.toFixed(1)}%` : '--'}
          subtitle={`${roadHealth?.total_segments_monitored || 6} monitored corridors`}
          icon={Activity}
          badgeText={roadHealth && roadHealth.overall_city_index > 75 ? 'OPTIMAL' : 'DEGRADED'}
          badgeType={roadHealth && roadHealth.overall_city_index > 75 ? 'success' : 'warning'}
        />

        <KpiCard
          title="Current AQI"
          value={avgAqi}
          subtitle="Mobile Sensor Average"
          icon={Wind}
          badgeText={Number(avgAqi) > 100 ? 'MODERATE' : 'GOOD'}
          badgeType={Number(avgAqi) > 100 ? 'warning' : 'success'}
        />

        <KpiCard
          title="Open Work Orders"
          value={openWorkOrders.length}
          subtitle={`${workOrders.length} total municipal orders`}
          icon={ClipboardList}
          badgeText={openWorkOrders.length > 0 ? 'IN PROGRESS' : 'ALL CLEAR'}
          badgeType={openWorkOrders.length > 0 ? 'default' : 'success'}
        />
      </div>

      {/* Main Command Section: Hero Geospatial Map (Left) + Priority Hazards (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-200 flex items-center gap-2 font-mono">
              <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
              <span>Vadodara Metropolitan Telemetry Map</span>
            </h2>
            <div className="flex items-center gap-3 text-xs text-slate-400 font-mono">
              <span>{buses.length} Active Transponders</span>
              <span className="text-slate-600">•</span>
              <span>{routes.length} Corridors</span>
            </div>
          </div>

          <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-[#060a12]">
            <CommandMap
              buses={buses}
              incidents={activeIncidents}
              routes={routes}
              height="600px"
            />
          </div>
        </div>

        {/* Priority Hazards & Disaster Escalation Drawer */}
        <div className="space-y-4">
          <div className="bg-slate-900/90 border border-slate-800/90 rounded-xl p-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h2 className="text-xs font-bold uppercase tracking-widest text-slate-200 flex items-center gap-2 font-mono">
                <Flame className="w-4 h-4 text-rose-500" />
                <span>Priority Hazards</span>
              </h2>
              <Link
                to="/incidents"
                className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1 font-semibold"
              >
                <span>Full Inventory</span>
                <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="mt-3 space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
              {activeIncidents.length === 0 ? (
                <div className="p-8 text-center border border-slate-800/80 rounded-xl text-slate-400 text-xs">
                  No active incidents detected. All monitored corridors operating nominally.
                </div>
              ) : (
                activeIncidents.slice(0, 6).map((inc) => (
                  <Link
                    key={inc.id}
                    to={`/incidents/${inc.id}`}
                    className="block p-3 rounded-lg bg-slate-950/80 border border-slate-800/90 hover:border-slate-700 hover:bg-slate-850/80 transition-all"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-semibold text-xs text-white uppercase tracking-wide">
                        {inc.hazard_type.replace(/_/g, ' ')}
                      </span>
                      <PriorityBadge score={inc.priority_score} size="sm" />
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                      <span className="truncate max-w-[170px]">{inc.address_hint || `(${inc.lat.toFixed(4)}, ${inc.lon.toFixed(4)})`}</span>
                      <StatusBadge status={inc.status} size="sm" />
                    </div>

                    <div className="flex items-center justify-between text-[10px] text-slate-400 pt-2 border-t border-slate-800/60 font-mono">
                      <span className={inc.distinct_bus_count > 1 ? 'text-emerald-400 font-semibold' : ''}>
                        {inc.distinct_bus_count > 1 ? `✓ ${inc.distinct_bus_count} Buses Corroborated` : `${inc.distinct_bus_count} Bus Detection`}
                      </span>
                      <span>Conf: {(inc.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </Link>
                ))
              )}
            </div>
          </div>

          {/* Emergency Fast-Path Notice */}
          {criticalAlerts.length > 0 && (
            <div className="p-4 rounded-xl border border-rose-700/80 bg-rose-950/30 text-rose-200 tactical-border-rose">
              <div className="flex items-center gap-2 font-bold text-xs uppercase tracking-wider mb-1 font-mono">
                <Flame className="w-4 h-4 text-rose-400 animate-pulse" />
                <span>DISASTER ESCALATION ACTIVE</span>
              </div>
              <p className="text-xs text-rose-200/90 mb-3">
                {criticalAlerts.length} critical waterlogging emergency alerts active in Vadodara low-lying transit corridors.
              </p>
              <Link
                to="/emergency"
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow transition-colors"
              >
                <span>Launch Emergency Console</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Corridor Road Health Overview Bar */}
      <div className="bg-slate-900/90 border border-slate-800/90 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              Monitored Corridors Pavement Roughness & Health Index
            </h2>
          </div>
          <Link
            to="/road-health"
            className="text-xs text-sky-400 hover:text-sky-300 flex items-center gap-1 font-semibold"
          >
            <span>Full Health Matrix</span>
            <ArrowRight className="w-3 h-3" />
          </Link>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {roadHealth?.segments.map((seg) => {
            const isCritical = seg.health_score < 40;
            const isPoor = seg.health_score < 60 && seg.health_score >= 40;
            const isFair = seg.health_score < 80 && seg.health_score >= 60;

            let badgeColor = 'text-emerald-400 border-emerald-800/80 bg-emerald-950/40';
            if (isCritical) badgeColor = 'text-rose-400 border-rose-800/80 bg-rose-950/40 font-bold';
            else if (isPoor) badgeColor = 'text-orange-400 border-orange-800/80 bg-orange-950/40 font-semibold';
            else if (isFair) badgeColor = 'text-amber-400 border-amber-800/80 bg-amber-950/40';

            return (
              <div
                key={seg.segment_code}
                className="p-3 rounded-lg bg-slate-950/80 border border-slate-800"
              >
                <div className="text-xs font-medium text-slate-300 truncate mb-1">
                  {seg.corridor_name}
                </div>
                <div className="flex items-baseline justify-between">
                  <span className="text-lg font-bold text-white font-mono">
                    {seg.health_score.toFixed(0)}%
                  </span>
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border uppercase ${badgeColor}`}>
                    {seg.rating}
                  </span>
                </div>
                <div className="mt-1.5 text-[11px] text-slate-400 flex justify-between font-mono">
                  <span>Defects: {seg.confirmed_defects_count}</span>
                  <span>IRI: {seg.roughness_index.toFixed(1)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Demo Controls Section */}
      <DemoControl
        activeScenario={simStatus?.active_scenario}
        onActionComplete={fetchDashboardData}
      />

      {/* Live Activity Feed */}
      <div className="bg-slate-900/90 border border-slate-800/90 rounded-xl p-4 shadow-xl">
        <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-200 font-mono">
              Live Fleet Sensor Telemetry Feed
            </h2>
          </div>
          <span className="text-[11px] text-slate-400 font-mono">
            WebSocket Channel: /ws/live
          </span>
        </div>

        <div className="space-y-2">
          {activityFeed.length === 0 ? (
            <div className="text-xs text-slate-400 py-4 text-center font-mono">
              Listening for real-time telemetry packets, sensor shocks, and verification audits...
            </div>
          ) : (
            activityFeed.map((item) => {
              let tagColor = 'bg-slate-800 text-slate-300 border-slate-700';
              let tagLabel = 'TELEMETRY';
              if (item.type === 'critical') {
                tagColor = 'bg-rose-950 text-rose-300 border-rose-700 font-bold';
                tagLabel = 'DISASTER';
              } else if (item.type === 'confirmed') {
                tagColor = 'bg-emerald-950 text-emerald-300 border-emerald-700 font-semibold';
                tagLabel = 'CORROBORATED';
              } else if (item.type === 'incident') {
                tagColor = 'bg-amber-950 text-amber-300 border-amber-700 font-semibold';
                tagLabel = 'DETECTION';
              } else if (item.type === 'verify') {
                tagColor = 'bg-sky-950 text-sky-300 border-sky-700 font-semibold';
                tagLabel = 'VERIFIED';
              } else if (item.type === 'work_order') {
                tagColor = 'bg-indigo-950 text-indigo-300 border-indigo-700';
                tagLabel = 'ORDER';
              }

              return (
                <div
                  key={item.id}
                  className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-950/80 border border-slate-800/80 text-xs font-mono"
                >
                  <div className="flex items-center gap-2.5 min-w-0 pr-2">
                    <span className={`text-[9px] px-1.5 py-0.5 rounded border uppercase tracking-wider shrink-0 ${tagColor}`}>
                      {tagLabel}
                    </span>
                    <span className="text-slate-200 truncate">{item.text}</span>
                  </div>
                  <span className="text-slate-500 text-[11px] shrink-0 font-mono">{item.time}</span>
                </div>
              );
            })
          )}
        </div>
      </div>

    </div>
  );
};
