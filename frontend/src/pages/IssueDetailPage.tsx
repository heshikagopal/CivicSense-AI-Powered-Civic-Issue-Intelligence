import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api, { authStorage } from '../api/client';
import { IssueDetail, PriorityBreakdown, Department, DuplicateCandidate } from '../types';
import { PriorityBadge } from '../components/PriorityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { 
  Shield, MapPin, Clock, Users, Cpu, FileText, CheckCircle2, 
  AlertTriangle, RefreshCw, Edit3, Send, Check, X, ArrowLeft 
} from 'lucide-react';

export const IssueDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const user = authStorage.getUser();

  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [priority, setPriority] = useState<PriorityBreakdown | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals & Action States
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideScore, setOverrideScore] = useState<number>(75);
  const [overrideReason, setOverrideReason] = useState<string>('');

  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedDeptId, setSelectedDeptId] = useState<string>('');
  const [assignNotes, setAssignNotes] = useState<string>('');

  const [showResolutionModal, setShowResolutionModal] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState<string>('');
  const [proofImageUrl, setProofImageUrl] = useState<string>('');

  const [verificationNotes, setVerificationNotes] = useState<string>('');

  const fetchDetail = async () => {
    try {
      const [issueRes, prioRes, deptsRes, auditRes] = await Promise.all([
        api.get(`/issues/${id}`),
        api.get(`/issues/${id}/priority`),
        api.get('/departments'),
        api.get(`/issues/${id}/audit`)
      ]);
      setIssue(issueRes.data);
      setPriority(prioRes.data);
      setDepartments(deptsRes.data);
      setAuditLogs(auditRes.data);
      if (issueRes.data.assigned_department_id) {
        setSelectedDeptId(issueRes.data.assigned_department_id);
      }
    } catch (err) {
      console.error('Failed to load issue detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  // Handle Priority Override
  const handleOverridePriority = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideReason.trim()) {
      alert('Mandatory justification reason required.');
      return;
    }
    try {
      await api.post(`/issues/${id}/priority/override`, {
        new_priority_score: overrideScore,
        override_reason: overrideReason
      });
      setShowOverrideModal(false);
      fetchDetail();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to override priority.');
    }
  };

  // Handle Department Assignment
  const handleAssignDepartment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post(`/issues/${id}/assign`, {
        department_id: selectedDeptId,
        notes: assignNotes
      });
      setShowAssignModal(false);
      fetchDetail();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to assign department.');
    }
  };

  // Handle Resolution Submission
  const handleSubmitResolution = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post(`/issues/${id}/resolution`, {
        resolution_notes: resolutionNotes,
        proof_image_url: proofImageUrl || (issue?.reports[0]?.image_url || '/static/samples/pothole_sample.jpg')
      });
      setShowResolutionModal(false);
      fetchDetail();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to submit resolution.');
    }
  };

  // Handle Supervisor Verification
  const handleVerifyResolution = async (resolutionId: string, approve: boolean) => {
    try {
      await api.post(`/resolution/${resolutionId}/verify`, {
        is_verified: approve,
        verification_notes: verificationNotes || (approve ? 'Supervisor on-site verification confirmed.' : 'Rework requested.')
      });
      fetchDetail();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to verify resolution.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto py-20 px-4 text-center text-slate-500 text-sm">
        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-civic-600" />
        Loading civic intelligence details...
      </div>
    );
  }

  if (!issue) {
    return (
      <div className="max-w-7xl mx-auto py-20 px-4 text-center">
        <h2 className="text-xl font-bold text-slate-900">Issue Not Found</h2>
        <Link to="/admin" className="text-civic-600 text-sm mt-2 inline-block">Return to Directory</Link>
      </div>
    );
  }

  const primaryReport = issue.reports && issue.reports.length > 0 ? issue.reports[0] : null;

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Back and Header */}
      <div className="space-y-4">
        <Link to="/admin" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Operations Directory</span>
        </Link>

        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5">
              <span className="font-mono text-sm font-bold text-civic-800 bg-civic-50 px-2.5 py-0.5 rounded-lg border border-civic-200">
                {issue.issue_code}
              </span>
              <StatusBadge status={issue.status} size="md" />
              <PriorityBadge score={issue.priority_score} band={issue.priority_band} size="md" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 mt-1">{issue.title}</h1>
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 pt-1">
              <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {issue.address}</span>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> First Reported: {new Date(issue.first_reported_at).toLocaleString()}</span>
              <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {issue.report_count} Supporting Citizen Report(s)</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => setShowOverrideModal(true)}
              className="px-3.5 py-2 rounded-xl border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-xs transition flex items-center gap-1.5"
            >
              <Edit3 className="w-3.5 h-3.5 text-amber-600" />
              <span>Override Priority</span>
            </button>

            <button
              onClick={() => setShowAssignModal(true)}
              className="px-3.5 py-2 rounded-xl bg-civic-600 hover:bg-civic-700 text-white text-xs font-semibold shadow-xs transition flex items-center gap-1.5"
            >
              <Users className="w-3.5 h-3.5" />
              <span>Assign Department</span>
            </button>

            {issue.status !== 'RESOLVED' && (
              <button
                onClick={() => setShowResolutionModal(true)}
                className="px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-xs transition flex items-center gap-1.5"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Submit Resolution</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Main Grid: Visuals & Priority Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Visual AI Inspection (7 Cols) */}
        <div className="lg:col-span-7 space-y-6">
          {/* Primary Evidence Photo */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-civic-600" />
              Computer Vision Inspection & Bounding Box
            </h2>

            <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-200 aspect-16/10 flex items-center justify-center">
              <img
                src={primaryReport?.image_url || '/static/samples/pothole_sample.jpg'}
                alt="Civic Issue Proof"
                className="w-full h-full object-contain"
              />
            </div>

            {/* Detections List */}
            {issue.recent_detections && issue.recent_detections.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-slate-100">
                <div className="text-xs font-semibold text-slate-600">Model Detections & Confidence:</div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {issue.recent_detections.map((d, i) => (
                    <div key={i} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs flex items-center justify-between">
                      <span className="font-semibold text-slate-800 uppercase tracking-wide">{d.category_code}</span>
                      <span className="font-mono font-bold text-civic-700">{Math.round(d.confidence * 100)}% Confidence</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Citizen Reports Supporting This Issue */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-civic-600" />
              Linked Citizen Reports ({issue.reports.length})
            </h2>

            <div className="divide-y divide-slate-100">
              {issue.reports.map((rep) => (
                <div key={rep.id} className="py-3 flex items-start justify-between gap-4 text-xs">
                  <div>
                    <div className="font-mono font-bold text-slate-800">{rep.report_code}</div>
                    <div className="text-slate-600 mt-0.5">{rep.citizen_comment || 'Citizen defect report submitted.'}</div>
                    <div className="text-slate-400 text-[11px] font-mono mt-1">
                      {new Date(rep.created_at).toLocaleString()} • Location: {rep.address_text || 'GPS Verified'}
                    </div>
                  </div>
                  <StatusBadge status={rep.status} size="sm" />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Explainable Priority & Triage (5 Cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Priority Scorecard */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Explainable Priority Engine
                </h2>
                <div className="text-[11px] text-slate-500">
                  Calculated Administrative Triage Score
                </div>
              </div>
              <PriorityBadge score={issue.priority_score} band={issue.priority_band} size="lg" />
            </div>

            {priority?.is_overridden && (
              <div className="p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-800 space-y-1">
                <div className="font-bold flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Administrative Priority Override Active</span>
                </div>
                <div className="text-[11px] italic">"{priority.override_reason}"</div>
              </div>
            )}

            {/* 5 Factors Cards */}
            <div className="space-y-2.5">
              {priority?.factors && Object.entries(priority.factors).map(([key, f]) => (
                <div key={key} className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-800 capitalize">
                      {key.replace('_', ' ')}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-slate-500 text-[11px]">Weight: {f.weight_percent}%</span>
                      <span className="font-mono font-bold text-civic-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                        {Math.round(f.score)} / 100
                      </span>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {f.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Department Assignment Record */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
              Department Assignment
            </h2>
            <div className="text-xs space-y-2">
              <div>
                <span className="text-slate-500">Department:</span>{' '}
                <span className="font-semibold text-slate-800">{issue.assigned_department_name || 'Roads & Bridges'}</span>
              </div>
              <div>
                <span className="text-slate-500">Assigned Officer:</span>{' '}
                <span className="font-semibold text-slate-800">{issue.assigned_officer_id ? 'Marcus Vance (Field Team)' : 'Unassigned'}</span>
              </div>
            </div>
          </div>

          {/* Resolutions & Human Verification */}
          {issue.resolutions && issue.resolutions.length > 0 && (
            <div className="bg-white p-5 rounded-2xl border border-emerald-200 bg-emerald-50/10 shadow-xs space-y-4">
              <h2 className="text-sm font-bold text-emerald-800 uppercase tracking-wider flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Resolution Record & Supervisor Verification
              </h2>

              {issue.resolutions.map((res) => (
                <div key={res.id} className="space-y-3 text-xs">
                  <div className="p-3 bg-white rounded-xl border border-emerald-200 space-y-2">
                    <div className="font-semibold text-slate-800">Field Notes:</div>
                    <p className="text-slate-600 leading-relaxed">{res.notes}</p>
                    <div className="text-[11px] text-slate-400 font-mono">
                      Resolved by: {res.resolved_by_name} on {res.resolved_at}
                    </div>
                  </div>

                  {/* Verification Status */}
                  <div className="p-3 bg-white rounded-xl border border-slate-200 flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-slate-800">Supervisor Verification:</div>
                      <div className="text-[11px] text-slate-500">
                        {res.is_verified ? `Verified by ${res.verified_by_name || 'Chief Officer'}` : 'Pending Quality Sign-Off'}
                      </div>
                    </div>
                    {res.is_verified ? (
                      <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 font-bold rounded-full text-xs">
                        Verified
                      </span>
                    ) : (
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleVerifyResolution(res.id, true)}
                          className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-semibold transition"
                        >
                          Approve Sign-Off
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Audit Logs */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-600" />
              Administrative Audit Trail
            </h2>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {auditLogs.map((log) => (
                <div key={log.id} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-0.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-800">{log.action}</span>
                    <span className="text-[10px] text-slate-400 font-mono">{log.timestamp}</span>
                  </div>
                  <div className="text-slate-500 text-[11px]">By: {log.user_name}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* OVERRIDE PRIORITY MODAL */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900">Administrative Priority Override</h3>
            <p className="text-xs text-slate-500">
              Overrides the automated triage score. Mandatory justification is required and recorded in the immutable audit log.
            </p>

            <form onSubmit={handleOverridePriority} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  New Priority Score (0 to 100): <span className="font-bold font-mono text-civic-700">{overrideScore}</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={overrideScore}
                  onChange={(e) => setOverrideScore(parseInt(e.target.value))}
                  className="w-full accent-civic-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Mandatory Justification Reason</label>
                <textarea
                  required
                  rows={3}
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  placeholder="e.g. VIP transit corridor / Imminent monsoon flooding risk..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowOverrideModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl text-xs font-semibold transition shadow-xs"
                >
                  Save Override & Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ASSIGN DEPARTMENT MODAL */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900">Assign Municipal Department</h3>

            <form onSubmit={handleAssignDepartment} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Department</label>
                <select
                  value={selectedDeptId}
                  onChange={(e) => setSelectedDeptId(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs bg-white text-slate-800"
                >
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Dispatch Instructions / Notes</label>
                <textarea
                  rows={3}
                  value={assignNotes}
                  onChange={(e) => setAssignNotes(e.target.value)}
                  placeholder="Dispatch instructions for field engineering crew..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAssignModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-civic-600 hover:bg-civic-700 text-white rounded-xl text-xs font-semibold transition shadow-xs"
                >
                  Confirm Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RESOLUTION SUBMISSION MODAL */}
      {showResolutionModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 space-y-4 shadow-xl">
            <h3 className="text-lg font-bold text-slate-900">Submit Work Completion Resolution</h3>
            <p className="text-xs text-slate-500">
              Submitted by field officer. Subject to quality verification by municipal supervisor.
            </p>

            <form onSubmit={handleSubmitResolution} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Work Completion Notes</label>
                <textarea
                  required
                  rows={3}
                  value={resolutionNotes}
                  onChange={(e) => setResolutionNotes(e.target.value)}
                  placeholder="Describe repair actions taken (e.g. cold-mix asphalt patch compacted)..."
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Resolution Proof Image URL</label>
                <input
                  type="text"
                  value={proofImageUrl}
                  onChange={(e) => setProofImageUrl(e.target.value)}
                  placeholder="/static/samples/pothole_sample.jpg"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowResolutionModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-xl text-xs font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-semibold transition shadow-xs"
                >
                  Submit for Verification
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
