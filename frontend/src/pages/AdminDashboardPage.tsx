import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { AnalyticsSummary, Issue, IssueCategory } from '../types';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  LineChart, Line, CartesianGrid, Legend, PieChart, Pie, Cell 
} from 'recharts';
import { 
  LayoutDashboard, AlertCircle, CheckCircle2, Clock, 
  Users, Layers, ArrowUpRight, Search, Filter, ShieldAlert 
} from 'lucide-react';

const PRIORITY_COLORS: Record<string, string> = {
  LOW: '#10B981',
  MEDIUM: '#F59E0B',
  HIGH: '#F97316',
  CRITICAL: '#EF4444',
};

export const AdminDashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [distribution, setDistribution] = useState<any>(null);
  const [trends, setTrends] = useState<any[]>([]);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [categories, setCategories] = useState<IssueCategory[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter & Search
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedPriority, setSelectedPriority] = useState<string>('ALL');

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const [sumRes, distRes, trendRes, issueRes, catRes] = await Promise.all([
          api.get('/analytics/summary'),
          api.get('/analytics/distribution'),
          api.get('/analytics/trends?days=7'),
          api.get('/issues?limit=100'),
          api.get('/categories')
        ]);
        setSummary(sumRes.data);
        setDistribution(distRes.data);
        setTrends(trendRes.data);
        setIssues(issueRes.data);
        setCategories(catRes.data);
      } catch (err) {
        console.error('Failed to load admin analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  const filteredIssues = issues.filter((i) => {
    const matchesSearch = 
      i.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      i.issue_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (i.address && i.address.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCat = selectedCategory === 'ALL' || (i.category_code && i.category_code === selectedCategory);
    const matchesStatus = selectedStatus === 'ALL' || i.status === selectedStatus;
    const matchesPriority = selectedPriority === 'ALL' || i.priority_band === selectedPriority;
    return matchesSearch && matchesCat && matchesStatus && matchesPriority;
  });

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-slate-900 text-white text-xs font-semibold">
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Municipal Dispatch Command</span>
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight mt-1">
            Administrative Operations & Triage
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/map"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 shadow-xs transition"
          >
            <span>Geospatial Hotspots</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
          <Link
            to="/report"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-civic-600 hover:bg-civic-700 rounded-xl text-xs font-semibold text-white shadow-xs transition"
          >
            <span>+ Log Direct Report</span>
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Issues</div>
          <div className="text-2xl font-bold text-slate-900 mt-1">{summary ? summary.total_issues : '-'}</div>
          <div className="text-[11px] text-slate-400 mt-1 font-mono">100% DB Synced</div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-semibold text-blue-600 uppercase tracking-wider">Pending Review</div>
          <div className="text-2xl font-bold text-blue-700 mt-1">{summary ? summary.pending_issues : '-'}</div>
          <div className="text-[11px] text-slate-400 mt-1">Awaiting dispatch</div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-semibold text-amber-600 uppercase tracking-wider">In Progress</div>
          <div className="text-2xl font-bold text-amber-700 mt-1">{summary ? summary.in_progress_issues : '-'}</div>
          <div className="text-[11px] text-slate-400 mt-1">Crews dispatched</div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Resolved</div>
          <div className="text-2xl font-bold text-emerald-700 mt-1">{summary ? summary.resolved_issues : '-'}</div>
          <div className="text-[11px] text-slate-400 mt-1">Supervised closure</div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
          <div className="text-xs font-semibold text-civic-600 uppercase tracking-wider">Duplicates Merged</div>
          <div className="text-2xl font-bold text-civic-700 mt-1">{summary ? summary.duplicate_reports_identified : '-'}</div>
          <div className="text-[11px] text-slate-400 mt-1">Vision deduplicated</div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-red-200 bg-red-50/20 shadow-xs">
          <div className="text-xs font-semibold text-red-600 uppercase tracking-wider">Critical / High</div>
          <div className="text-2xl font-bold text-red-700 mt-1">{summary ? summary.high_critical_count : '-'}</div>
          <div className="text-[11px] text-red-500 mt-1 font-medium">Needs immediate triage</div>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Breakdown Bar Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Issues by Category</h2>
          <div className="h-64">
            {distribution && distribution.categories ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={distribution.categories} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="category_name" angle={-15} textAnchor="end" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                  <Bar dataKey="count" fill="#0284C7" radius={[4, 4, 0, 0]} name="Reports" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">Loading chart...</div>
            )}
          </div>
        </div>

        {/* 7-Day Trend Line Chart */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">7-Day Intake vs Resolution Trend</h2>
          <div className="h-64">
            {trends && trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                  <Legend wrapperStyle={{ fontSize: 11, paddingTop: 10 }} />
                  <Line type="monotone" dataKey="reported" stroke="#2563EB" strokeWidth={2.5} name="Reported" />
                  <Line type="monotone" dataKey="resolved" stroke="#10B981" strokeWidth={2.5} name="Resolved" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">Loading trend...</div>
            )}
          </div>
        </div>
      </div>

      {/* Issues Management Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden space-y-4 p-5">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Municipal Issues Directory</h2>
            <p className="text-xs text-slate-500">Sorted by explainable priority score</p>
          </div>

          {/* Search & Filters */}
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Search code, title, address..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 border border-slate-300 rounded-lg text-xs w-48 focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
              />
            </div>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
            >
              <option value="ALL">All Categories</option>
              {categories.map((c) => (
                <option key={c.code} value={c.code}>{c.display_name}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
            >
              <option value="ALL">All Statuses</option>
              <option value="REPORTED">Reported</option>
              <option value="VERIFIED">Verified</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="RESOLVED">Resolved</option>
            </select>

            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value)}
              className="px-2.5 py-1.5 border border-slate-300 rounded-lg text-xs bg-white text-slate-700"
            >
              <option value="ALL">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase font-semibold border-y border-slate-200">
              <tr>
                <th className="py-3 px-3">Issue Code</th>
                <th className="py-3 px-3">Category</th>
                <th className="py-3 px-3">Title & Location</th>
                <th className="py-3 px-3">Priority Score</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-3">Reports</th>
                <th className="py-3 px-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredIssues.map((issue) => (
                <tr key={issue.id} className="hover:bg-slate-50/80 transition">
                  <td className="py-3 px-3 font-mono font-bold text-civic-700">
                    <Link to={`/issues/${issue.id}`} className="hover:underline">
                      {issue.issue_code}
                    </Link>
                  </td>
                  <td className="py-3 px-3 font-medium text-slate-800">
                    {issue.category_name || 'Civic Defect'}
                  </td>
                  <td className="py-3 px-3">
                    <div className="font-semibold text-slate-900">{issue.title}</div>
                    <div className="text-slate-400 text-[11px]">{issue.address || 'Urban Sector'}</div>
                  </td>
                  <td className="py-3 px-3">
                    <PriorityBadge score={issue.priority_score} band={issue.priority_band} size="sm" />
                  </td>
                  <td className="py-3 px-3">
                    <StatusBadge status={issue.status} size="sm" />
                  </td>
                  <td className="py-3 px-3 font-mono text-slate-700 font-medium">
                    {issue.report_count}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <Link
                      to={`/issues/${issue.id}`}
                      className="px-3 py-1.5 bg-civic-50 hover:bg-civic-100 text-civic-700 rounded-lg font-semibold transition inline-block"
                    >
                      Manage
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
