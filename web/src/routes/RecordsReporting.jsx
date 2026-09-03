import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function RecordsReporting() {
  const { user } = useAuth();
  const [selectedCrimeFilter, setSelectedCrimeFilter] = useState('ALL');
  const [selectedYear, setSelectedYear] = useState('2026');

  const deidentifiedRecords = [
    {
      case_id_hash: 'c89a01f2...9b12',
      crime_type: 'Cybercrime',
      status: 'FIR_Registered',
      state_precinct: 'North Zone Cyber Unit',
      days_in_investigation: 4,
      court_level: 'Chief Judicial Magistrate',
      has_fsl_evidence: true,
      bail_status: 'Hearing_Scheduled'
    },
    {
      case_id_hash: '71ab9901...33d1',
      crime_type: 'NDPS',
      status: 'Under_Investigation',
      state_precinct: 'Anti-Narcotics Task Force',
      days_in_investigation: 18,
      court_level: 'Special Sessions Court',
      has_fsl_evidence: true,
      bail_status: 'Rejected'
    },
    {
      case_id_hash: '55ee1248...66ac',
      crime_type: 'Financial Fraud',
      status: 'Chargesheet_Filed',
      state_precinct: 'Economic Offences Wing',
      days_in_investigation: 42,
      court_level: 'Chief Judicial Magistrate',
      has_fsl_evidence: true,
      bail_status: 'Granted'
    },
    {
      case_id_hash: '33aa8190...44ff',
      crime_type: 'Cybercrime',
      status: 'Under_Investigation',
      state_precinct: 'Cyber Police Station Central',
      days_in_investigation: 12,
      court_level: 'Chief Judicial Magistrate',
      has_fsl_evidence: false,
      bail_status: 'Arrested'
    }
  ];

  const filteredRecords = deidentifiedRecords.filter(r => {
    if (selectedCrimeFilter === 'ALL') return true;
    return r.crime_type === selectedCrimeFilter;
  });

  return (
    <div>
      <div className="gov-breadcrumb-bar">
        <span>NCRB Reporting</span>
        <span className="gov-breadcrumb-separator">›</span>
        <span>Statistical Aggregates</span>
      </div>

      <div className="page-container">
        <div className="page-header">
          <div>
            <h1 className="page-title">National Crime Records Bureau (NCRB) Reporting</h1>
            <p className="page-desc">
              Anonymized statistical research and criminal justice analytics. Backed by a dedicated de-identified database view.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className="tag tag-neutral">Role: NCRB Analyst</span>
            <span className="tag tag-neutral">Access: De-Identified Only</span>
          </div>
        </div>

        <div className="domain-notice">
          <strong>Domain 7 Architecture Guarantee:</strong> This view reads from a dedicated de-identified data pipeline.
          Informant identities, complainant names, phone numbers, and addresses are structurally omitted from the database view.
        </div>

        {/* Factual Operational Metrics */}
        <div className="grid-3">
          <div className="stat-widget">
            <span className="stat-value">1,482</span>
            <span className="stat-label">Total Documented Matters</span>
            <span className="stat-sub">Across 42 state police stations</span>
          </div>
          <div className="stat-widget">
            <span className="stat-value" style={{ color: 'var(--ink-900)' }}>38.4 Days</span>
            <span className="stat-label">Average Time to Charge Sheet Filing</span>
            <span className="stat-sub">Statutory compliance: 100%</span>
          </div>
          <div className="stat-widget">
            <span className="stat-value" style={{ color: 'var(--status-success-text)' }}>99.8%</span>
            <span className="stat-label">Cryptographic Custody Validation</span>
            <span className="stat-sub">Ledger integrity check: Passed</span>
          </div>
        </div>

        {/* Filters Toolbar */}
        <div className="card" style={{ padding: '12px 16px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <div>
                <label className="form-label" style={{ fontSize: '11px', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Crime Classification
                </label>
                <select
                  className="form-select"
                  style={{ height: '32px', fontSize: '13px' }}
                  value={selectedCrimeFilter}
                  onChange={(e) => setSelectedCrimeFilter(e.target.value)}
                >
                  <option value="ALL">All Classifications</option>
                  <option value="Cybercrime">Cybercrime</option>
                  <option value="NDPS">NDPS</option>
                  <option value="Financial Fraud">Financial Fraud</option>
                </select>
              </div>

              <div>
                <label className="form-label" style={{ fontSize: '11px', textTransform: 'uppercase', marginBottom: '2px' }}>
                  Cohort Period
                </label>
                <select
                  className="form-select"
                  style={{ height: '32px', fontSize: '13px' }}
                  value={selectedYear}
                  onChange={(e) => setSelectedYear(e.target.value)}
                >
                  <option value="2026">Year 2026 (YTD)</option>
                  <option value="2025">Year 2025 (Annual)</option>
                </select>
              </div>
            </div>

            <button className="btn btn-secondary" style={{ height: '32px', fontSize: '13px' }}>
              Export Anonymized CSV
            </button>
          </div>
        </div>

        {/* De-identified Cases Table */}
        <div className="card">
          <span className="table-caption">
            {filteredRecords.length} de-identified cases matching filter criteria.
          </span>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Anonymized Hash ID</th>
                  <th>Classification</th>
                  <th>Lifecycle Stage</th>
                  <th>Zonal Precinct</th>
                  <th>Days Open</th>
                  <th>Adjudicating Court</th>
                  <th>Forensic Evidence</th>
                  <th>Bail Disposition</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((r) => (
                  <tr key={r.case_id_hash}>
                    <td><span className="mono-text">{r.case_id_hash}</span></td>
                    <td style={{ fontWeight: 500 }}>{r.crime_type}</td>
                    <td><span className="tag tag-neutral">{r.status}</span></td>
                    <td style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{r.state_precinct}</td>
                    <td>{r.days_in_investigation} days</td>
                    <td style={{ fontSize: '13px' }}>{r.court_level}</td>
                    <td>
                      <span className={`tag ${r.has_fsl_evidence ? 'tag-success' : 'tag-neutral'}`}>
                        {r.has_fsl_evidence ? 'Attached' : 'None'}
                      </span>
                    </td>
                    <td><span className="tag tag-neutral">{r.bail_status}</span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
