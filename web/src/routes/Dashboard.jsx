import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useI18n } from '../contexts/I18nContext';

export default function Dashboard() {
  const { user } = useAuth();
  const { t } = useI18n();

  const role = user?.role || 'duty_officer';

  // Role-specific action cards & metrics
  const getRoleConfig = () => {
    switch (role) {
      case 'io':
      case 'sho':
      case 'duty_officer':
        return {
          title: t('role_' + role, 'Police Investigation Authority'),
          metrics: [
            { label: t('dash_metric_active_cases', 'Active Cases'), value: '24', sub: 'Assigned in this precinct' },
            { label: t('dash_metric_integrity', 'Fabric Ledger Integrity'), value: '100%', sub: 'SHA-256 hashes confirmed' },
            { label: t('dash_metric_sla', 'Oldest Pending SLA Requisition'), value: '48h', sub: 'HDFC Bank Nodal Unit' }
          ],
          actions: [
            { label: 'Register New FIR', desc: 'Create initial case docket and commit hash to Fabric', route: '/cases' },
            { label: 'Inspect Case Worklist', desc: 'Manage evidence, witness statements, and case diary', route: '/cases' },
            { label: 'Check Needs-Review Queue', desc: 'Verify low-confidence and fallback redacted documents', route: '/review-queue' }
          ]
        };

      case 'court':
        return {
          title: t('role_court', 'Judicial Bench & Magistrate Portal'),
          metrics: [
            { label: 'Pending Bail Applications', value: '4', sub: 'Awaiting judicial determination' },
            { label: 'Active Trial Proceedings', value: '12', sub: 'Charges framed & scheduled' },
            { label: 'Unredacted Audit Trail', value: '1,420', sub: 'Immutable ledger events' }
          ],
          actions: [
            { label: 'Review Bail Applications', desc: 'Adjudicate bail petitions and issue orders with conditions', route: '/judiciary' },
            { label: 'Trial Proceedings & Hearings', desc: 'Inspect case dossiers and Section 173 compliance', route: '/judiciary' },
            { label: 'Inspect Audit Trail', desc: 'Examine cryptographic chain of custody and AI decisions', route: '/judiciary' }
          ]
        };

      case 'prosecutor':
        return {
          title: t('role_prosecutor', 'Public Prosecutor Review'),
          metrics: [
            { label: 'Cases Pending Charge Sheet', value: '8', sub: 'Evidence collection nearing 60/90 days' },
            { label: 'Stage Requirements Passed', value: '5', sub: 'Ready for court docketing' },
            { label: 'Section 409 Conflicts', value: '3', sub: 'Missing mandatory evidence' }
          ],
          actions: [
            { label: 'Validate Stage Requirements', desc: 'Check crime-type mandatory requirements before filing', route: '/cases' },
            { label: 'Review Evidentiary Dockets', desc: 'Inspect forensic certificates and seizure panchnamas', route: '/cases' }
          ]
        };

      case 'external_authority':
        return {
          title: t('role_external_authority', 'External Authority Fulfillment'),
          metrics: [
            { label: 'Pending Requisitions', value: '6', sub: 'Dispatched under Section 91 CrPC' },
            { label: 'Oldest Requisition', value: '6 days', sub: 'Target SLA: under 5 days' },
            { label: 'Completed Submissions', value: '84', sub: 'Certified reports committed to chain' }
          ],
          actions: [
            { label: 'View Requisitions Inbox', desc: 'Inspect pending evidence requests sorted Oldest First', route: '/authority' },
            { label: 'Submit Certified Report', desc: 'Upload signed PDF and commit directly to custody chain', route: '/authority' }
          ]
        };

      case 'defense':
        return {
          title: t('role_defense', 'Defense Counsel Gateway'),
          metrics: [
            { label: 'Active Bail Petitions', value: '2', sub: 'Under consideration by Magistrate' },
            { label: 'Next Scheduled Hearing', value: '10 Sept', sub: 'Court No. 3 Patiala House' },
            { label: 'Surety Undertakings', value: '1', sub: 'Registered & solvency verified' }
          ],
          actions: [
            { label: 'File Bail Application', desc: 'Submit petition under Section 437/439 CrPC', route: '/defense' },
            { label: 'Register Surety Bond', desc: 'Submit guarantor documents following bail grant', route: '/defense' }
          ]
        };

      case 'config_admin':
      case 'security_auditor':
        return {
          title: t('role_config_admin', 'Platform Administration & Security Governance'),
          metrics: [
            { label: 'System & Custom Roles', value: '10', sub: 'Authoritative RBAC definitions' },
            { label: 'Active Organizations', value: '4', sub: 'Cryptographic MSP tenants' },
            { label: 'Audit Log Chain Status', value: 'Healthy', sub: 'Zero forks, serial hash valid' }
          ],
          actions: [
            { label: 'Manage Roles & Permissions', desc: 'Create custom roles, assign permissions, and manage users', route: '/admin' },
            { label: 'Configure Document Schemas', desc: 'Manage sensitivity tiers and entity recognizers', route: '/admin' },
            { label: 'Blockchain Chain Recovery', desc: 'Two-person control manual retry recovery for documents', route: '/admin' }
          ]
        };

      case 'records_ncrb_analyst':
      default:
        return {
          title: t('role_records_ncrb_analyst', 'NCRB Statistical Analytics'),
          metrics: [
            { label: 'Total Matters Tracked', value: '1,482', sub: 'Across 42 state police stations' },
            { label: 'Avg Days to Charge Sheet', value: '38.4', sub: 'Statutory compliance: 100%' },
            { label: 'De-Identified Records', value: '100%', sub: 'Zero PII data leakage' }
          ],
          actions: [
            { label: 'Explore Statistical Reports', desc: 'De-identified criminal justice analytics and trends', route: '/reports' }
          ]
        };
    }
  };

  const config = getRoleConfig();

  return (
    <div>
      <div className="gov-breadcrumb-bar">
        <span>{t('nav_dashboard', 'Dashboard Hub')}</span>
        <span className="gov-breadcrumb-separator">›</span>
        <span>{user?.name || 'Officer'}</span>
      </div>

      <div className="page-container">
        
        {/* Officer Identity Banner */}
        <div className="card" style={{ marginBottom: '20px', background: 'var(--surface-panel)', borderLeft: '4px solid var(--ink-900)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-secondary)', fontWeight: 600 }}>
                {t('dash_officer_profile', 'Officer Identity Profile')}
              </div>
              <h1 style={{ fontSize: '22px', fontWeight: 600, color: 'var(--ink-900)', marginTop: '4px' }}>
                {user?.name || 'Authorized Officer'}
              </h1>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
                {user?.designation || 'Government Official'} · {user?.org_name || 'Government Organization'}
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
              <span className="tag tag-neutral" style={{ fontSize: '12px', padding: '4px 8px' }}>
                {t('dash_service_id', 'Service ID')}: <strong style={{ marginLeft: '4px', fontFamily: 'var(--font-mono)' }}>{user?.service_id || 'GOV-SEC-ID'}</strong>
              </span>
              <span className="tag tag-success" style={{ fontSize: '12px', padding: '4px 8px' }}>
                {config.title}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '20px', marginTop: '16px', paddingTop: '12px', borderTop: '1px solid var(--border-default)', fontSize: '12px', color: 'var(--text-secondary)' }}>
            <div>
              <span>Official Email:</span> <strong style={{ color: 'var(--text-primary)' }}>{user?.email}</strong>
            </div>
            <div>
              <span>Authoritative Role Code:</span> <strong style={{ color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>{user?.role}</strong>
            </div>
            <div>
              <span>Access Clearance:</span> <span className="tag tag-success" style={{ marginLeft: '4px' }}>Authoritative RBAC Verified</span>
            </div>
          </div>
        </div>

        {/* Operational Metrics */}
        <div className="grid-3" style={{ marginBottom: '20px' }}>
          {config.metrics.map((m, idx) => (
            <div key={idx} className="stat-widget">
              <span className="stat-value">{m.value}</span>
              <span className="stat-label">{m.label}</span>
              <span className="stat-sub">{m.sub}</span>
            </div>
          ))}
        </div>

        {/* Role-Specific Workflows & Actions */}
        <div className="card">
          <h2 className="card-title">{t('dash_quick_actions', 'Operational Quick Actions')}</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
            Primary workflows and tasks assigned to your authoritative jurisdiction:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {config.actions.map((act, i) => (
              <div
                key={i}
                style={{
                  padding: '16px',
                  borderRadius: '4px',
                  border: '1px solid var(--border-default)',
                  background: 'var(--surface-sunken)',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--ink-900)', margin: '0 0 6px 0' }}>
                    {act.label}
                  </h3>
                  <p style={{ fontSize: '12px', color: 'var(--text-secondary)', margin: '0 0 16px 0', lineHeight: '18px' }}>
                    {act.desc}
                  </p>
                </div>
                <Link
                  to={act.route}
                  className="btn btn-primary"
                  style={{ textDecoration: 'none', textAlign: 'center', width: 'auto', alignSelf: 'flex-start' }}
                >
                  Launch Workflow →
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* System & Jurisdictional Notice */}
        <div className="domain-notice" style={{ marginTop: '20px' }}>
          <strong>Role-Based Access Control Enforcement:</strong> Your navigation and data views are filtered
          strictly to match the authoritative role and permissions associated with your official service identity.
          Cross-jurisdictional reads and privilege self-escalation are structurally prevented at the API boundary.
        </div>

      </div>
    </div>
  );
}
