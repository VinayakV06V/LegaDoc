// Domain 6 — Defense / Accused. Submission-only, nothing else. This is the
// domain with the least access and the most consequence if RBAC is loose —
// see SYSTEM_DESIGN.md, Domain 6. Do not add a read view here beyond the
// user's own bail submissions without re-reading that section first.
//
// TODO: bail application form, surety bond form.
export default function DefenseAccused() {
  return (
    <div>
      <h1>Defense / Accused</h1>
      <p>Not implemented yet — see SYSTEM_DESIGN.md, Domain 6.</p>
    </div>
  );
}
