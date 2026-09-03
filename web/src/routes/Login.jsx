import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useI18n } from '../contexts/I18nContext';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, testCredentials } = useAuth();
  const { language, setLanguage, t, supportedLanguages } = useI18n();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showTestDrawer, setShowTestDrawer] = useState(false);

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const result = await login({ email: identifier, password });
    setLoading(false);

    if (result.success) {
      navigate('/dashboard', { replace: true });
    } else {
      setError(result.error || "Authentication failed. Please verify your government credentials.");
    }
  };

  const handleSelectTestAccount = (acc) => {
    setIdentifier(acc.email);
    setPassword('GovSecure@2026');
    setError(null);
  };

  return (
    <div style={{ minHeight: '85vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div className="card" style={{ maxWidth: '480px', width: '100%', padding: '32px' }}>
        
        {/* Language Selector Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <span style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)', fontWeight: 600 }}>
            {t('official_system', 'Official System')}
          </span>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <label style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: 500 }}>
              {t('choose_language', 'Language')}:
            </label>
            <select
              className="form-select"
              style={{ width: 'auto', height: '28px', fontSize: '11px', padding: '2px 6px' }}
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
            >
              {supportedLanguages.map(l => (
                <option key={l.code} value={l.code}>{l.native} ({l.label})</option>
              ))}
            </select>
          </div>
        </div>

        {/* Portal Branding */}
        <div style={{ marginBottom: '24px', borderBottom: '1px solid var(--border-default)', paddingBottom: '16px' }}>
          <h1 style={{ fontSize: '20px', fontWeight: 600, color: 'var(--ink-900)', margin: 0 }}>
            {t('login_portal_title', 'Secure Digital DMS Access Portal')}
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '4px' }}>
            {t('login_portal_sub', 'Official Electronic Records & Chain-of-Custody System')}
          </p>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Authoritative Credentials Form */}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">
              {t('service_id_label', 'Official Email ID or Government Service ID / Badge')}
            </label>
            <input
              type="text"
              className="form-input"
              placeholder={t('service_id_placeholder', 'e.g. officer.rao@police.gov.in or DL-POL-4921')}
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              {t('password_label', 'Password / Authentication Secret')}
            </label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '8px' }}
            disabled={loading}
          >
            {loading ? t('signin_loading', 'Verifying Authoritative Credentials...') : t('signin_btn', 'Sign In & Authorize')}
          </button>
        </form>

        {/* Authoritative Access Control Notice */}
        <div style={{ marginTop: '20px', fontSize: '11px', color: 'var(--text-tertiary)', lineHeight: '16px' }}>
          {t('auth_notice', 'Notice: Access is strictly audited. Role and permissions are authoritatively retrieved from the Government Identity Directory upon verification.')}
        </div>

        {/* Pre-Registered Official Test Credentials (Evaluation Drawer) */}
        <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid var(--border-default)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--ink-900)' }}>
              {t('test_accounts_header', 'Pre-Registered Official Test Accounts')}
            </span>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ height: '26px', fontSize: '11px', padding: '0 8px' }}
              onClick={() => setShowTestDrawer(!showTestDrawer)}
            >
              {showTestDrawer ? 'Hide Accounts' : 'Show Accounts'}
            </button>
          </div>

          {showTestDrawer && (
            <div style={{ marginTop: '12px' }}>
              <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                {t('test_accounts_sub', 'Click any official identity to auto-fill credentials and verify authoritative server-side role resolution:')}
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '220px', overflowY: 'auto' }}>
                {testCredentials.map((acc) => (
                  <div
                    key={acc.email}
                    onClick={() => handleSelectTestAccount(acc)}
                    style={{
                      padding: '8px 10px',
                      borderRadius: '4px',
                      border: '1px solid var(--border-default)',
                      background: 'var(--surface-sunken)',
                      cursor: 'pointer',
                      fontSize: '11px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                        {acc.designation}
                      </div>
                      <div style={{ color: 'var(--text-secondary)', fontSize: '10px' }}>
                        {acc.service_id} · {acc.email}
                      </div>
                    </div>
                    <span className="tag tag-neutral" style={{ fontSize: '10px' }}>
                      {acc.role_label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
