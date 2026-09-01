import { Routes, Route, Link } from "react-router-dom";

import PoliceInvestigation from "./routes/PoliceInvestigation.jsx";
import ExternalAuthority from "./routes/ExternalAuthority.jsx";
import Judiciary from "./routes/Judiciary.jsx";
import DefenseAccused from "./routes/DefenseAccused.jsx";
import RecordsReporting from "./routes/RecordsReporting.jsx";
import PlatformAdmin from "./routes/PlatformAdmin.jsx";

// One route per domain in SYSTEM_DESIGN.md's "Domain Views" section — not one
// per role. Split further per-role only once a domain's page actually needs it.
export default function App() {
  return (
    <div>
      <nav>
        <Link to="/police">Police & Investigation</Link> |{" "}
        <Link to="/authority">External Authority</Link> |{" "}
        <Link to="/judiciary">Judiciary</Link> |{" "}
        <Link to="/defense">Defense / Accused</Link> |{" "}
        <Link to="/records">Records / NCRB</Link> |{" "}
        <Link to="/admin">Platform / Admin</Link>
      </nav>
      <Routes>
        <Route path="/police" element={<PoliceInvestigation />} />
        <Route path="/authority" element={<ExternalAuthority />} />
        <Route path="/judiciary" element={<Judiciary />} />
        <Route path="/defense" element={<DefenseAccused />} />
        <Route path="/records" element={<RecordsReporting />} />
        <Route path="/admin" element={<PlatformAdmin />} />
        <Route path="/" element={<PoliceInvestigation />} />
      </Routes>
    </div>
  );
}
