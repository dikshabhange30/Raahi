import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Logo from "../components/Logo";
import { initials } from "../utils";

const links = [
  { to: "/communities", label: "Communities", icon: "🏘️" },
  { to: "/help", label: "Help requests", icon: "🤝" },
  { to: "/messages", label: "Messages", icon: "💬" },
  { to: "/safety", label: "Safety", icon: "🛡️" },
  { to: "/profile", label: "Profile", icon: "👤" },
];

export default function AppLayout() {
  const { user, isAdmin, signOut } = useAuth();
  const name = user.full_name || user.username;
  // The Admin link is added ONLY when the backend confirmed admin rights.
  const items = isAdmin ? [...links, { to: "/admin", label: "Admin", icon: "⚙️" }] : links;

  return (
    <div className="shell">
      <aside className="sidebar">
        <Logo to="/communities" light />
        <nav aria-label="Main">
          {items.map((l) => (
            <NavLink key={l.to} to={l.to} className="nav-link">
              <span aria-hidden="true">{l.icon}</span>
              <span>{l.label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="me">
          <div className="avatar">{initials(name)}</div>
          <div className="me-info">
            <strong>{name}</strong>
            <button className="link-btn" onClick={signOut}>Log out</button>
          </div>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
