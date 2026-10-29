import Sticker from "../components/Stickers";
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import MessageThread from "../components/MessageThread";
import Modal from "../components/Modal";
import { initials, normaliseMember } from "../utils";

export default function CommunityChat() {
  const { id } = useParams();
  const communityId = Number(id);
  const { user } = useAuth();
  const toast = useToast();

  const [community, setCommunity] = useState(null);
  const [messages, setMessages] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [denied, setDenied] = useState(false);
  const [error, setError] = useState("");
  const [helpFor, setHelpFor] = useState(null);
  const [reportFor, setReportFor] = useState(null);

  const loadMessages = useCallback(async () => {
    const { data } = await api.get(`/communities/${communityId}/messages`);
    setMessages([...data].sort((a, b) => a.id - b.id));
  }, [communityId]);

  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const mine = await api.get("/communities/mine");
        const found = mine.data.find((c) => c.id === communityId);
        if (!found) { setDenied(true); return; }
        if (alive) setCommunity(found);
        const [, mem] = await Promise.all([loadMessages(), api.get(`/communities/${communityId}/members`)]);
        if (alive) setMembers(Array.isArray(mem.data) ? mem.data.map(normaliseMember) : []);
      } catch (err) {
        if (err.response?.status === 403) setDenied(true);
        else setError(getErrorMessage(err));
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, [communityId, loadMessages]);

  // Messages are fetched again every 10 seconds (polling, not real-time).
  useEffect(() => {
    if (denied || loading) return;
    const t = setInterval(() => loadMessages().catch(() => {}), 10000);
    return () => clearInterval(t);
  }, [denied, loading, loadMessages]);

  const send = async (content) => {
    try {
      const { data } = await api.post(`/communities/${communityId}/messages`, { content });
      setMessages((m) => [...m, data]);
    } catch (err) {
      toast(getErrorMessage(err), "error");
      throw err;
    }
  };

  const block = async (m) => {
    if (!window.confirm(`Block ${m.name}?`)) return;
    try {
      await api.post(`/safety/block/${m.id}`);
      toast(`Blocked ${m.name}`);
    } catch (err) { toast(getErrorMessage(err), "error"); }
  };

  if (loading) return <div className="page"><div className="card skeleton tall" /></div>;
  if (denied) {
    return (
      <div className="page">
        <div className="card empty-state"><Sticker name="speech" size={84} rotate={-6} />
          <h2>Members only</h2>
          <p className="muted">Join this community to read and send messages.</p>
          <Link className="btn" to="/communities">Back to communities</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <Link to="/communities" className="back">← Communities</Link>
          <h1>{community?.name}</h1>
          <div className="chips">
            <span className="chip">{community?.city}</span>
            <span className="chip">{community?.language}</span>
          </div>
        </div>
        <button className="btn secondary" onClick={() => loadMessages().catch((e) => toast(getErrorMessage(e), "error"))}>Refresh</button>
      </header>
      {error && <div className="error" role="alert">{error}</div>}

      <div className="chat-layout">
        <MessageThread messages={messages} meId={user.id} onSend={send} emptyText="No messages yet. Start the conversation." />

        <aside className="card members">
          <h2>Members ({members.length})</h2>
          <ul>
            {members.map((m) => (
              <li key={m.id}>
                <div className="avatar sm">{initials(m.name)}</div>
                <div className="member-info">
                  <strong>{m.name}{m.id === user.id && " (you)"}</strong>
                  {m.id !== user.id && (
                    <div className="member-actions">
                      <button className="link-btn" onClick={() => setHelpFor(m)}>Ask for help</button>
                      <button className="link-btn" onClick={() => setReportFor(m)}>Report</button>
                      <button className="link-btn danger-text" onClick={() => block(m)}>Block</button>
                    </div>
                  )}
                </div>
              </li>
            ))}
            {members.length === 0 && <li className="muted">No members to show.</li>}
          </ul>
        </aside>
      </div>

      {helpFor && <HelpModal member={helpFor} communityId={communityId} onClose={() => setHelpFor(null)} />}
      {reportFor && <ReportModal member={reportFor} communityId={communityId} onClose={() => setReportFor(null)} />}
    </div>
  );
}

function HelpModal({ member, communityId, onClose }) {
  const toast = useToast();
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/help-requests/", { recipient_id: member.id, community_id: communityId, message: message.trim() });
      toast("Help request sent");
      onClose();
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setBusy(false); }
  };

  return (
    <Modal title={`Ask ${member.name} for help`} onClose={onClose}>
      <form onSubmit={submit}>
        <label htmlFor="help-msg">What do you need help with?</label>
        <textarea id="help-msg" rows={4} maxLength={1000} value={message} onChange={(e) => setMessage(e.target.value)} required />
        {error && <div className="error" role="alert">{error}</div>}
        <div className="modal-actions">
          <button type="button" className="btn secondary" onClick={onClose}>Cancel</button>
          <button className="btn" disabled={busy || !message.trim()}>{busy ? "Sending…" : "Send request"}</button>
        </div>
      </form>
    </Modal>
  );
}

export function ReportModal({ member, communityId, onClose }) {
  const toast = useToast();
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await api.post("/safety/reports", { reported_user_id: member.id, community_id: communityId ?? null, reason: reason.trim() });
      toast("Report submitted. Thank you.");
      onClose();
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setBusy(false); }
  };

  return (
    <Modal title={`Report ${member.name}`} onClose={onClose}>
      <form onSubmit={submit}>
        <label htmlFor="report-reason">What happened? (at least 5 characters)</label>
        <textarea id="report-reason" rows={4} minLength={5} maxLength={1000} value={reason} onChange={(e) => setReason(e.target.value)} required />
        {error && <div className="error" role="alert">{error}</div>}
        <div className="modal-actions">
          <button type="button" className="btn secondary" onClick={onClose}>Cancel</button>
          <button className="btn danger" disabled={busy || reason.trim().length < 5}>{busy ? "Sending…" : "Submit report"}</button>
        </div>
      </form>
    </Modal>
  );
}
