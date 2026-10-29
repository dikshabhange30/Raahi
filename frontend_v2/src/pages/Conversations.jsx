import Sticker from "../components/Stickers";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { fmtTime, initials } from "../utils";

export default function Conversations() {
  const { user } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/conversations/")
      .then((r) => setItems(r.data))
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <h1>Messages</h1>
          <p className="muted">Private conversations that start from an accepted help request.</p>
        </div>
      </header>
      {error && <div className="error" role="alert">{error}</div>}
      {loading ? <div className="card skeleton" /> : items.length === 0 ? (
        <div className="card empty-state"><Sticker name="speech" size={84} rotate={-6} />
          <h2>No conversations yet</h2>
          <p className="muted">Once a help request is accepted, open the conversation from Help requests.</p>
          <Link className="btn" to="/help">Go to help requests</Link>
        </div>
      ) : (
        <div className="stack">
          {items.map((c) => {
            const other = c.user_one_id === user.id ? c.user_two_id : c.user_one_id;
            return (
              <Link key={c.id} to={`/messages/${c.id}`} className="card convo-row">
                <div className="avatar">{initials(`U${other}`)}</div>
                <div>
                  <strong>Conversation with user #{other}</strong>
                  <div className="muted small">Started {fmtTime(c.created_at)}</div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
