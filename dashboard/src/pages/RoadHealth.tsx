import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  RefreshCw, 
  TrendingUp, 
  MapPin, 
  Gauge, 
  AlertTriangle,
  Layers,
  BarChart3
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Cell
} from 'recharts';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getRoadHealthOverview, calculateRoadHealth } from '../api/roadHealth';
import { RoadHealthOverviewResponse } from '../types';

export const RoadHealth: React.FC = () => {
  const [data, setData] = useState<RoadHealthOverviewResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [recalculating, setRecalculating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setError(null);
      const res = await getRoadHealthOverview();
      setData(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load road health telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRecalculate = async () => {
    try {
      setRecalculating(true);
      const updated = await calculateRoadHealth();
      setData(updated);
    } catch (err: any) {
      console.error('Failed to recalculate:', err);
    } finally {
      setRecalculating(false);
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

  if (error || !data) {
    return <ErrorMessage message={error || 'No road health telemetry available'} onRetry={fetchData} />;
  }

  // Chart data preparation
  const chartData = data.segments.map((s) => ({
    name: s.corridor_name.replace(' Corridor', '').replace(' Radial', '').replace(' Line', '').replace(' Arterial', ''),
    score: Math.round(s.health_score),
    roughness: Number(s.roughness_index.toFixed(2)),
    defects: s.confirmed_defects_count,
  }));

  const getBarColor = (score: number) => {
    if (score >= 80) return '#10b981'; // emerald
    if (score >= 60) return '#f59e0b'; // amber
    if (score >= 40) return '#f97316'; // orange
    return '#ef4444'; // rose
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <span>Vadodara Corridor Road Health Index</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Dynamic Pavement Roughness (IRI) & Structural Degradation Derived from Transit Bus Accelerometers
          </p>
        </div>

        <button
          onClick={handleRecalculate}
          disabled={recalculating}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${recalculating ? 'animate-spin' : ''}`} />
          <span>{recalculating ? 'Re-evaluating Corridors...' : 'Recalculate Indices'}</span>
        </button>
      </div>

      {/* Citywide Index Hero Banner */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-xl md:col-span-2">
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
            Overall City Pavement Health Index
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-extrabold font-mono text-white tracking-tight">
              {data.overall_city_index.toFixed(1)}%
            </span>
            <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded border uppercase ${
              data.overall_city_index >= 75
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800'
                : 'bg-amber-950/80 text-amber-300 border-amber-800'
            }`}>
              {data.overall_city_index >= 75 ? 'NOMINAL NETWORK STATUS' : 'MAINTENANCE REQUIRED'}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-2">
            Aggregated across {data.total_segments_monitored} major public transit corridors in Vadodara metropolitan area.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-xl">
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
            Active Defect Density
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-2">
            {(data.segments.reduce((acc, s) => acc + s.defect_density, 0) / data.segments.length).toFixed(2)}
            <span className="text-xs font-normal text-slate-400 ml-1.5 font-sans">defects / km</span>
          </div>
          <div className="text-[11px] text-slate-500 mt-2 font-mono">
            Derived from 35m spatial clusters
          </div>
        </div>

        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 shadow-xl">
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-1">
            Fleet Sensing Coverage
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-2">
            100%
          </div>
          <div className="text-[11px] text-slate-500 mt-2 font-mono">
            All 6 municipal zones monitored
          </div>
        </div>
      </div>

      {/* Comparison Chart */}
      <div className="p-5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-xl">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-sky-400" />
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-200 font-mono">
              Corridor Structural Health Comparison (Current Cycle)
            </h2>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Real-time sensor trace aggregation
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
              <CartesianGrid strokeDasharray="2 4" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 11, fill: '#94a3b8' }} interval={0} angle={-15} textAnchor="end" />
              <YAxis stroke="#64748b" domain={[0, 100]} tick={{ fontSize: 11, fill: '#94a3b8' }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#091222', borderColor: '#1e2e48', borderRadius: '10px', fontSize: '12px', boxShadow: '0 8px 24px rgba(0,0,0,0.8)' }}
                itemStyle={{ color: '#f1f5f9', fontWeight: 600 }}
                labelStyle={{ color: '#38bdf8', fontWeight: 700, marginBottom: '4px' }}
              />
              <Bar dataKey="score" name="Health Score (%)" radius={[6, 6, 0, 0]}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Monitored Corridors Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data.segments.map((seg) => {
          const isCritical = seg.health_score < 40;
          const isPoor = seg.health_score < 60 && seg.health_score >= 40;
          const isFair = seg.health_score < 80 && seg.health_score >= 60;

          let badgeColor = 'text-emerald-400 border-emerald-800 bg-emerald-950/40';
          if (isCritical) badgeColor = 'text-rose-400 border-rose-800 bg-rose-950/40 animate-pulse font-bold';
          else if (isPoor) badgeColor = 'text-orange-400 border-orange-800 bg-orange-950/40 font-semibold';
          else if (isFair) badgeColor = 'text-amber-400 border-amber-800 bg-amber-950/40';

          return (
            <div
              key={seg.segment_code}
              className="p-5 rounded-xl bg-slate-900/90 border border-slate-800/90 shadow-xl space-y-3 hover:border-slate-700 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-sky-400 font-bold uppercase tracking-wider bg-sky-950/60 px-2 py-0.5 rounded border border-sky-800/60">
                  {seg.segment_code}
                </span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${badgeColor}`}>
                  {seg.rating}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-bold text-white font-sans">
                  {seg.corridor_name}
                </h3>
                <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-1 font-mono">
                  <MapPin className="w-3 h-3 text-slate-500 shrink-0" />
                  <span className="truncate">
                    ({seg.start_lat.toFixed(3)}, {seg.start_lon.toFixed(3)}) &rarr; ({seg.end_lat.toFixed(3)}, {seg.end_lon.toFixed(3)})
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-2 pt-3 border-t border-slate-800 font-mono text-center">
                <div className="p-2 rounded bg-slate-950/80 border border-slate-800/80">
                  <div className="text-[10px] text-slate-400">Score</div>
                  <div className="text-base font-extrabold text-white mt-0.5">
                    {seg.health_score.toFixed(0)}%
                  </div>
                </div>

                <div className="p-2 rounded bg-slate-950/80 border border-slate-800/80">
                  <div className="text-[10px] text-slate-400">IRI Metric</div>
                  <div className="text-base font-extrabold text-slate-200 mt-0.5">
                    {seg.roughness_index.toFixed(1)}
                  </div>
                </div>

                <div className="p-2 rounded bg-slate-950/80 border border-slate-800/80">
                  <div className="text-[10px] text-slate-400">Defects</div>
                  <div className={`text-base font-extrabold mt-0.5 ${seg.confirmed_defects_count > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                    {seg.confirmed_defects_count}
                  </div>
                </div>
              </div>

              <div className="text-[10px] text-slate-500 font-mono text-right pt-1">
                Assessed: {new Date(seg.last_assessed_at).toLocaleTimeString()}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

