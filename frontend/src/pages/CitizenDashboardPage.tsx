import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api, { authStorage } from '../api/client';
import { Report, Issue } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { PriorityBadge } from '../components/PriorityBadge';
import { Camera, Clock, MapPin, CheckCircle2, AlertCircle, ArrowRight, UserCheck } from 'lucide-react';

export const CitizenDashboardPage: React.FC = () => {
  const user = authStorage.getUser();
  const [reports, setReports] = useState<Report[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCitizenData = async () => {
      try {
        const [repRes, issueRes] = await Promise.all([
          api.get('/reports/mine').catch(() => ({ data: [] })),
          api.get('/issues?limit=6')
        ]);
        setReports(repRes.data || []);
        setIssues(issueRes.data || []);
      } catch (err) {
        console.error('Failed to load citizen data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCitizenData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto py-10 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Welcome Header */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-civic-50 text-civic-700 text-xs font-semibold border border-civic-200">
            <UserCheck className="w-3.5 h-3.5" />
            <span>Citizen Portal</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">
            Welcome back, {user ? user.full_name : 'Civic Contributor'}
          </h1>
          <p className="text-xs text-slate-500">
            Track your submitted infrastructure complaints, view field updates, and support neighborhood issues.
          </p>
        </div>

        <Link
          to="/report"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-civic-600 hover:bg-civic-700 text-white rounded-xl text-sm font-semibold shadow-sm transition"
        >
          <Camera className="w-4 h-4" />
          Report New Issue
        </Link>
      </div>

      {/* Reports Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900">My Submitted Reports</h2>
          <span className="text-xs text-slate-500">{reports.length} report(s)</span>
        </div>

        {reports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reports.map((report) => (
              <div key={report.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3 flex flex-col justify-between">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-civic-700 bg-civic-50 px-2 py-0.5 rounded border border-civic-200">
                      {report.report_code}
                    </span>
                    <StatusBadge status={report.status} size="sm" />
                  </div>

                  <h3 className="font-semibold text-slate-900 text-sm">
                    {report.citizen_category_suggestion || 'Civic Issue'}
                  </h3>

                  <p className="text-xs text-slate-500 line-clamp-2">
                    {report.citizen_comment || report.address_text || 'Submitted via mobile reporting.'}
                  </p>

                  <div className="text-[11px] text-slate-400 flex items-center gap-1 font-mono">
                    <Clock className="w-3 h-3" />
                    <span>{new Date(report.created_at).toLocaleString()}</span>
                  </div>
                </div>

                {report.issue_id && (
                  <Link
                    to={`/issues/${report.issue_id}`}
                    className="inline-flex items-center justify-center gap-1.5 w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-lg text-xs font-semibold transition"
                  >
                    <span>Track Municipal Action</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center space-y-3 shadow-xs">
            <div className="w-12 h-12 rounded-xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
              <Camera className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-slate-800 text-sm">No personal complaints submitted yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              When you report civic issues like potholes or garbage accumulation, they will appear here with live resolution tracking.
            </p>
            <Link
              to="/report"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-civic-600 hover:bg-civic-700 text-white rounded-lg text-xs font-semibold shadow-xs transition"
            >
              Report Your First Issue
            </Link>
          </div>
        )}
      </div>

      {/* Community Active Issues */}
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">Active Issues In Your Area</h2>
            <p className="text-xs text-slate-500">Other civic hazards being addressed by municipal departments</p>
          </div>
          <Link to="/map" className="text-xs font-semibold text-civic-600 hover:underline">
            View Live City Map →
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {issues.map((issue) => (
            <div key={issue.id} className="bg-white rounded-2xl border border-slate-200 p-5 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-slate-700 bg-slate-100 px-2 py-0.5 rounded">
                  {issue.issue_code}
                </span>
                <PriorityBadge score={issue.priority_score} band={issue.priority_band} size="sm" />
              </div>

              <div>
                <h3 className="font-semibold text-slate-900 text-sm">{issue.title}</h3>
                <div className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                  <MapPin className="w-3.5 h-3.5" />
                  <span className="line-clamp-1">{issue.address || 'Urban Sector'}</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                <StatusBadge status={issue.status} size="sm" />
                <Link to={`/issues/${issue.id}`} className="font-semibold text-civic-600 hover:text-civic-700">
                  Inspect →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
