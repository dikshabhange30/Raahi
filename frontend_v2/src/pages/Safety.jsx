import { useCallback, useEffect, useState } from "react";
import api, { getErrorMessage } from "../services/api";
import { useToast } from "../context/ToastContext";

// The blocked-list response format isn't documented, so accept ids or objects.
function toBlockedId(item) {
  if (typeof item === "number") return item;
  return item.blocked_user_id ?? item.blocked_id ?? item.user_id ?? item.id;
}

export default function Safety() {
  const toast = useToast();
  const [blocked, setBlocked] = useState([]);
  const [loading, setLoading] = useState(true);
  const [blockId, setBlockId] = useState("");
  const [report, setReport] = useState({ reported_user_id: "", community_id: "", reason: "" });
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const { data } = await api.get("/safety/blocked");
      const arr = Array.isArray(data) ? data : data?.blocked || data?.users || [];
      setBlocked(arr.map((x) => ({ id: toBlockedId(x), raw: x })));
    } catch (err) { toast(getErrorMessage(err), "error"); }
    finally { setLoading(false); }
  }, [toast]);

  useEffect(() => { load(); }, [load]);

  const block = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post(`/safety/block/${Number(blockId)}`);
      toast("User blocked");
      setBlockId("");
      await load();
    } catch (err) { toast(getErrorMessage(err), "error"); }
    finally { setBusy(false); }
  };

  const unblock = async (id) => {
    try {
      await api.delete(`/safety/block/${id}`);
      toast("User unblocked");
      await load();
    } catch (err) { toast(getErrorMessage(err), "error"); }
  };

  const submitReport = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post("/safety/reports", {
        reported_user_id: Number(report.reported_user_id),
        community_id: report.community_id ? Number(report.community_id) : null,
        reason: report.reason.trim(),
      });
      toast("Report submitted. Thank you.");
      setReport({ reported_user_id: "", community_id: "", reason: "" });
    } catch (err) { toast(getErrorMessage(err), "error"); }
    finally { setBusy(false); }
  };

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <h1>Safety</h1>
          <p className="muted">Block people you don't want to hear from, or report behaviour to our moderators.</p>
        </div>
      </header>

      <div className="two-col">
        <section className="card">
          <h2>Blocked people</h2>
          <form className="inline-form" onSubmit={block}>
            <label htmlFor="block-id" className="sr-only">User ID to block</label>
            <input id="block-id" type="number" min="1" placeholder="User ID" value={blockId} onChange={(e) => setBlockId(e.target.value)} required />
            <button className="btn" disabled={busy}>Block</button>
          </form>
          <p className="muted small">You can also block from a member list inside a community.</p>
          {loading ? <div className="skeleton" /> : blocked.length === 0 ? (
            <p className="empty">You haven't blocked anyone.</p>
          ) : (
            <ul className="plain-list">
              {blocked.map((b, i) => (
                <li key={b.id ?? i}>
                  <span>User #{b.id}</span>
                  {b.id != null && <button className="btn secondary" onClick={() => unblock(b.id)}>Unblock</button>}
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="card">
          <h2>Report a person</h2>
          <form onSubmit={submitReport}>
            <label htmlFor="r-user">User ID</label>
            <input id="r-user" type="number" min="1" value={report.reported_user_id} onChange={(e) => setReport({ ...report, reported_user_id: e.target.value })} required />
            <label htmlFor="r-comm">Community ID (optional)</label>
            <input id="r-comm" type="number" min="1" value={report.community_id} onChange={(e) => setReport({ ...report, community_id: e.target.value })} />
            <label htmlFor="r-reason">What happened?</label>
            <textarea id="r-reason" rows={4} minLength={5} maxLength={1000} value={report.reason} onChange={(e) => setReport({ ...report, reason: e.target.value })} required />
            <button className="btn danger" disabled={busy}>Submit report</button>
          </form>
        </section>
      </div>
    </div>
  );
}
