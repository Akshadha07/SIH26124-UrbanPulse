import React, { useState } from 'react';
import { Play, RotateCcw, FastForward, CheckCircle2, AlertTriangle, Layers, Loader2 } from 'lucide-react';
import { triggerScenario, resetSimulation, advanceSimulationTick } from '../../api/simulation';

interface DemoControlProps {
  activeScenario?: string | null;
  onActionComplete?: () => void;
}

export const DemoControl: React.FC<DemoControlProps> = ({ activeScenario, onActionComplete }) => {
  const [loading, setLoading] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const handleScenario = async (name: string) => {
    try {
      setLoading(name);
      setMessage(null);
      await triggerScenario(name);
      setMessage('Activated: ' + name);
      if (onActionComplete) onActionComplete();
    } catch (err: any) {
      setMessage('Error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(null);
    }
  };

  const handleReset = async () => {
    try {
      setLoading('reset');
      setMessage(null);
      await resetSimulation();
      setMessage('Simulation reset successfully');
      if (onActionComplete) onActionComplete();
    } catch (err: any) {
      setMessage('Error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(null);
    }
  };

  const handleTick = async () => {
    try {
      setLoading('tick');
      setMessage(null);
      await advanceSimulationTick();
      setMessage('Advanced 1 tick');
      if (onActionComplete) onActionComplete();
    } catch (err: any) {
      setMessage('Error: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(null);
    }
  };

  const getButtonClass = (scenario: string) => {
    const base = 'flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium border transition-colors ';
    if (activeScenario === scenario) {
      if (scenario === 'pothole_cluster') return base + 'bg-amber-600/20 text-amber-200 border-amber-600';
      if (scenario === 'monsoon_flood') return base + 'bg-rose-600/20 text-rose-200 border-rose-600';
      if (scenario === 'high_crowd_rush') return base + 'bg-blue-600/20 text-blue-200 border-blue-600';
      if (scenario === 'sensor_failure') return base + 'bg-purple-600/20 text-purple-200 border-purple-600';
    }
    return base + 'bg-slate-800/80 hover:bg-slate-800 text-slate-200 border-slate-700';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800/80 pb-2">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
            SIH Demonstration Engine
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/30">
          SIMULATED ENVIRONMENT
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
        <button
          onClick={() => handleScenario('pothole_cluster')}
          disabled={loading !== null}
          className={getButtonClass('pothole_cluster')}
        >
          {loading === 'pothole_cluster' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
          )}
          <span>Pothole Cluster</span>
        </button>

        <button
          onClick={() => handleScenario('monsoon_flood')}
          disabled={loading !== null}
          className={getButtonClass('monsoon_flood')}
        >
          {loading === 'monsoon_flood' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          )}
          <span>Monsoon Flood</span>
        </button>

        <button
          onClick={() => handleScenario('high_crowd_rush')}
          disabled={loading !== null}
          className={getButtonClass('high_crowd_rush')}
        >
          {loading === 'high_crowd_rush' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 text-blue-400" />
          )}
          <span>Crowd Rush</span>
        </button>

        <button
          onClick={() => handleScenario('sensor_failure')}
          disabled={loading !== null}
          className={getButtonClass('sensor_failure')}
        >
          {loading === 'sensor_failure' ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 text-purple-400" />
          )}
          <span>Sensor Failure</span>
        </button>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60">
        <div className="flex items-center gap-2">
          <button
            onClick={handleTick}
            disabled={loading !== null}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
          >
            {loading === 'tick' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <FastForward className="w-3.5 h-3.5 text-cyan-400" />
            )}
            <span>Advance Tick</span>
          </button>

          <button
            onClick={handleReset}
            disabled={loading !== null}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-rose-950/40 hover:bg-rose-900/60 text-rose-300 border border-rose-800/50 transition-colors"
          >
            {loading === 'reset' ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <RotateCcw className="w-3.5 h-3.5" />
            )}
            <span>Reset Run Isolation</span>
          </button>
        </div>

        {message && (
          <div className="flex items-center gap-1.5 text-xs text-slate-300">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>{message}</span>
          </div>
        )}
      </div>
    </div>
  );
};
