import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { Fleet } from './pages/Fleet';
import { Incidents } from './pages/Incidents';
import { IncidentDetails } from './pages/IncidentDetails';
import { Emergency } from './pages/Emergency';
import { RoadHealth } from './pages/RoadHealth';
import { WorkOrders } from './pages/WorkOrders';
import { useWebSocket } from './hooks/useWebSocket';
import { getIncidents, getWaterloggingAlerts } from './api/incidents';

export const App: React.FC = () => {
  const { isConnected, subscribe } = useWebSocket();
  const [activeIncidentsCount, setActiveIncidentsCount] = useState<number>(0);
  const [criticalAlertsCount, setCriticalAlertsCount] = useState<number>(0);

  const fetchCounts = async () => {
    try {
      const [incidents, alerts] = await Promise.all([
        getIncidents(),
        getWaterloggingAlerts(),
      ]);
      const active = incidents.filter(
        (i) => i.status !== 'resolved' && i.status !== 'verified_closed'
      );
      setActiveIncidentsCount(active.length);
      setCriticalAlertsCount(alerts.length);
    } catch {
      // ignore transient polling errors
    }
  };

  useEffect(() => {
    fetchCounts();

    const unsubAlert = subscribe('waterlogging_alert', () => {
      fetchCounts();
    });
    const unsubIncident = subscribe('incident_detected', () => {
      fetchCounts();
    });
    const unsubConfirmed = subscribe('incident_confirmed', () => {
      fetchCounts();
    });

    return () => {
      unsubAlert();
      unsubIncident();
      unsubConfirmed();
    };
  }, [subscribe]);

  return (
    <Router>
      <Layout
        wsConnected={isConnected}
        activeIncidentsCount={activeIncidentsCount}
        criticalAlertsCount={criticalAlertsCount}
      >
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard subscribeWs={subscribe} />} />
          <Route path="/fleet" element={<Fleet subscribeWs={subscribe} />} />
          <Route path="/incidents" element={<Incidents subscribeWs={subscribe} />} />
          <Route path="/incidents/:id" element={<IncidentDetails />} />
          <Route path="/emergency" element={<Emergency subscribeWs={subscribe} />} />
          <Route path="/road-health" element={<RoadHealth />} />
          <Route path="/work-orders" element={<WorkOrders subscribeWs={subscribe} />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
