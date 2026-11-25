import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { MapIssuePoint, HotspotCluster, IssueCategory } from '../types';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import { 
  MapPin, Flame, Layers, Filter, Sparkles, AlertTriangle, 
  ArrowRight, ShieldAlert, RefreshCw, Compass 
} from 'lucide-react';

// Fix Leaflet default icon issues in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom colored SVG pin markers for priority
const createCustomMarker = (band: string) => {
  const colorMap: Record<string, string> = {
    CRITICAL: '#EF4444',
    HIGH: '#F97316',
    MEDIUM: '#F59E0B',
    LOW: '#10B981',
  };
  const color = colorMap[band] || '#0284C7';

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${color}" width="32" height="32" stroke="#FFFFFF" stroke-width="1.5"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>`;
  return L.divIcon({
    html: svg,
    className: 'custom-map-pin',
    iconSize: [32, 32],
    iconAnchor: [16, 32],
    popupAnchor: [0, -32],
  });
};

export const MapIntelligencePage: React.FC = () => {
  const [issues, setIssues] = useState<MapIssuePoint[]>([]);
  const [hotspots, setHotspots] = useState<HotspotCluster[]>([]);
  const [categories, setCategories] = useState<IssueCategory[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters & Layers
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [viewMode, setViewMode] = useState<'MARKERS' | 'HOTSPOTS'>('MARKERS');

  const [selectedIssue, setSelectedIssue] = useState<MapIssuePoint | null>(null);

  const fetchMapData = async () => {
    try {
      const [issuesRes, hotspotsRes, catsRes] = await Promise.all([
        api.get('/map/issues'),
        api.get('/map/hotspots'),
        api.get('/categories')
      ]);
      setIssues(issuesRes.data);
      setHotspots(hotspotsRes.data);
      setCategories(catsRes.data);
    } catch (err) {
      console.error('Failed to load map data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMapData();
  }, []);

  const filteredIssues = issues.filter((i) => {
    const matchesCat = categoryFilter === 'ALL' || i.category_code === categoryFilter;
    const matchesStatus = statusFilter === 'ALL' || i.status === statusFilter;
    const matchesPriority = priorityFilter === 'ALL' || i.priority_band === priorityFilter;
    return matchesCat && matchesStatus && matchesPriority;
  });

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Top Filter Bar */}
      <div className="bg-white border-b border-slate-200 px-4 py-3 z-20 shadow-xs flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-700">
            <Compass className="w-4 h-4" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-900">Geospatial Intelligence Map</h1>
            <p className="text-[11px] text-slate-500">Live PostGIS / DBSCAN Spatial Analysis</p>
          </div>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
          <button
            onClick={() => setViewMode('MARKERS')}
            className={`px-3 py-1 rounded-lg transition ${
              viewMode === 'MARKERS' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Issue Markers ({filteredIssues.length})
          </button>
          <button
            onClick={() => setViewMode('HOTSPOTS')}
            className={`px-3 py-1 rounded-lg transition flex items-center gap-1.5 ${
              viewMode === 'HOTSPOTS' ? 'bg-civic-600 text-white shadow-xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Flame className="w-3.5 h-3.5" />
            <span>DBSCAN Hotspots ({hotspots.length})</span>
          </button>
        </div>

        {/* Filter Selects */}
        <div className="flex items-center gap-2">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-2.5 py-1 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
          >
            <option value="ALL">All Categories</option>
            {categories.map((c) => (
              <option key={c.code} value={c.code}>{c.display_name}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2.5 py-1 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
          >
            <option value="ALL">All Statuses</option>
            <option value="REPORTED">Reported</option>
            <option value="VERIFIED">Verified</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="RESOLVED">Resolved</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-2.5 py-1 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Main Map + Hotspot Sidebar Layout */}
      <div className="flex-1 flex relative overflow-hidden">
        {/* Leaflet Map Canvas */}
        <div className="flex-1 relative z-10">
          <MapContainer
            center={[12.9716, 77.5946]}
            zoom={14}
            scrollWheelZoom={true}
            className="w-full h-full"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* Individual Issue Markers */}
            {viewMode === 'MARKERS' &&
              filteredIssues.map((issue) => (
                <Marker
                  key={issue.id}
                  position={[issue.latitude, issue.longitude]}
                  icon={createCustomMarker(issue.priority_band)}
                  eventHandlers={{
                    click: () => setSelectedIssue(issue),
                  }}
                >
                  <Popup>
                    <div className="p-1 space-y-2 max-w-xs text-xs">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono font-bold text-civic-700 bg-civic-50 px-2 py-0.5 rounded border border-civic-200">
                          {issue.issue_code}
                        </span>
                        <StatusBadge status={issue.status} size="sm" />
                      </div>
                      <div className="font-semibold text-slate-900 text-sm">{issue.title}</div>
                      <div className="flex items-center justify-between text-slate-500 pt-1">
                        <span>{issue.category_name}</span>
                        <PriorityBadge score={issue.priority_score} band={issue.priority_band} size="sm" />
                      </div>
                      <Link
                        to={`/issues/${issue.id}`}
                        className="block text-center w-full py-1.5 bg-civic-600 hover:bg-civic-700 text-white rounded-lg font-semibold transition mt-2"
                      >
                        Inspect Issue Details →
                      </Link>
                    </div>
                  </Popup>
                </Marker>
              ))}

            {/* DBSCAN Hotspots Circles */}
            {viewMode === 'HOTSPOTS' &&
              hotspots.map((spot) => {
                const color = spot.severity_level === 'SEVERE' ? '#EF4444' : spot.severity_level === 'HIGH' ? '#F97316' : '#F59E0B';
                return (
                  <Circle
                    key={spot.cluster_id}
                    center={[spot.center_lat, spot.center_lng]}
                    radius={spot.radius_meters}
                    pathOptions={{
                      color: color,
                      fillColor: color,
                      fillOpacity: 0.35,
                      weight: 2,
                    }}
                  >
                    <Popup>
                      <div className="p-1 space-y-2 text-xs">
                        <div className="font-bold text-slate-900 flex items-center gap-1.5">
                          <Flame className="w-4 h-4 text-red-600" />
                          <span>Civic Defect Cluster #{spot.cluster_id + 1}</span>
                        </div>
                        <div><span className="font-semibold text-slate-700">Dominant Category:</span> {spot.dominant_category}</div>
                        <div><span className="font-semibold text-slate-700">Recurrence Density:</span> {spot.issue_count} complaints within {Math.round(spot.radius_meters)}m</div>
                        <div><span className="font-semibold text-slate-700">Average Priority:</span> {spot.average_priority} / 100</div>
                        <div className="font-bold text-red-700 uppercase">Severity: {spot.severity_level} RISK</div>
                      </div>
                    </Popup>
                  </Circle>
                );
              })}
          </MapContainer>
        </div>

        {/* Hotspot Intelligence Sidebar Panel */}
        {viewMode === 'HOTSPOTS' && (
          <div className="w-80 bg-white border-l border-slate-200 z-20 shadow-md p-4 space-y-4 overflow-y-auto">
            <div>
              <h2 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                <Flame className="w-4 h-4 text-red-600" />
                <span>DBSCAN Recurrence Hotspots</span>
              </h2>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Observed spatial complaint concentrations computed via algorithmic density clustering.
              </p>
            </div>

            <div className="space-y-3">
              {hotspots.length > 0 ? (
                hotspots.map((spot) => (
                  <div key={spot.cluster_id} className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800">Cluster #{spot.cluster_id + 1}</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        spot.severity_level === 'SEVERE' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                      }`}>
                        {spot.severity_level}
                      </span>
                    </div>
                    <div><span className="text-slate-500">Category:</span> <span className="font-semibold">{spot.dominant_category}</span></div>
                    <div><span className="text-slate-500">Density:</span> {spot.issue_count} complaints within {Math.round(spot.radius_meters)}m</div>
                    <div><span className="text-slate-500">Avg Priority:</span> <span className="font-mono font-bold text-civic-700">{spot.average_priority}</span></div>
                  </div>
                ))
              ) : (
                <div className="text-xs text-slate-400 text-center py-6">
                  No spatial defect concentrations detected at current epsilon threshold.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
