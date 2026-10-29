import Sticker from "../components/Stickers";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { fmtTime } from "../utils";

export default function HelpRequests() {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [tab, setTab] = useState("received");
  const [sent, setSent] = useState([]);
  const [received, setReceived] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [s, r] = await Promise.all([api.get("/help-requests/sent"), api.get("/help-requests/received")]);
      setSent(s.data);
      setReceived(r.data);
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const act = async (id, action) => {
    setBusyId(id);
    try {
      await api.patch(`/help-requests/${id}/${action}`);
      toast(action === "accept" ? "Request accepted" : "Request declined");
      await load();
    } catch (err) { toast(getErrorMessage(err), "error"); }
    finally { setBusyId(null); }
  };

  const startChat = async (id) => {
    setBusyId(id);
    try {
      const { data } = await api.post(`/conversations/from-request/${id}`);
      navigate(`/messages/${data.id}`);
    } catch (err) { toast(getErrorMessage(err), "error"); setBusyId(null); }
  };

  const list = tab === "received" ? received : sent;

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <h1>Help requests</h1>
          <p className="muted">Ask a fellow member for help, or respond to someone who asked you.</p>
        </div>
      </header>

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "received"} className={tab === "received" ? "active" : ""} onClick={() => setTab("received")}>Received ({received.length})</button>
        <button role="tab" aria-selected={tab === "sent"} className={tab === "sent" ? "active" : ""} onClick={() => setTab("sent")}>Sent ({sent.length})</button>
      </div>

      {error && <div className="error" role="alert">{error}</div>}
      {loading ? <div className="card skeleton" /> : list.length === 0 ? (
        <div className="card empty-state"><Sticker name="heart" size={84} rotate={-6} />
          <h2>{tab === "received" ? "No requests for you yet" : "You haven't asked anyone yet"}</h2>
          <p className="muted">{tab === "sent" ? "Open a community and choose \"Ask for help\" next to a member." : "When someone asks you for help, it shows up here."}</p>
        </div>
      ) : (
        <div className="stack">
          {list.map((r) => {
            const status = (r.status || "").toLowerCase();
            const other = tab === "received" ? r.sender_id : r.recipient_id;
            return (
              <article key={r.id} className="card request">
                <div className="request-top">
                  <strong>{tab === "received" ? `From user #${other}` : `To user #${other}`}</strong>
                  <span className={`status ${status}`}>{r.status}</span>
                </div>
                <p>{r.message}</p>
                <div className="muted small">Community #{r.community_id} · {fmtTime(r.created_at)}</div>
                <div className="card-actions">
                  {tab === "received" && status === "pending" && (
                    <>
                      <button className="btn" disabled={busyId === r.id} onClick={() => act(r.id, "accept")}>Accept</button>
                      <button className="btn secondary" disabled={busyId === r.id} onClick={() => act(r.id, "reject")}>Decline</button>
                    </>
                  )}
                  {status === "accepted" && (
                    <button className="btn" disabled={busyId === r.id} onClick={() => startChat(r.id)}>Open conversation</button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
      <span className="sr-only">Signed in as {user.username}</span>
    </div>
  );
}
