import React from 'react';
import { Shield, Cpu, MapPin, Database } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 py-10 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-white font-bold text-base">
              <Shield className="w-5 h-5 text-civic-400" />
              <span>CivicSense Platform</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              AI-Powered Civic Issue Intelligence transforming citizen reports into structured, actionable municipal interventions.
            </p>
          </div>

          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">AI / ML Pipeline</h4>
            <ul className="text-xs space-y-2">
              <li className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-civic-400" /> YOLO11 Object Detection</li>
              <li className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-civic-400" /> MobileNet / DINO Embeddings</li>
              <li className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-civic-400" /> Geospatial DBSCAN Clustering</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">Workflows</h4>
            <ul className="text-xs space-y-2 text-slate-400">
              <li>Citizen Multi-Source Reporting</li>
              <li>Spatial Duplicate Suppression</li>
              <li>5-Factor Priority Triage</li>
              <li>Human Resolution Verification</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white text-xs font-semibold uppercase tracking-wider mb-3">Transparency & Safety</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Priority scores represent explainable administrative triage estimates. Location metadata is sanitized for citizen privacy.
            </p>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-400">
          <div>© 2026 CivicSense Intelligence Systems. Autonomous Competition Build.</div>
          <div className="mt-2 sm:mt-0 font-mono text-[11px] text-civic-400">v1.0.0-PROD-VERIFIED</div>
        </div>
      </div>
    </footer>
  );
};
