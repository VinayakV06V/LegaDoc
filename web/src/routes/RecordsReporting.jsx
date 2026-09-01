// Domain 7 — Records / NCRB Reporting. Read-only, de-identified metadata
// only, via GET /reports/case-metadata. See SYSTEM_DESIGN.md, Domain 7.
//
// TODO: case-metadata table/chart view. Do not wire this page to /cases or
// /documents endpoints even "just for a quick filter" — that defeats the
// whole point of this role having its own dedicated view.
export default function RecordsReporting() {
  return (
    <div>
      <h1>Records / NCRB Reporting</h1>
      <p>Not implemented yet — see SYSTEM_DESIGN.md, Domain 7.</p>
    </div>
  );
}
