import { Routes, Route, NavLink, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext.jsx";
import { I18nProvider, useI18n } from "./contexts/I18nContext.jsx";
import StatusBanner from "./components/StatusBanner.jsx";
import Login from "./routes/Login.jsx";
import Dashboard from "./routes/Dashboard.jsx";

import PoliceInvestigation from "./routes/PoliceInvestigation.jsx";
import CaseDetail from "./routes/CaseDetail.jsx";
import DocumentViewer from "./routes/DocumentViewer.jsx";
import ChargeSheetFiling from "./routes/ChargeSheetFiling.jsx";
import NeedsReviewQueue from "./routes/NeedsReviewQueue.jsx";
import ExternalAuthority from "./routes/ExternalAuthority.jsx";
import Judiciary from "./routes/Judiciary.jsx";
import DefenseAccused from "./routes/DefenseAccused.jsx";
import RecordsReporting from "./routes/RecordsReporting.jsx";
import PlatformAdmin from "./routes/PlatformAdmin.jsx";

function PrivateRoute({ children, allowedRoles }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const role = user.role?.toLowerCase();
    const isAllowed = allowedRoles.some(r => r.toLowerCase() === role);
    if (!isAllowed) {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
}

function AppNavigation() {
  const { user, logout } = useAuth();
  const { language, setLanguage, t, supportedLanguages } = useI18n();
  const location = useLocation();

  if (!user && location.pathname === "/login") {
    return null;
  }

  const role = user?.role?.toLowerCase() || '';

  // Role-scoped navigation definition per Requirement 5
  const isPolice = ['duty_officer', 'io', 'sho', 'police', 'cyber_cell', 'narcotics_police'].includes(role);
  const isCourt = role === 'court';
  const isProsecutor = role === 'prosecutor';
  const isAuthority = role === 'external_authority';
  const isDefense = role === 'defense';
  const isAdmin = ['config_admin', 'security_auditor', 'admin'].includes(role);
  const isNCRB = role === 'records_ncrb_analyst';

  return (
    <>
      <header className="gov-masthead">
        <div className="gov-masthead-left">
          <span className="gov-emblem-badge">[{t('official_system', 'Official System')}]</span>
          <div>
            <div className="gov-system-title">{t('gov_title', 'Government of India · Secure Digital DMS')}</div>
            <span className="gov-system-subtitle">{t('gov_subtitle', 'SIH26190 · Hyperledger Fabric Cryptographic Ledger')}</span>
          </div>
        </div>

        <div className="gov-masthead-right">
          {/* Language Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginRight: '8px' }}>
            <label style={{ fontSize: '11px', color: 'rgba(255,255,255,0.85)', fontWeight: 500 }}>
              {t('choose_language', 'Language')}:
            </label>
            <select
              className="form-select"
              style={{
                width: 'auto',
                height: '28px',
                fontSize: '11px',
                padding: '2px 8px',
                background: 'rgba(255,255,255,0.12)',
                color: '#ffffff',
                border: '1px solid rgba(255,255,255,0.3)',
                borderRadius: '4px'
              }}
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {supportedLanguages.map(l => (
                <option key={l.code} value={l.code} style={{ background: '#0B2547', color: '#ffffff' }}>
                  {l.native} ({l.label})
                </option>
              ))}
            </select>
          </div>

          {user ? (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', marginRight: '4px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#ffffff' }}>
                  {user.name || user.email}
                </span>
                <span style={{ fontSize: '10px', color: 'rgba(255,255,255,0.75)', fontFamily: 'var(--font-mono)' }}>
                  {user.service_id || user.role?.toUpperCase()}
                </span>
              </div>
              <button className="gov-logout-btn" onClick={logout} title="Clear session and sign out">
                {t('sign_out', 'Sign Out')}
              </button>
            </>
          ) : (
            <NavLink to="/login" className="gov-logout-btn" style={{ textDecoration: 'none' }}>
              {t('sign_in', 'Sign In')}
            </NavLink>
          )}
        </div>
      </header>

      {user && (
        <nav className="gov-nav-band">
          <NavLink to="/dashboard" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
            {t('nav_dashboard', 'Dashboard Hub')}
          </NavLink>

          {/* Police Navigation */}
          {(isPolice || isAdmin) && (
            <>
              <NavLink to="/cases" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
                {t('nav_cases', 'Investigation & Cases')}
              </NavLink>
              <NavLink to="/review-queue" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
                {t('nav_review_queue', 'Needs-Review Queue')}
              </NavLink>
            </>
          )}

          {/* Prosecution Navigation */}
          {isProsecutor && (
            <NavLink to="/cases" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
              {t('nav_cases', 'Prosecutor Case Review')}
            </NavLink>
          )}

          {/* Judicial Bench Navigation */}
          {(isCourt || isAdmin || isProsecutor) && (
            <NavLink to="/judiciary" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
              {t('nav_judiciary', 'Judicial Bench')}
            </NavLink>
          )}

          {/* External Authority Navigation */}
          {(isAuthority || isAdmin) && (
            <NavLink to="/authority" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
              {t('nav_authority', 'External Authorities')}
            </NavLink>
          )}

          {/* Defense Navigation */}
          {(isDefense || isAdmin) && (
            <NavLink to="/defense" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
              {t('nav_defense', 'Defense Submissions')}
            </NavLink>
          )}

          {/* NCRB Reporting */}
          {(isNCRB || isAdmin) && (
            <NavLink to="/reports" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
              {t('nav_reports', 'NCRB Statistical Reports')}
            </NavLink>
          )}

          {/* Administration Navigation */}
          {isAdmin && (
            <NavLink to="/admin" className={({ isActive }) => "gov-nav-item" + (isActive ? " active" : "")}>
              {t('nav_admin', 'Platform Administration')}
            </NavLink>
          )}
        </nav>
      )}
    </>
  );
}

function AppFooter() {
  const { t } = useI18n();
  return (
    <footer className="gov-footer">
      <div className="gov-footer-content">
        <span>{t('gov_footer_org', 'GOVERNMENT OF INDIA · NATIONAL INFORMATICS CENTRE / MHA')}</span>
        <span className="gov-footer-note">{t('gov_footer_note', 'FOR OFFICIAL USE ONLY · SIH26190 SECURE DIGITAL DMS')}</span>
      </div>
    </footer>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <div className="app-layout">
          <StatusBanner />
          <AppNavigation />
          <main style={{ flex: 1 }}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />

              {/* Police Routes */}
              <Route path="/cases" element={
                <PrivateRoute allowedRoles={['duty_officer', 'io', 'sho', 'police', 'prosecutor', 'config_admin', 'security_auditor']}>
                  <PoliceInvestigation />
                </PrivateRoute>
              } />
              <Route path="/police" element={<Navigate to="/cases" replace />} />
              <Route path="/cases/:id" element={<PrivateRoute><CaseDetail /></PrivateRoute>} />
              <Route path="/cases/:id/documents/:docId" element={<PrivateRoute><DocumentViewer /></PrivateRoute>} />
              <Route path="/cases/:id/charge-sheet" element={<PrivateRoute><ChargeSheetFiling /></PrivateRoute>} />
              <Route path="/review-queue" element={
                <PrivateRoute allowedRoles={['duty_officer', 'io', 'sho', 'config_admin', 'security_auditor']}>
                  <NeedsReviewQueue />
                </PrivateRoute>
              } />

              {/* External Authority */}
              <Route path="/authority" element={
                <PrivateRoute allowedRoles={['external_authority', 'config_admin', 'security_auditor']}>
                  <ExternalAuthority />
                </PrivateRoute>
              } />

              {/* Judiciary */}
              <Route path="/judiciary" element={
                <PrivateRoute allowedRoles={['court', 'prosecutor', 'config_admin', 'security_auditor']}>
                  <Judiciary />
                </PrivateRoute>
              } />

              {/* Defense */}
              <Route path="/defense" element={
                <PrivateRoute allowedRoles={['defense', 'config_admin']}>
                  <DefenseAccused />
                </PrivateRoute>
              } />

              {/* NCRB Reporting */}
              <Route path="/reports" element={
                <PrivateRoute allowedRoles={['records_ncrb_analyst', 'config_admin', 'security_auditor']}>
                  <RecordsReporting />
                </PrivateRoute>
              } />
              <Route path="/records" element={<Navigate to="/reports" replace />} />

              {/* Platform Administration */}
              <Route path="/admin" element={
                <PrivateRoute allowedRoles={['config_admin', 'security_auditor']}>
                  <PlatformAdmin />
                </PrivateRoute>
              } />

              {/* Default Redirect to Dashboard */}
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </main>
          <AppFooter />
        </div>
      </AuthProvider>
    </I18nProvider>
  );
}
