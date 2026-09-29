import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  ArrowUpDown, 
  ShieldCheck, 
  Eye, 
  RefreshCw,
  SlidersHorizontal 
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { PriorityBadge } from '../components/common/PriorityBadge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getIncidents, triggerFusionCycle } from '../api/incidents';
import { HazardResponse } from '../types';

interface IncidentsPageProps {
  subscribeWs: (eventType: string, handler: (envelope: any) => void) => () => void;
}

export const Incidents: React.FC<IncidentsPageProps> = ({ subscribeWs }) => {
  const [incidents, setIncidents] = useState<HazardResponse[]>([]);
  const [search, setSearch] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<'priority_score' | 'severity' | 'confirmation_count'>('priority_score');
  const [sortAsc, setSortAsc] = useState<boolean>(false);
  const [isFusing, setIsFusing] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchIncidents = async () => {
    try {
      setError(null);
      const data = await getIncidents();
      setIncidents(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch incident inventory');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncidents();

    const unsubDetected = subscribeWs('incident_detected', () => {
      fetchIncidents();
    });
    const unsubConfirmed = subscribeWs('incident_confirmed', () => {
      fetchIncidents();
    });

    return () => {
      unsubDetected();
      unsubConfirmed();
    };
  }, [subscribeWs]);

  const handleManualFusion = async () => {
    try {
      setIsFusing(true);
      await triggerFusionCycle();
      await fetchIncidents();
    } catch (err: any) {
      console.error('Fusion trigger failed:', err);
    } finally {
      setIsFusing(false);
    }
  };

  const filteredIncidents = incidents
    .filter((inc) => {
      const matchesSearch =
        inc.hazard_type.toLowerCase().includes(search.toLowerCase()) ||
        (inc.address_hint && inc.address_hint.toLowerCase().includes(search.toLowerCase())) ||
        String(inc.id).includes(search);
      const matchesType = typeFilter === 'all' || inc.hazard_type.toLowerCase().includes(typeFilter.toLowerCase());
      const matchesStatus = statusFilter === 'all' || inc.status.toLowerCase() === statusFilter.toLowerCase();
      const matchesSeverity =
        severityFilter === 'all' ||
        (severityFilter === 'high' && inc.severity >= 3.5) ||
        (severityFilter === 'low' && inc.severity < 3.5);

      return matchesSearch && matchesType && matchesStatus && matchesSeverity;
    })
    .sort((a, b) => {
      const factor = sortAsc ? 1 : -1;
      return (a[sortField] - b[sortField]) * factor;
    });

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={2} />
        <LoadingSkeleton rows={10} />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchIncidents} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>AI Road Hazard & Incident Intelligence</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Spatio-Temporally Clustered Incidents • Multi-Sensor & Corroborated Road Defects
          </p>
        </div>

        <button
          onClick={handleManualFusion}
          disabled={isFusing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isFusing ? 'animate-spin' : ''}`} />
          <span>{isFusing ? 'Running AI Fusion...' : 'Run AI Fusion Cycle'}</span>
        </button>
      </div>

      {/* Filter / Search Bar */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
          <div className="relative lg:col-span-2">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search by ID, Defect Type, or Location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Defect Classes</option>
              <option value="pothole">Pothole</option>
              <option value="waterlogging">Waterlogging</option>
              <option value="road_crack">Road Crack</option>
              <option value="garbage">Garbage Dump</option>
            </select>
          </div>

          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="reported">Reported (Single Pass)</option>
              <option value="confirmed">Confirmed (Corroborated)</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="verified_closed">Verified Closed</option>
              <option value="escalated_disaster">Escalated Disaster</option>
            </select>
          </div>

          <div>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Severities</option>
              <option value="high">High Severity (&ge; 3.5)</option>
              <option value="low">Low Severity (&lt; 3.5)</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase font-mono tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Incident ID</th>
                <th className="py-2.5 px-3">Hazard Type</th>
                <th className="py-2.5 px-3">Location / Corridor</th>
                <th 
                  className="py-2.5 px-3 cursor-pointer hover:text-white"
                  onClick={() => {
                    if (sortField === 'priority_score') setSortAsc(!sortAsc);
                    else { setSortField('priority_score'); setSortAsc(false); }
                  }}
                >
                  <div className="flex items-center gap-1">
                    <span>Priority Score</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th 
                  className="py-2.5 px-3 cursor-pointer hover:text-white"
                  onClick={() => {
                    if (sortField === 'severity') setSortAsc(!sortAsc);
                    else { setSortField('severity'); setSortAsc(false); }
                  }}
                >
                  <div className="flex items-center gap-1">
                    <span>Severity</span>
                    <ArrowUpDown className="w-3 h-3" />
                  </div>
                </th>
                <th className="py-2.5 px-3">AI Confidence</th>
                <th className="py-2.5 px-3">Corroboration</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3 text-right">Audit Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredIncidents.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-8 text-center text-slate-500 font-sans">
                    No hazards match the active filter criteria.
                  </td>
                </tr>
              ) : (
                filteredIncidents.map((inc) => {
                  const isMultiSensor = Array.isArray(inc.sources) && inc.sources.length > 1;
                  const isCorroborated = inc.distinct_bus_count > 1;

                  return (
                    <tr key={inc.id} className="hover:bg-slate-850/80 transition-colors">
                      <td className="py-2.5 px-3 font-bold text-white">
                        #{inc.id}
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="font-semibold text-slate-200 capitalize font-sans">
                          {inc.hazard_type.replace(/_/g, ' ')}
                        </div>
                        {isMultiSensor && (
                          <div className="text-[10px] text-cyan-400 font-mono flex items-center gap-1 mt-0.5">
                            <ShieldCheck className="w-3 h-3" />
                            <span>MULTI-SENSOR</span>
                          </div>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400 font-sans">
                        {inc.address_hint || `(${inc.lat.toFixed(4)}, ${inc.lon.toFixed(4)})`}
                      </td>
                      <td className="py-2.5 px-3">
                        <PriorityBadge score={inc.priority_score} size="sm" />
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">
                        {inc.severity.toFixed(1)} / 5.0
                      </td>
                      <td className="py-2.5 px-3 text-slate-300">
                        {(inc.confidence * 100).toFixed(0)}%
                      </td>
                      <td className="py-2.5 px-3">
                        <div className="flex items-center gap-1">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] ${
                            isCorroborated 
                              ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold' 
                              : 'bg-slate-800 text-slate-400'
                          }`}>
                            {inc.distinct_bus_count} Buses
                          </span>
                        </div>
                      </td>
                      <td className="py-2.5 px-3">
                        <StatusBadge status={inc.status} size="sm" />
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <Link
                          to={`/incidents/${inc.id}`}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/40 text-xs transition-colors font-sans"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>Forensics</span>
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
