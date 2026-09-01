// Domains 2-4 — Forensic (FSL/Digital FSL), Medical (Hospital), and
// Financial/Verification (Bank, Telecom, RTO). Shared shape: view routed
// evidence requests, submit a report/document against one. See
// SYSTEM_DESIGN.md — access must be scoped to the specific request routed to
// this org, never the rest of the case file.
//
// TODO: evidence-request inbox, submit-and-attach-document form.
export default function ExternalAuthority() {
  return (
    <div>
      <h1>External Authority</h1>
      <p>Not implemented yet — see SYSTEM_DESIGN.md, Domains 2-4.</p>
    </div>
  );
}
