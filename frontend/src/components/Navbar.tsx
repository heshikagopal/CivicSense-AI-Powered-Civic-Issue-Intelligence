import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { authStorage } from '../api/client';
import { Shield, Map, PlusCircle, LayoutDashboard, UserCheck, LogOut, LogIn, Activity } from 'lucide-react';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const user = authStorage.getUser();

  const handleLogout = () => {
    authStorage.clearAuth();
    navigate('/');
    window.location.reload();
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-civic-600 flex items-center justify-center text-white shadow-md group-hover:bg-civic-700 transition">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <span className="text-lg font-bold text-slate-900 tracking-tight">Civic<span className="text-civic-600">Sense</span></span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold px-2 py-0.5 bg-civic-50 text-civic-700 rounded-full border border-civic-200">
                AI Intelligence
              </span>
            </div>
          </Link>

          {/* Navigation links */}
          <nav className="hidden md:flex items-center gap-1">
            <Link
              to="/"
              className={`px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/') ? 'text-civic-600 bg-civic-50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              Overview
            </Link>
            <Link
              to="/report"
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/report') ? 'text-civic-600 bg-civic-50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <PlusCircle className="w-4 h-4 text-civic-600" />
              Report Issue
            </Link>
            <Link
              to="/map"
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/map') ? 'text-civic-600 bg-civic-50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Map className="w-4 h-4 text-emerald-600" />
              Map Intelligence
            </Link>
            <Link
              to="/citizen"
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/citizen') ? 'text-civic-600 bg-civic-50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <UserCheck className="w-4 h-4 text-indigo-600" />
              Citizen Hub
            </Link>
            <Link
              to="/admin"
              className={`flex items-center gap-1.5 px-3 py-2 rounded-md text-sm font-medium transition ${
                isActive('/admin') ? 'text-civic-600 bg-civic-50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <LayoutDashboard className="w-4 h-4 text-amber-600" />
              Admin Center
            </Link>
          </nav>

          {/* User / Authentication actions */}
          <div className="flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-2">
                <div className="hidden sm:block text-right">
                  <div className="text-xs font-semibold text-slate-800">{user.full_name}</div>
                  <div className="text-[10px] uppercase font-bold text-civic-600 tracking-wider">{user.role}</div>
                </div>
                <button
                  onClick={handleLogout}
                  title="Log out"
                  className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                to="/auth"
                className="flex items-center gap-1.5 px-3.5 py-1.5 bg-civic-600 hover:bg-civic-700 text-white rounded-lg text-sm font-medium shadow-sm transition"
              >
                <LogIn className="w-4 h-4" />
                <span>Sign In / Demo</span>
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
