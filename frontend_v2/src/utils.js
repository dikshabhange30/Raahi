export function initials(name = "?") {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase())
    .join("") || "?";
}

export function fmtTime(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return "";
  return d.toLocaleString([], {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Members endpoint returns users (or memberships). Normalise either shape.
export function normaliseMember(m) {
  const u = m.user || m;
  const id = m.user_id ?? u.id;
  const name = u.full_name || u.username || `User #${id}`;
  return { id, name, username: u.username, city: u.city, profession: u.profession };
}
