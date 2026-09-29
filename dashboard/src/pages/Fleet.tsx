import React, { useState, useEffect } from 'react';
import { Bus, Search, Filter, Radio, Gauge, Users, Compass, Clock, MapPin } from 'lucide-react';
import { CommandMap } from '../components/maps/CommandMap';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getLiveFleet, getFleetRoutes } from '../api/fleet';
import { BusLiveResponse, RouteResponse } from '../types';

interface FleetPageProps {
  subscribeWs: (eventType: string, handler: (envelope: any) => void) => () => void;
}

export const Fleet: React.FC<FleetPageProps> = ({ subscribeWs }) => {
  const [buses, setBuses] = useState<BusLiveResponse[]>([]);
  const [routes, setRoutes] = useState<RouteResponse[]>([]);
  const [selectedBus, setSelectedBus] = useState<BusLiveResponse | null>(null);
  const [search, setSearch] = useState<string>('');
  const [routeFilter, setRouteFilter] = useState<string>('all');
  const [occupancyFilter, setOccupancyFilter] = useState<string>('all');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFleet = async () => {
    try {
      setError(null);
      const [fleetData, routesData] = await Promise.all([
        getLiveFleet(),
        getFleetRoutes(),
      ]);
      setBuses(fleetData);
      setRoutes(routesData);
      if (fleetData.length > 0 && !selectedBus) {
        setSelectedBus(fleetData[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch live fleet telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFleet();

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

        // Also update selected bus if applicable
        setSelectedBus((prev) => {
          if (!prev) return prev;
          const match = envelope.data.active_buses.find((x: any) => x.bus_id === prev.bus_id);
          if (match) {
            return { ...prev, ...match, last_updated: envelope.timestamp };
          }
          return prev;
        });
      }
    });

    return () => {
      unsubBus();
    };
  }, [subscribeWs]);

  const filteredBuses = buses.filter((bus) => {
    const matchesSearch =
      bus.bus_id.toLowerCase().includes(search.toLowerCase()) ||
      bus.route_name.toLowerCase().includes(search.toLowerCase());
    const matchesRoute = routeFilter === 'all' || bus.route_id === routeFilter;
    const matchesOccupancy =
      occupancyFilter === 'all' || bus.occupancy_level.toLowerCase() === occupancyFilter.toLowerCase();
    return matchesSearch && matchesRoute && matchesOccupancy;
  });

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={3} />
        <LoadingSkeleton rows={10} />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchFleet} />;
  }

  return (
    <div className="space-y-6">
      {/* Header & Metric stats */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bus className="w-5 h-5 text-blue-400" />
            <span>Vadodara Transit Fleet Telemetry</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Distributed Mobile Sensing Network • 12 Active Buses with BEL Sensor Kits
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono">
            Active: <span className="text-emerald-400 font-bold">{buses.length} Vehicles</span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono">
            Corridors: <span className="text-blue-400 font-bold">{routes.length} Routes</span>
          </div>
        </div>
      </div>

      {/* Map & Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-xs font-bold uppercase tracking-widest text-slate-200 flex items-center gap-2 font-mono">
              <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
              <span>Real-Time Fleet Trajectory Map</span>
            </h2>
            <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>12 Simulated Buses Transmitting</span>
            </div>
          </div>

          <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-[#060a12]">
            <CommandMap
              buses={buses}
              routes={routes}
              selectedIncidentId={null}
              onSelectBus={(b) => setSelectedBus(b)}
              height="520px"
            />
          </div>
        </div>

        {/* Selected Bus Telemetry Inspector */}
        <div className="bg-slate-900/90 border border-slate-800/90 rounded-xl p-5 shadow-xl flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
                <h3 className="text-xs font-bold uppercase tracking-widest text-slate-200 font-mono">
                  Vehicle Telemetry Node
                </h3>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold">
                NODE ONLINE
              </span>
            </div>

            {selectedBus ? (
              <div className="mt-4 space-y-3.5">
                <div>
                  <div className="text-xl font-extrabold text-white font-mono tracking-tight flex items-center justify-between">
                    <span>{selectedBus.bus_id}</span>
                    <span className="text-[10px] text-sky-400 font-normal border border-sky-800 bg-sky-950/60 px-2 py-0.5 rounded">
                      {selectedBus.route_id}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1 font-sans">
                    {selectedBus.route_name}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2.5 pt-2 border-t border-slate-800/80">
                  <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1 font-mono">
                      <Gauge className="w-3.5 h-3.5 text-sky-400" />
                      <span>Speed</span>
                    </div>
                    <div className="text-base font-extrabold font-mono text-white">
                      {selectedBus.speed.toFixed(1)} <span className="text-xs font-normal text-slate-400">km/h</span>
                    </div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1 font-mono">
                      <Compass className="w-3.5 h-3.5 text-amber-400" />
                      <span>Bearing</span>
                    </div>
                    <div className="text-base font-extrabold font-mono text-white">
                      {selectedBus.heading.toFixed(0)}°
                    </div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1 font-mono">
                      <Users className="w-3.5 h-3.5 text-purple-400" />
                      <span>Load</span>
                    </div>
                    <div className="text-base font-extrabold font-mono text-white">
                      {selectedBus.crowd_count} <span className="text-xs font-normal text-slate-400">/ {selectedBus.capacity}</span>
                    </div>
                  </div>

                  <div className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1 font-mono">
                      <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Status</span>
                    </div>
                    <div className="text-xs font-bold uppercase tracking-wider text-emerald-400 mt-1 font-mono">
                      {selectedBus.occupancy_level}
                    </div>
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2 text-xs font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>GPS Coordinates:</span>
                    <span className="text-sky-400 font-bold">
                      {selectedBus.lat.toFixed(5)}, {selectedBus.lon.toFixed(5)}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Operational State:</span>
                    <span className="text-emerald-400 font-bold uppercase">
                      {selectedBus.status}
                    </span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Telemetry Kit:</span>
                    <span className="text-slate-300">Camera + IMU + AQI</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-8 text-center text-xs text-slate-400 font-sans">
                Select a vehicle from the fleet table or map to inspect real-time sensor streams.
              </div>
            )}
          </div>

          {selectedBus && (
            <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-slate-500" />
                <span>Last Telemetry Packet:</span>
              </span>
              <span className="text-slate-200">{new Date(selectedBus.last_updated).toLocaleTimeString()}</span>
            </div>
          )}
        </div>
      </div>

      {/* Filter and Search Bar */}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 mb-4">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Bus ID or Corridor..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="w-4 h-4 text-slate-500" />
            <select
              value={routeFilter}
              onChange={(e) => setRouteFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Corridors</option>
              {routes.map((r) => (
                <option key={r.route_id} value={r.route_id}>
                  {r.route_name}
                </option>
              ))}
            </select>

            <select
              value={occupancyFilter}
              onChange={(e) => setOccupancyFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
            >
              <option value="all">All Occupancy Levels</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="full">Full</option>
            </select>
          </div>
        </div>

        {/* Fleet Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase font-mono tracking-wider border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Vehicle ID</th>
                <th className="py-2.5 px-3">Transit Corridor</th>
                <th className="py-2.5 px-3">Current Coordinates</th>
                <th className="py-2.5 px-3">Velocity</th>
                <th className="py-2.5 px-3">Occupancy</th>
                <th className="py-2.5 px-3">Status</th>
                <th className="py-2.5 px-3">Edge Hardware</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {filteredBuses.map((bus) => {
                const isSelected = selectedBus?.bus_id === bus.bus_id;
                return (
                  <tr
                    key={bus.bus_id}
                    onClick={() => setSelectedBus(bus)}
                    className={`cursor-pointer transition-colors ${
                      isSelected ? 'bg-blue-950/40 text-blue-200' : 'hover:bg-slate-850 text-slate-300'
                    }`}
                  >
                    <td className="py-2.5 px-3 font-bold text-white flex items-center gap-1.5">
                      <Bus className="w-3.5 h-3.5 text-blue-400" />
                      <span>{bus.bus_id}</span>
                    </td>
                    <td className="py-2.5 px-3 font-sans">{bus.route_name}</td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {bus.lat.toFixed(4)}, {bus.lon.toFixed(4)}
                    </td>
                    <td className="py-2.5 px-3">{bus.speed.toFixed(1)} km/h</td>
                    <td className="py-2.5 px-3">
                      <span className="capitalize">{bus.occupancy_level}</span> ({bus.crowd_count}/{bus.capacity})
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 uppercase">
                        {bus.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">
                        BEL KIT #{(bus.bus_id.match(/\d+/) || ['0'])[0]}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
