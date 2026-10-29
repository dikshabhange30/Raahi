import Sticker from "../components/Stickers";
import { useCallback, useEffect, useState } from "react";
import api, { getErrorMessage } from "../services/api";
import { useToast } from "../context/ToastContext";
import { fmtTime } from "../utils";

const STATUSES = ["pending", "reviewed", "resolved", "dismissed"];

export default function Admin() {
  const toast = useToast();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const { data } = await api.get("/safety/admin/reports");
      setReports(data);
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const setStatus = async (id, status) => {
    try {
      await api.patch(`/safety/admin/reports/${id}`, null, { params: { new_status: status } });
      toast("Report updated");
      await load();
    } catch (err) { toast(getErrorMessage(err), "error"); }
  };

  const deactivate = async (userId) => {
    if (!window.confirm(`Deactivate user #${userId}?`)) return;
    try {
      await api.patch(`/safety/admin/users/${userId}/deactivate`);
      toast(`User #${userId} deactivated`);
    } catch (err) { toast(getErrorMessage(err), "error"); }
  };

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <h1>Admin: reports</h1>
          <p className="muted">Review reports and act on them. Only visible to administrators.</p>
        </div>
      </header>
      {error && <div className="error" role="alert">{error}</div>}
      {loading ? <div className="card skeleton" /> : reports.length === 0 ? (
        <div className="card empty-state"><Sticker name="shield" size={84} rotate={-6} /><h2>No reports</h2><p className="muted">Nothing to review right now.</p></div>
      ) : (
        <div className="stack">
          {reports.map((r) => (
            <article key={r.id} className="card request">
              <div className="request-top">
                <strong>Report #{r.id}: user #{r.reported_user_id} reported by user #{r.reporter_id}</strong>
                <span className={`status ${(r.status || "").toLowerCase()}`}>{r.status}</span>
              </div>
              <p>{r.reason}</p>
              <div className="muted small">{r.community_id ? `Community #${r.community_id} · ` : ""}{fmtTime(r.created_at)}</div>
              <div className="card-actions">
                <label htmlFor={`st-${r.id}`} className="sr-only">Status</label>
                <select id={`st-${r.id}`} value={r.status} onChange={(e) => setStatus(r.id, e.target.value)} className="status-select">
                  {[...new Set([r.status, ...STATUSES])].map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
                <button className="btn danger" onClick={() => deactivate(r.reported_user_id)}>Deactivate user</button>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
