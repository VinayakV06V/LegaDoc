import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function Judiciary() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('bail'); // 'bail' | 'trial' | 'audit'

  const [selectedCase, setSelectedCase] = useState('CYB-2026-482910');
  const [hearingDate, setHearingDate] = useState('2026-09-10T11:00');
  const [bailDecision, setBailDecision] = useState('GRANTED');
  const [bailConditions, setBailConditions] = useState('Personal bond of INR 50,000 with one local surety. Surrender passport to court registry.');
  const [actionAlert, setActionAlert] = useState(null);

  const bailApplications = [
    {
      id: 'BAIL-2026-001',
      case_number: 'CYB-2026-482910',
      accused: 'Vikram Sharma',
      sections: 'IT Act Sec 66D, IPC 420',
      filed_date: '2026-09-02',
      status: 'Hearing Scheduled',
      medical_summary: 'Hypertension reported (verified by Civil Hospital)'
    },
    {
      id: 'BAIL-2026-002',
      case_number: 'NDP-2026-119482',
      accused: 'Rahul M. Verma',
      sections: 'NDPS Act Sec 20(b)(ii)(B)',
      filed_date: '2026-09-01',
      status: 'Pending Review',
      medical_summary: 'No special medical grounds submitted'
    }
  ];

  const trialHearings = [
    {
      id: 'TR-2026-001',
      case_number: 'FIN-2026-881923',
      stage: 'Framing of Charges',
      prosecutor: 'Adv. R. S. Iyer (Public Prosecutor)',
      defense_counsel: 'Adv. M. K. Sen',
      next_hearing: '2026-09-15',
      charge_sheet_status: 'Validated Against Stage Requirements'
    }
  ];

  const handleIssueBailOrder = (e) => {
    e.preventDefault();
    setActionAlert({
      type: 'success',
      msg: `Judicial Bail Order (${bailDecision}) recorded on Hyperledger Fabric ledger for Case ${selectedCase}. Immutable timestamp attached.`
    });
  };

  const handleScheduleHearing = (e) => {
    e.preventDefault();
    setActionAlert({
      type: 'success',
      msg: `Hearing notice published for ${selectedCase} on ${hearingDate}. Summons transmitted to IO and Defense.`
    });
  };

  return (
    <div>
      <div className="gov-breadcrumb-bar">
        <span>Judiciary</span>
        <span className="gov-breadcrumb-separator">›</span>
        <span>Magistrate Bench Docket</span>
      </div>

      <div className="page-container">
        <div className="page-header">
          <div>
            <h1 className="page-title">Judicial Bench & Magistrate Portal</h1>
            <p className="page-desc">
              Bail hearings, stage requirement compliance checks, judicial charge sheet review, and unredacted evidentiary inspection.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <span className="tag tag-neutral">Role: Court / Magistrate</span>
            <span className="tag tag-success">Privilege: Unredacted Judicial Review</span>
          </div>
        </div>

        <div className="domain-notice">
          <strong>Judicial Authority Note (Flows 4 & 5):</strong> The court bench receives the complete evidentiary file
          including unredacted sensitive markers, chain-of-custody verification hashes, and full AI Parser audit logs.
        </div>

        {/* Tabs */}
        <div className="gov-tabs">
          <button
            className={`gov-tab-btn ${activeTab === 'bail' ? 'active' : ''}`}
            onClick={() => setActiveTab('bail')}
          >
            Bail Docket & Orders
          </button>
          <button
            className={`gov-tab-btn ${activeTab === 'trial' ? 'active' : ''}`}
            onClick={() => setActiveTab('trial')}
          >
            Trial Proceedings & Charge Sheets
          </button>
          <button
            className={`gov-tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
            onClick={() => setActiveTab('audit')}
          >
            Full Ledger Audit Trail
          </button>
        </div>

        {actionAlert && (
          <div className={`alert ${actionAlert.type === 'success' ? 'alert-success' : 'alert-warning'}`}>
            {actionAlert.msg}
          </div>
        )}

        {/* Tab 1: Bail */}
        {activeTab === 'bail' && (
          <div className="grid-2">
            <div className="card">
              <span className="table-caption">
                {bailApplications.length} active bail applications pending determination.
              </span>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Case Number</th>
                      <th>Accused</th>
                      <th>Sections</th>
                      <th>Status</th>
                      <th>Select</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bailApplications.map((b) => (
                      <tr key={b.id}>
                        <td><span className="mono-text">{b.case_number}</span></td>
                        <td style={{ fontWeight: 500 }}>{b.accused}</td>
                        <td style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{b.sections}</td>
                        <td><span className="tag tag-pending">{b.status}</span></td>
                        <td>
                          <button
                            className="btn btn-secondary"
                            style={{ height: '28px', fontSize: '12px', padding: '0 8px' }}
                            onClick={() => setSelectedCase(b.case_number)}
                          >
                            Select
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card">
              <h2 className="card-title">Issue Judicial Bail Order</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '16px' }}>
                Target Docket: <strong>{selectedCase}</strong>. All determinations are signed and committed to the ledger.
              </p>

              <form onSubmit={handleIssueBailOrder}>
                <div className="form-group">
                  <label className="form-label">Judicial Determination</label>
                  <select
                    className="form-select"
                    value={bailDecision}
                    onChange={(e) => setBailDecision(e.target.value)}
                  >
                    <option value="GRANTED">Bail Granted (Regular Bail)</option>
                    <option value="INTERIM">Interim Bail Pending Verification</option>
                    <option value="REJECTED">Bail Rejected (Risk of Flight / Tampering)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Bail Conditions & Directions</label>
                  <textarea
                    className="form-textarea"
                    value={bailConditions}
                    onChange={(e) => setBailConditions(e.target.value)}
                    rows={3}
                  />
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                  <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                    Pronounce Order
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={handleScheduleHearing}
                  >
                    Schedule Hearing
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Tab 2: Trial */}
        {activeTab === 'trial' && (
          <div className="card">
            <span className="table-caption">
              Trial bench hearings and Section 173 CrPC compliance reviews.
            </span>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Case Identifier</th>
                    <th>Current Trial Stage</th>
                    <th>Public Prosecutor</th>
                    <th>Defense Counsel</th>
                    <th>Next Hearing Date</th>
                    <th>Compliance Check</th>
                  </tr>
                </thead>
                <tbody>
                  {trialHearings.map((t) => (
                    <tr key={t.id}>
                      <td><span className="mono-text">{t.case_number}</span></td>
                      <td style={{ fontWeight: 500 }}>{t.stage}</td>
                      <td>{t.prosecutor}</td>
                      <td>{t.defense_counsel}</td>
                      <td>{t.next_hearing}</td>
                      <td><span className="tag tag-success">Validated</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tab 3: Full Audit */}
        {activeTab === 'audit' && (
          <div className="card">
            <span className="table-caption">
              Full unredacted audit trail verified against Hyperledger Fabric hash chain.
            </span>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Actor / Role</th>
                    <th>Action</th>
                    <th>Target Resource</th>
                    <th>Hash / Block ID</th>
                    <th>Integrity</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>2026-09-02 10:30:14</td>
                    <td>Duty Officer (Officer Kumar)</td>
                    <td><span className="mono-text">case_registered</span></td>
                    <td>CYB-2026-482910</td>
                    <td><span className="mono-text">0x8a92b41c</span></td>
                    <td><span className="tag tag-success">Chain Verified</span></td>
                  </tr>
                  <tr>
                    <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>2026-09-02 10:32:05</td>
                    <td>AI Pipeline (PaddleOCR)</td>
                    <td><span className="mono-text">redaction_auto_tagged</span></td>
                    <td>Doc-4829-Complaint</td>
                    <td><span className="mono-text">0x71e409aa</span></td>
                    <td><span className="tag tag-neutral">4 Spans Tagged</span></td>
                  </tr>
                  <tr>
                    <td style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>2026-09-02 11:15:30</td>
                    <td>Investigating Officer (IO Rao)</td>
                    <td><span className="mono-text">evidence_requested</span></td>
                    <td>HDFC Bank Nodal Request</td>
                    <td><span className="mono-text">0xfe228901</span></td>
                    <td><span className="tag tag-success">Chain Verified</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
