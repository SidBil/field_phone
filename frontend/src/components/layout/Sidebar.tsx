import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/ingest", label: "Import & Segment", icon: "📥" },
  { to: "/query", label: "Phonetic Query", icon: "🔍" },
  { to: "/transcribe", label: "Transcribe", icon: "✏️" },
  { to: "/audit", label: "Audit", icon: "📋" },
  { to: "/tone", label: "Tone Analysis", icon: "🎵" },
] as const;

export function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h1>FieldPhone</h1>
      </div>
      <ul className="sidebar-nav">
        {NAV_ITEMS.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <span className="sidebar-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}
