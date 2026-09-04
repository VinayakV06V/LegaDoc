import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function CaseDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('documents'); // 'documents' | 'evidence' | 'bail' | 'diary'

  const caseData = {
    id: id || 'b1a2c3d4-0001-4000-8000-000000000001',
    case_number: 'CYB-2026-482910',
    crime_type: 'Cybercrime',
    status: 'Under_Investigation',
    registered_at: '2026-09-01T10:30:00Z',
    assigned_io: 'Officer S. Rao (IO)',
    court: 'Patiala House Chief Judicial Magistrate',
    oldest_pending_item_hours: 48,
  };

  const documents = [
    { id: 'doc-001', type: 'FIR Initial Record', version: 1, hash: '8f92a11b6c73e04812f86419bd39c298', status: 'ready', chain_status: 'confirmed' },
    { id: 'doc-002', type: 'Panchnama (Seizure)', version: 1, hash: '44aa9011e8271109a1284bb192837182', status: 'ready', chain_status: 'confirmed' },
    { id: 'doc-003', type: 'Witness Statement', version: 1, hash: '77bc5512e0912781290384aa81928374', status: 'needs_review', chain_status: 'pending' }
  ];

  const evidenceRequests = [
    { id: 'REQ-2026-01', authority: 'HDFC Bank Nodal Unit', req_type: 'Transaction Statement', status: 'PENDING', requested_days_ago: 2, is_slow: true },
    { id: 'REQ-2026-02', authority: 'Airtel Telecom Nodal', req_type: 'CDR / IPDR Logs', status: 'FULFILLED', requested_days_ago: 3, is_slow: false },
  ];

  return (
    <div>
      <div className="gov-breadcrumb-bar">
        <Link to="/cases">Cases</Link>
        <span className="gov-breadcrumb-separator">›</span>
        <span>Docket {caseData.case_number}</span>
      </div>

      <div className="page-container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Case File: {caseData.case_number}</h1>
            <p className="page-desc">
              Crime Type: {caseData.crime_type} · Investigating Officer: {caseData.assigned_io} · Adjudicating Court: {caseData.court}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className="tag tag-neutral">{caseData.status}</span>
            <span className="tag tag-success">Fabric Ledger Confirmed</span>
            <Link to={`/cases/${caseData.id}/charge-sheet`} className="btn btn-primary" style={{ height: '32px', fontSize: '13px' }}>
              Prosecutor Review
            </Link>
          </div>
        </div>

        {/* Bottleneck Warning */}
        <div className="card" style={{ borderLeft: '4px solid var(--status-pending-text)', padding: '12px 16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <strong style={{ color: 'var(--status-pending-text)', fontSize: '13px' }}>
                Pending Evidence Requisition SLA Notice
              </strong>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                Requisition to <strong>HDFC Bank Nodal Unit</strong> has been open for {caseData.oldest_pending_item_hours} hours.
              </div>
            </div>
            <span className="tag tag-pending">Oldest: 48h</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="gov-tabs">
          <button
            className={`gov-tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveTab('documents')}
          >
            Evidentiary Documents ({documents.length})
          </button>
          <button
            className={`gov-tab-btn ${activeTab === 'evidence' ? 'active' : ''}`}
            onClick={() => setActiveTab('evidence')}
          >
            Evidence Requisitions ({evidenceRequests.length})
          </button>
          <button
            className={`gov-tab-btn ${activeTab === 'bail' ? 'active' : ''}`}
            onClick={() => setActiveTab('bail')}
          >
            Bail Docket
          </button>
          <button
            className={`gov-tab-btn ${activeTab === 'diary' ? 'active' : ''}`}
            onClick={() => setActiveTab('diary')}
          >
            Case Diary
          </button>
        </div>

        {/* Tab 1: Documents */}
        {activeTab === 'documents' && (
          <div className="card">
            <span className="table-caption">
              {documents.length} official documents attached to this case file.
            </span>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Doc Identifier</th>
                    <th>Classification</th>
                    <th>Version</th>
                    <th>SHA-256 Hash</th>
                    <th>Redaction Status</th>
                    <th>Ledger State</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((d) => (
                    <tr key={d.id}>
                      <td><span className="mono-text">{d.id}</span></td>
                      <td style={{ fontWeight: 500 }}>{d.type}</td>
                      <td>v{d.version}</td>
                      <td><span className="mono-text">{d.hash.slice(0, 16)}...</span></td>
                      <td>
                        <span className={`tag ${d.status === 'ready' ? 'tag-success' : 'tag-pending'}`}>
                          {d.status}
                        </span>
                      </td>
                      <td>
                        <span className={`tag ${d.chain_status === 'confirmed' ? 'tag-success' : 'tag-pending'}`}>
                          {d.chain_status}
                        </span>
                      </td>
                      <td>
                        <Link
                          to={`/cases/${caseData.id}/documents/${d.id}`}
                          className="btn btn-secondary"
                          style={{ height: '28px', fontSize: '12px', padding: '0 8px' }}
                        >
                          View Document
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 2: Evidence */}
        {activeTab === 'evidence' && (
          <div className="card">
            <span className="table-caption">
              External organization evidence requisitions dispatched under Section 91 CrPC.
            </span>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Requisition ID</th>
                    <th>Authority</th>
                    <th>Requested Material</th>
                    <th>Status</th>
                    <th>Age</th>
                  </tr>
                </thead>
                <tbody>
                  {evidenceRequests.map((er) => (
                    <tr key={er.id}>
                      <td><span className="mono-text">{er.id}</span></td>
                      <td style={{ fontWeight: 500 }}>{er.authority}</td>
                      <td>{er.req_type}</td>
                      <td>
                        <span className={`tag ${er.status === 'FULFILLED' ? 'tag-success' : 'tag-pending'}`}>
                          {er.status}
                        </span>
                      </td>
                      <td>
                        <span className={`tag ${er.is_slow ? 'tag-danger' : 'tag-neutral'}`}>
                          {er.requested_days_ago} days ago
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Bail */}
        {activeTab === 'bail' && (
          <div className="card">
            <h2 className="card-title">Bail Proceedings (Concurrent Track)</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
              Bail actions run independently of investigation status per procedural criminal law.
            </p>
            <div style={{ background: 'var(--surface-sunken)', border: '1px solid var(--border-default)', padding: '16px', borderRadius: '4px' }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-secondary)', fontWeight: 600 }}>
                Current Bail Stage
              </div>
              <div style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)', marginTop: '4px' }}>
                Hearing Scheduled
              </div>
              <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Hearing set before Patiala House Court No. 4 on 10 September 2026.
              </div>
              <div style={{ marginTop: '12px' }}>
                <Link to="/judiciary" className="btn btn-secondary" style={{ height: '32px', fontSize: '13px' }}>
                  Open Judicial Docket
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Diary */}
        {activeTab === 'diary' && (
          <div className="card">
            <h2 className="card-title">Case Diary Log (Section 172 CrPC)</h2>
            <div style={{ background: 'var(--surface-sunken)', border: '1px solid var(--border-default)', padding: '14px', borderRadius: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: 'var(--text-secondary)' }}>
                <span>Entry No. 04 · 02 September 2026, 11:30 hrs</span>
                <span className="mono-text">Officer S. Rao (IO)</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-primary)', marginTop: '8px', lineHeight: '20px' }}>
                Conducted preliminary interrogation of suspect in custody. Recorded Section 161 statements of bank officers. Forwarded digital exhibit to CFSL for forensic analysis.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
