import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { AnalyticsSummary, Issue } from '../types';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Shield, Camera, Cpu, Layers, CheckCircle2, ArrowRight, 
  MapPin, AlertTriangle, Users, BarChart3, Clock, Sparkles
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [recentIssues, setRecentIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLandingData = async () => {
      try {
        const [sumRes, issuesRes] = await Promise.all([
          api.get('/analytics/summary'),
          api.get('/issues?limit=5')
        ]);
        setSummary(sumRes.data);
        setRecentIssues(issuesRes.data);
      } catch (err) {
        console.error('Error fetching landing data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLandingData();
  }, []);

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-civic-50/60 via-white to-slate-50 border-b border-slate-200 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-civic-100/80 border border-civic-200 text-civic-800 text-xs font-semibold tracking-wide uppercase">
              <Sparkles className="w-3.5 h-3.5 text-civic-600" />
              Next-Generation Urban Governance
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
              AI-Powered Civic Issue <span className="text-civic-600">Intelligence</span>
            </h1>

            <p className="text-base sm:text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto">
              Transforming disconnected citizen complaints into structured, explainable municipal intelligence. Real-time computer vision detection, multi-factor duplicate deduplication, and explainable priority triage.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
              <Link
                to="/report"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-civic-600 hover:bg-civic-700 text-white font-semibold text-sm shadow-md hover:shadow-lg transition transform hover:-translate-y-0.5"
              >
                <Camera className="w-4 h-4" />
                Report an Issue
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
              <Link
                to="/map"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white hover:bg-slate-50 text-slate-700 font-semibold text-sm border border-slate-300 shadow-sm transition"
              >
                <MapPin className="w-4 h-4 text-emerald-600" />
                Explore Live Map
              </Link>
              <Link
                to="/auth"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-semibold text-sm shadow-sm transition"
              >
                <Users className="w-4 h-4 text-civic-400" />
                Launch Demo Role
              </Link>
            </div>
          </div>

          {/* Real Backend Statistics Bar */}
          <div className="mt-14 max-w-5xl mx-auto grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm text-center">
              <div className="text-3xl font-extrabold text-slate-900">
                {summary ? summary.total_issues : '7+'}
              </div>
              <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">Total Issues Tracked</div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm text-center">
              <div className="text-3xl font-extrabold text-amber-600">
                {summary ? summary.in_progress_issues : '2'}
              </div>
              <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">Dispatched Field Teams</div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm text-center">
              <div className="text-3xl font-extrabold text-emerald-600">
                {summary ? summary.resolved_issues : '1'}
              </div>
              <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">Verified Resolutions</div>
            </div>
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-sm text-center">
              <div className="text-3xl font-extrabold text-civic-600">
                {summary ? summary.duplicate_reports_identified : '3+'}
              </div>
              <div className="text-xs font-medium text-slate-500 mt-1 uppercase tracking-wider">Duplicates Deduplicated</div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Complete Civic Workflow</h2>
          <p className="text-sm text-slate-600 mt-2">
            From the moment a citizen snaps a photo to field resolution and supervisor verification.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">1</div>
            <h3 className="font-semibold text-slate-900 text-base">Citizen Capture & Privacy</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Citizens submit photos with automatic EXIF metadata stripping and explicit privacy consent.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center font-bold">2</div>
            <h3 className="font-semibold text-slate-900 text-base">Computer Vision Inference</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              YOLO11 detects civic anomalies (potholes, cracks, waste, lighting, infrastructure) with confidence bounding boxes.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold">3</div>
            <h3 className="font-semibold text-slate-900 text-base">Duplicate Deduplication</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Visual embeddings and geospatial proximity suppress redundant reports while aggregating community urgency.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-3 relative">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">4</div>
            <h3 className="font-semibold text-slate-900 text-base">Explainable Triage & Audit</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              5-factor mathematical priority triage, department routing, field resolution, and supervisor sign-off.
            </p>
          </div>
        </div>
      </section>

      {/* Recent Live Issues Feed */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Live Civic Issues Feed</h2>
            <p className="text-xs text-slate-500">Real-time status updates directly from municipal departments</p>
          </div>
          <Link to="/map" className="text-sm font-semibold text-civic-600 hover:text-civic-700 flex items-center gap-1">
            View All On Map <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="divide-y divide-slate-100">
            {recentIssues.length > 0 ? (
              recentIssues.map((issue) => (
                <div key={issue.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-slate-50/80 transition">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-civic-700 bg-civic-50 px-2 py-0.5 rounded border border-civic-200">
                        {issue.issue_code}
                      </span>
                      <StatusBadge status={issue.status} size="sm" />
                      <PriorityBadge score={issue.priority_score} band={issue.priority_band} size="sm" />
                    </div>
                    <h3 className="font-semibold text-slate-900 text-sm">{issue.title}</h3>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {issue.address || 'Urban Sector'}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {new Date(issue.created_at).toLocaleDateString()}</span>
                      <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {issue.report_count} report(s)</span>
                    </div>
                  </div>

                  <Link
                    to={`/issues/${issue.id}`}
                    className="inline-flex items-center justify-center px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-semibold transition"
                  >
                    View Details
                  </Link>
                </div>
              ))
            ) : (
              <div className="p-8 text-center text-slate-500 text-sm">
                Loading live civic reports...
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};
