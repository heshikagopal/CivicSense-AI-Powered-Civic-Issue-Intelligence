import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { authStorage } from '../api/client';
import { Shield, Lock, Mail, User, Phone, CheckCircle2, AlertCircle } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState<'citizen' | 'officer' | 'admin'>('citizen');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuickDemo = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setIsLogin(true);
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isLogin) {
        // FastAPI OAuth2 requires form data
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });

        authStorage.setAuth(res.data.access_token, res.data.user);
        if (res.data.user.role === 'admin') {
          navigate('/admin');
        } else if (res.data.user.role === 'officer') {
          navigate('/admin');
        } else {
          navigate('/citizen');
        }
      } else {
        const res = await api.post('/auth/register', {
          email,
          password,
          full_name: fullName,
          phone,
          role
        });

        // Auto login after register
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);
        const loginRes = await api.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        authStorage.setAuth(loginRes.data.access_token, loginRes.data.user);
        navigate('/citizen');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 px-4">
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-civic-100 text-civic-700 rounded-xl flex items-center justify-center mx-auto">
            <Shield className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">
            {isLogin ? 'Sign In to CivicSense' : 'Register Citizen Account'}
          </h1>
          <p className="text-xs text-slate-500">
            {isLogin ? 'Access your reports, administrative triage, or city intelligence' : 'Join thousands of citizens improving urban infrastructure'}
          </p>
        </div>

        {/* 1-Click Competition Demo Buttons */}
        <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
          <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider text-center">
            One-Click Demo Roles (For Evaluators)
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleQuickDemo('admin@civicsense.org', 'Admin123!')}
              className="px-2 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800 shadow-xs transition"
            >
              👑 Admin
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('officer@civicsense.org', 'Officer123!')}
              className="px-2 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800 shadow-xs transition"
            >
              👷 Officer
            </button>
            <button
              type="button"
              onClick={() => handleQuickDemo('citizen@civicsense.org', 'Citizen123!')}
              className="px-2 py-1.5 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-xs font-semibold text-slate-800 shadow-xs transition"
            >
              👤 Citizen
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <>
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Full Name</label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Maya Patel"
                    className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">Phone Number (Optional)</label>
                <div className="relative">
                  <Phone className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98765 43210"
                    className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
                  />
                </div>
              </div>
            </>
          )}

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@domain.com"
                className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-civic-500 focus:outline-hidden"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-civic-600 hover:bg-civic-700 text-white font-semibold rounded-lg text-sm shadow-sm transition disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-100">
          {isLogin ? "Don't have an account yet? " : "Already registered? "}
          <button
            type="button"
            onClick={() => {
              setIsLogin(!isLogin);
              setError(null);
            }}
            className="text-civic-600 font-semibold hover:underline"
          >
            {isLogin ? 'Register Citizen Account' : 'Sign in here'}
          </button>
        </div>
      </div>
    </div>
  );
};
