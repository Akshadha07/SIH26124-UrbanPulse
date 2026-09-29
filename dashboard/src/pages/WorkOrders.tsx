import React, { useState, useEffect } from 'react';
import { 
  ClipboardList, 
  Search, 
  Filter, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  User, 
  AlertCircle,
  FileCheck,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { LoadingSkeleton } from '../components/common/LoadingSkeleton';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { getWorkOrders, updateWorkOrderStatus, getWorkOrderAudits } from '../api/workOrders';
import { WorkOrderResponse, VerificationAuditResponse } from '../types';

interface WorkOrdersPageProps {
  subscribeWs: (eventType: string, handler: (envelope: any) => void) => () => void;
}

export const WorkOrders: React.FC<WorkOrdersPageProps> = ({ subscribeWs }) => {
  const [orders, setOrders] = useState<WorkOrderResponse[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<WorkOrderResponse | null>(null);
  const [audits, setAudits] = useState<VerificationAuditResponse[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [auditsLoading, setAuditsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);

  const fetchOrders = async () => {
    try {
      setError(null);
      const data = await getWorkOrders();
      setOrders(data);
      if (data.length > 0 && !selectedOrder) {
        setSelectedOrder(data[0]);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to fetch municipal work orders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();

    const unsubWo = subscribeWs('work_order_updated', () => {
      fetchOrders();
    });
    const unsubVerify = subscribeWs('verification_completed', () => {
      fetchOrders();
    });

    return () => {
      unsubWo();
      unsubVerify();
    };
  }, [subscribeWs]);

  // When selected order changes, load its verification audits
  useEffect(() => {
    if (!selectedOrder) {
      setAudits([]);
      return;
    }
    const loadAudits = async () => {
      try {
        setAuditsLoading(true);
        const auditList = await getWorkOrderAudits(selectedOrder.id);
        setAudits(auditList);
      } catch (err) {
        setAudits([]);
      } finally {
        setAuditsLoading(false);
      }
    };
    loadAudits();
  }, [selectedOrder]);

  const handleStatusTransition = async (orderId: number, nextStatus: string) => {
    try {
      setIsUpdating(true);
      setActionMessage(null);
      await updateWorkOrderStatus(orderId, { status: nextStatus, notes: `Status transitioned to ${nextStatus} via Command Center` });
      setActionMessage(`Work order #${orderId} moved to ${nextStatus}`);
      await fetchOrders();
      if (selectedOrder && selectedOrder.id === orderId) {
        const updatedAudits = await getWorkOrderAudits(orderId);
        setAudits(updatedAudits);
      }
    } catch (err: any) {
      setActionMessage(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsUpdating(false);
    }
  };

  const filteredOrders = orders.filter((o) => {
    const matchesSearch =
      o.title.toLowerCase().includes(search.toLowerCase()) ||
      o.assigned_to.toLowerCase().includes(search.toLowerCase()) ||
      String(o.id).includes(search);
    const matchesStatus = statusFilter === 'all' || o.status.toUpperCase() === statusFilter.toUpperCase();
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingSkeleton rows={2} />
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchOrders} />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <ClipboardList className="w-5 h-5 text-blue-400" />
            <span>Municipal Repair Work Orders & Verification Audits</span>
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Repair Crew Dispatch • Status Transitions • Autonomous Transit Bus Pass-by Auditing
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-slate-300">
          <span className="p-2 rounded bg-slate-900 border border-slate-800">
            Total Orders: <strong className="text-white">{orders.length}</strong>
          </span>
        </div>
      </div>

      {actionMessage && (
        <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* Main Grid: Orders List (Left) + Detail & Audit Viewer (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          {/* Filter Bar */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search Work Orders..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <Filter className="w-4 h-4 text-slate-500" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
              >
                <option value="all">All Statuses</option>
                <option value="ASSIGNED">Assigned</option>
                <option value="IN_REPAIR">In Repair</option>
                <option value="RESOLVED">Resolved</option>
                <option value="VERIFIED">Verified</option>
              </select>
            </div>
          </div>

          {/* Orders Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/80 text-slate-400 uppercase font-mono tracking-wider border-b border-slate-800">
                <tr>
                  <th className="py-2.5 px-3">WO ID</th>
                  <th className="py-2.5 px-3">Title & Location</th>
                  <th className="py-2.5 px-3">Assignee</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filteredOrders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500 font-sans">
                      No work orders found matching criteria.
                    </td>
                  </tr>
                ) : (
                  filteredOrders.map((wo) => {
                    const isSelected = selectedOrder?.id === wo.id;
                    return (
                      <tr
                        key={wo.id}
                        onClick={() => setSelectedOrder(wo)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? 'bg-sky-950/50 text-sky-200 border-l-2 border-sky-400 font-semibold' : 'hover:bg-slate-800/60 text-slate-300'
                        }`}
                      >
                        <td className="py-2.5 px-3 font-bold text-white font-mono">
                          #{wo.id}
                        </td>
                        <td className="py-2.5 px-3 font-sans">
                          <div className="font-semibold text-slate-200">{wo.title}</div>
                          <div className="text-[11px] text-slate-400 font-mono mt-0.5">{wo.location_hint}</div>
                        </td>
                        <td className="py-2.5 px-3 font-sans">
                          <div className="text-slate-300 font-medium">{wo.assigned_to}</div>
                          <div className="text-[10px] text-slate-400 font-mono">{wo.department}</div>
                        </td>
                        <td className="py-2.5 px-3">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            wo.priority === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border border-rose-700 animate-pulse' : 'bg-slate-800 text-slate-300 border border-slate-700'
                          }`}>
                            {wo.priority}
                          </span>
                        </td>
                        <td className="py-2.5 px-3">
                          <StatusBadge status={wo.status} size="sm" />
                        </td>
                        <td className="py-2.5 px-3 text-right font-sans">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedOrder(wo);
                            }}
                            className="p-1 rounded hover:bg-slate-800 text-sky-400"
                          >
                            <ChevronRight className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Order & Verification Audit Inspector */}
        <div className="bg-slate-900/90 border border-slate-800/90 rounded-xl p-5 shadow-xl flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <FileCheck className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold uppercase tracking-widest text-slate-200 font-mono">
                  Work Order Forensics & Audit
                </h3>
              </div>
              {selectedOrder && (
                <StatusBadge status={selectedOrder.status} size="sm" />
              )}
            </div>

            {selectedOrder ? (
              <div className="mt-4 space-y-4">
                <div>
                  <div className="text-sm font-bold text-white font-sans">
                    {selectedOrder.title}
                  </div>
                  <div className="text-xs text-slate-400 mt-1 font-mono">
                    Incident Ref: #{selectedOrder.incident_id} • Created: {new Date(selectedOrder.created_at).toLocaleString()}
                  </div>
                </div>

                <div className="p-3.5 rounded-lg bg-slate-950/80 border border-slate-800 space-y-2 text-xs font-mono">
                  <div className="flex justify-between text-slate-400">
                    <span>Department:</span>
                    <span className="text-slate-200 font-semibold">{selectedOrder.department}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Assigned Crew:</span>
                    <span className="text-slate-200 font-semibold">{selectedOrder.assigned_to}</span>
                  </div>
                  <div className="flex justify-between text-slate-400">
                    <span>Coordinates:</span>
                    <span className="text-sky-400 font-bold">
                      {selectedOrder.lat.toFixed(4)}, {selectedOrder.lon.toFixed(4)}
                    </span>
                  </div>
                </div>

                {/* State Transition Actions */}
                <div className="pt-2">
                  <div className="text-[10px] font-mono uppercase tracking-widest text-slate-400 mb-2 font-bold">
                    Action Dispatch Transition
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => handleStatusTransition(selectedOrder.id, 'IN_REPAIR')}
                      disabled={isUpdating || selectedOrder.status === 'IN_REPAIR'}
                      className="px-2.5 py-1 text-xs font-medium rounded bg-amber-950/70 hover:bg-amber-900 text-amber-300 border border-amber-800/80 transition-colors disabled:opacity-50"
                    >
                      Start Repair
                    </button>
                    <button
                      onClick={() => handleStatusTransition(selectedOrder.id, 'RESOLVED')}
                      disabled={isUpdating || selectedOrder.status === 'RESOLVED'}
                      className="px-2.5 py-1 text-xs font-medium rounded bg-emerald-950/70 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/80 transition-colors disabled:opacity-50"
                    >
                      Mark Repaired
                    </button>
                    <button
                      onClick={() => handleStatusTransition(selectedOrder.id, 'VERIFIED')}
                      disabled={isUpdating || selectedOrder.status === 'VERIFIED'}
                      className="px-2.5 py-1 text-xs font-medium rounded bg-sky-950/70 hover:bg-sky-900 text-sky-300 border border-sky-800/80 transition-colors disabled:opacity-50"
                    >
                      Run Pass-By Audit
                    </button>
                  </div>
                </div>

                {/* Autonomous Pass-By Audit Result */}
                <div className="pt-3 border-t border-slate-800">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-[11px] font-mono uppercase tracking-wider text-slate-300 flex items-center gap-1.5 font-bold">
                      <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                      <span>Transit Pass-By Verification Audit</span>
                    </div>
                    {audits.length > 0 && (
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-bold">
                        {audits.length} AUDIT PASS
                      </span>
                    )}
                  </div>

                  {auditsLoading ? (
                    <div className="text-xs text-slate-500 font-mono py-2">Loading audit record...</div>
                  ) : audits.length > 0 ? (
                    <div className="space-y-2">
                      {audits.map((a) => (
                        <div key={a.id} className="p-3.5 rounded-lg bg-slate-950 border border-emerald-900/60 text-xs font-mono space-y-1.5">
                          <div className="flex justify-between items-center">
                            <span className="font-bold text-emerald-400">Verdict: {a.verdict}</span>
                            <span className="text-[10px] text-slate-400">{new Date(a.verification_timestamp).toLocaleTimeString()}</span>
                          </div>
                          <div className="text-slate-300 text-[11px]">
                            Auditing Bus: <strong className="text-sky-400">{a.bus_id}</strong>
                          </div>
                          <div className="text-slate-300 text-[11px]">
                            Residual Vibration: <strong className="text-emerald-300 font-bold">{a.vibration_peak_g.toFixed(2)} g</strong> (Normal Road Threshold)
                          </div>
                          {a.notes && (
                            <div className="text-[10px] text-slate-400 italic pt-1 border-t border-slate-800/80">
                              "{a.notes}"
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-3.5 rounded-lg bg-slate-950/60 border border-slate-800 text-[11px] text-slate-400 font-sans">
                      No automated verification pass recorded yet. When a public transit bus traverses this GPS coordinate after repair, its vibration sensors will verify pavement smoothness.
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-400 font-sans">
                Select an order to inspect repair dispatch details and automated sensor audits.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

