import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { BusLiveResponse, HazardResponse, RouteResponse, AQIPointResponse } from '../../types';

interface CommandMapProps {
  buses?: BusLiveResponse[];
  incidents?: HazardResponse[];
  routes?: RouteResponse[];
  aqiHotspots?: AQIPointResponse[];
  selectedIncidentId?: number | null;
  onSelectIncident?: (incident: HazardResponse) => void;
  onSelectBus?: (bus: BusLiveResponse) => void;
  height?: string;
  zoom?: number;
  center?: [number, number];
}

export const CommandMap: React.FC<CommandMapProps> = ({
  buses = [],
  incidents = [],
  routes = [],
  aqiHotspots = [],
  selectedIncidentId = null,
  onSelectIncident,
  onSelectBus,
  height = '500px',
  zoom = 13,
  center = [22.3072, 73.1812],
}) => {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const busLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const incidentLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const routeLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const aqiLayerGroupRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: center,
        zoom: zoom,
        zoomControl: false,
      });

      L.control.zoom({ position: 'bottomright' }).addTo(map);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      routeLayerGroupRef.current = L.layerGroup().addTo(map);
      incidentLayerGroupRef.current = L.layerGroup().addTo(map);
      busLayerGroupRef.current = L.layerGroup().addTo(map);
      aqiLayerGroupRef.current = L.layerGroup().addTo(map);

      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!routeLayerGroupRef.current) return;
    routeLayerGroupRef.current.clearLayers();

    routes.forEach((route) => {
      if (route.coordinates && route.coordinates.length > 0) {
        // Ambient glow polyline
        const glowPolyline = L.polyline(route.coordinates as L.LatLngExpression[], {
          color: route.color || '#0284c7',
          weight: 6,
          opacity: 0.25,
        });
        glowPolyline.addTo(routeLayerGroupRef.current!);

        // Core tactical route polyline
        const polyline = L.polyline(route.coordinates as L.LatLngExpression[], {
          color: route.color || '#38bdf8',
          weight: 2.5,
          opacity: 0.85,
          dashArray: '6, 10',
        });
        polyline.bindTooltip(`Corridor: ${route.route_name}`, { sticky: true });
        polyline.addTo(routeLayerGroupRef.current!);
      }
    });
  }, [routes]);

  useEffect(() => {
    if (!busLayerGroupRef.current) return;
    busLayerGroupRef.current.clearLayers();

    buses.forEach((bus) => {
      const heading = bus.heading || 0;
      const shortId = bus.bus_id.replace('BUS-VMC-', 'B-');

      // Tactical SVG Bus Marker with directional heading chevron
      const iconHtml = `
        <div style="position: relative; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
          <div style="
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            background: rgba(14, 165, 233, 0.15);
            border: 1px solid rgba(56, 189, 248, 0.3);
          "></div>
          <div style="
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #081120;
            border: 2px solid #0284c7;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8), 0 0 10px rgba(56, 189, 248, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
          ">
            <!-- Directional Vector Arrow -->
            <div style="
              position: absolute;
              top: -6px;
              left: 50%;
              transform: translateX(-50%) rotate(${heading}deg);
              transform-origin: center 21px;
              width: 0;
              height: 0;
              border-left: 4px solid transparent;
              border-right: 4px solid transparent;
              border-bottom: 7px solid #38bdf8;
              filter: drop-shadow(0 0 3px rgba(56, 189, 248, 0.8));
            "></div>
            <!-- Bus Glyph SVG -->
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="15" rx="2"></rect>
              <line x1="3" y1="9" x2="21" y2="9"></line>
              <circle cx="7.5" cy="15.5" r="1.5" fill="#38bdf8"></circle>
              <circle cx="16.5" cy="15.5" r="1.5" fill="#38bdf8"></circle>
            </svg>
          </div>
          <div style="
            position: absolute;
            bottom: -15px;
            background: rgba(8, 17, 32, 0.95);
            border: 1px solid #1e293b;
            color: #94a3b8;
            font-size: 9px;
            font-family: monospace;
            font-weight: 700;
            padding: 1px 4px;
            border-radius: 3px;
            white-space: nowrap;
            letter-spacing: -0.2px;
          ">
            ${shortId}
          </div>
        </div>
      `;

      const busIcon = L.divIcon({
        html: iconHtml,
        className: 'tactical-bus-marker',
        iconSize: [34, 34],
        iconAnchor: [17, 17],
      });

      const marker = L.marker([bus.lat, bus.lon], { icon: busIcon });
      const popupHtml = `
        <div style="font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12px; color: #f1f5f9; min-width: 190px;">
          <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 5px; margin-bottom: 6px;">
            <div style="font-weight: 700; color: #38bdf8; font-family: monospace;">${bus.bus_id}</div>
            <span style="font-size: 9px; padding: 2px 6px; border-radius: 4px; background: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); font-weight: 600;">
              TRANSIT SENSOR
            </span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px 10px; font-size: 11px; margin-bottom: 6px;">
            <div>Route: <strong style="color: #e2e8f0;">${bus.route_name || bus.route_id}</strong></div>
            <div>Speed: <strong style="color: #e2e8f0;">${bus.speed.toFixed(1)} km/h</strong></div>
            <div>Heading: <strong style="color: #e2e8f0;">${bus.heading.toFixed(0)}°</strong></div>
            <div>Occupancy: <strong style="color: #e2e8f0;">${bus.crowd_count} pax</strong></div>
          </div>
          <div style="font-size: 10px; color: #64748b; font-family: monospace; border-top: 1px solid #1e293b; padding-top: 5px;">
            Telemetry Sync: ${new Date(bus.last_updated).toLocaleTimeString()}
          </div>
        </div>
      `;
      marker.bindPopup(popupHtml);

      if (onSelectBus) {
        marker.on('click', () => onSelectBus(bus));
      }

      marker.addTo(busLayerGroupRef.current!);
    });
  }, [buses, onSelectBus]);

  useEffect(() => {
    if (!incidentLayerGroupRef.current) return;
    incidentLayerGroupRef.current.clearLayers();

    incidents.forEach((inc) => {
      const isWaterlogging = inc.hazard_type.toLowerCase().includes('waterlogging');
      const isCritical = inc.hazard_type === 'WATERLOGGING_CRITICAL' || inc.waterlogging_severity === 'CRITICAL' || inc.status === 'ESCALATED_DISASTER';
      const isPothole = inc.hazard_type.toLowerCase().includes('pothole');
      const isCorroborated = inc.distinct_bus_count > 1 || inc.confirmation_count > 1;

      let strokeColor = '#f59e0b';
      let bgColor = '#181204';
      let glowColor = 'rgba(245, 158, 11, 0.4)';
      let size = 30;

      // SVG Vector Glyphs for Hazards
      let glyphSvg = `
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="${strokeColor}" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <circle cx="12" cy="17" r="1" fill="${strokeColor}"></circle>
        </svg>
      `;

      if (isCritical) {
        strokeColor = '#ef4444';
        bgColor = '#22080a';
        glowColor = 'rgba(239, 68, 68, 0.6)';
        size = 36;
        glyphSvg = `
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <circle cx="12" cy="17" r="1" fill="#ef4444"></circle>
          </svg>
        `;
      } else if (isWaterlogging) {
        strokeColor = '#06b6d4';
        bgColor = '#04171d';
        glowColor = 'rgba(6, 182, 212, 0.4)';
        size = 32;
        glyphSvg = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
          </svg>
        `;
      } else if (isPothole) {
        strokeColor = '#f97316';
        bgColor = '#1f0d04';
        glowColor = 'rgba(249, 115, 22, 0.4)';
        size = 30;
        glyphSvg = `
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M9 12h6"></path>
            <path d="M12 9v6"></path>
          </svg>
        `;
      }

      const isSelected = selectedIncidentId === inc.id;

      // Corroboration Pip (Green dot indicator if verified by multiple buses)
      const corroborationPip = isCorroborated ? `
        <div style="
          position: absolute;
          top: -2px;
          right: -2px;
          width: 9px;
          height: 9px;
          border-radius: 50%;
          background: #10b981;
          border: 1.5px solid #060a12;
          box-shadow: 0 0 4px #10b981;
        " title="${inc.distinct_bus_count} Buses Corroborated"></div>
      ` : '';

      const iconHtml = `
        <div style="position: relative; width: ${size}px; height: ${size}px; display: flex; align-items: center; justify-content: center;">
          <div style="
            width: ${size}px;
            height: ${size}px;
            border-radius: ${isCritical ? '8px' : '50%'};
            background: ${bgColor};
            border: 2px solid ${strokeColor};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.8), 0 0 ${isSelected ? '16px' : '8px'} ${glowColor};
            display: flex;
            align-items: center;
            justify-content: center;
            transform: scale(${isSelected ? 1.25 : 1.0});
            transition: transform 0.2s cubic-bezier(0.2, 0, 0, 1);
          " class="${isCritical ? 'animate-alert-pulse' : ''}">
            ${glyphSvg}
          </div>
          ${corroborationPip}
        </div>
      `;

      const incIcon = L.divIcon({
        html: iconHtml,
        className: 'tactical-hazard-marker',
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2],
      });

      const marker = L.marker([inc.lat, inc.lon], { icon: incIcon });
      const addressPart = inc.address_hint ? `<div style="color: #94a3b8; font-size: 11px; margin-top: 4px; line-height: 1.3;">${inc.address_hint}</div>` : '';
      const popupHtml = `
        <div style="font-family: ui-sans-serif, system-ui, sans-serif; font-size: 12px; color: #f1f5f9; min-width: 210px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; border-bottom: 1px solid #1e293b; padding-bottom: 5px;">
            <span style="font-weight: 700; color: ${strokeColor}; text-transform: uppercase; font-size: 11px;">
              ${inc.hazard_type.replace(/_/g, ' ')}
            </span>
            <span style="font-size: 10px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.08); font-family: monospace; font-weight: 700; color: #e2e8f0;">
              Score: ${inc.priority_score.toFixed(1)}
            </span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px 8px; font-size: 11px; margin-bottom: 6px;">
            <div>Status: <strong style="color: #e2e8f0;">${inc.status}</strong></div>
            <div>Severity: <strong style="color: #e2e8f0;">${inc.severity.toFixed(1)}/5.0</strong></div>
            <div>Confidence: <strong style="color: #e2e8f0;">${(inc.confidence * 100).toFixed(0)}%</strong></div>
            <div>Corroborated: <strong style="color: ${isCorroborated ? '#10b981' : '#94a3b8'};">${inc.distinct_bus_count} Buses</strong></div>
          </div>
          ${addressPart}
          <div style="margin-top: 8px; border-top: 1px solid #1e293b; padding-top: 6px; text-align: right;">
            <a href="/incidents/${inc.id}" style="color: #38bdf8; text-decoration: none; font-weight: 600; font-size: 11px; display: inline-flex; align-items: center; gap: 4px;">
              <span>Inspect Forensics Dossier</span>
              <span>→</span>
            </a>
          </div>
        </div>
      `;
      marker.bindPopup(popupHtml);

      if (onSelectIncident) {
        marker.on('click', () => onSelectIncident(inc));
      }

      marker.addTo(incidentLayerGroupRef.current!);
    });
  }, [incidents, selectedIncidentId, onSelectIncident]);

  useEffect(() => {
    if (!aqiLayerGroupRef.current) return;
    aqiLayerGroupRef.current.clearLayers();

    aqiHotspots.forEach((point) => {
      const circle = L.circleMarker([point.lat, point.lon], {
        radius: 12,
        fillColor: point.aqi_value > 200 ? '#7c3aed' : point.aqi_value > 150 ? '#dc2626' : '#ea580c',
        fillOpacity: 0.35,
        color: point.aqi_value > 200 ? '#a78bfa' : point.aqi_value > 150 ? '#f87171' : '#fb923c',
        weight: 1.5,
      });

      circle.bindTooltip(`AQI: ${point.aqi_value.toFixed(0)} (${point.category}) | PM2.5: ${point.pm2_5.toFixed(1)}`, {
        sticky: true,
      });

      circle.addTo(aqiLayerGroupRef.current!);
    });
  }, [aqiHotspots]);

  return (
    <div className="relative w-full rounded-xl overflow-hidden border border-slate-800/90 shadow-2xl bg-[#060a12]" style={{ height }}>
      <div ref={mapContainerRef} className="w-full h-full" />
      {/* Precision Tactical Geospatial HUD Badge */}
      <div className="absolute top-3 left-3 z-[1000] bg-slate-950/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/80 text-[11px] text-slate-300 font-mono shadow-lg flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
        <span className="font-semibold text-slate-200">VADODARA METRO COMMAND</span>
        <span className="text-slate-500">|</span>
        <span className="text-slate-400">22.3072° N, 73.1812° E</span>
      </div>
    </div>
  );
};

