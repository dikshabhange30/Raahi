import Sticker from "../components/Stickers";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

function Skeletons() {
  return (
    <div className="grid">
      {[1, 2, 3].map((i) => <div key={i} className="card skeleton" />)}
    </div>
  );
}

export default function Communities() {
  const { user } = useAuth();
  const toast = useToast();
  const [tab, setTab] = useState("discover");
  const [all, setAll] = useState([]);
  const [mine, setMine] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filters, setFilters] = useState({ city: "", language: "", gender: "" });
  const [showCreate, setShowCreate] = useState(false);
  const [busyId, setBusyId] = useState(null);

  const load = useCallback(async (f) => {
    setLoading(true);
    setError("");
    try {
      const params = {};
      if (f.city.trim().length >= 2) params.city = f.city.trim();
      if (f.language.trim().length >= 2) params.language = f.language.trim();
      const [a, m] = await Promise.all([
        api.get("/communities/", { params }),
        api.get("/communities/mine"),
      ]);
      setAll(a.data);
      setMine(m.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(filters); /* eslint-disable-next-line */ }, []);

  const joinedIds = useMemo(() => new Set(mine.map((c) => c.id)), [mine]);
  const genders = useMemo(() => [...new Set(all.map((c) => c.gender_eligibility))], [all]);

  const visible = (tab === "discover" ? all : mine).filter(
    (c) => !filters.gender || c.gender_eligibility === filters.gender
  );

  const join = async (c) => {
    setBusyId(c.id);
    try {
      await api.post(`/communities/${c.id}/join`);
      toast(`Joined ${c.name}`);
      await load(filters);
    } catch (err) {
      toast(getErrorMessage(err), "error");
    } finally { setBusyId(null); }
  };

  const leave = async (c) => {
    if (!window.confirm(`Leave ${c.name}?`)) return;
    setBusyId(c.id);
    try {
      await api.delete(`/communities/${c.id}/leave`);
      toast(`Left ${c.name}`);
      await load(filters);
    } catch (err) {
      toast(getErrorMessage(err), "error");
    } finally { setBusyId(null); }
  };

  const onSearch = (e) => { e.preventDefault(); load(filters); };
  const clear = () => {
    const f = { city: "", language: "", gender: "" };
    setFilters(f);
    load(f);
  };

  return (
    <div className="page">
      <header className="page-head">
        <div>
          <h1>Hello, {user.full_name || user.username}</h1>
          <p className="muted">Find a community that speaks your language in your city.</p>
        </div>
        <button className="btn" onClick={() => setShowCreate((s) => !s)}>
          {showCreate ? "Close" : "Start a community"}
        </button>
      </header>

      {showCreate && (
        <CreateCommunity
          onDone={() => { setShowCreate(false); load(filters); }}
        />
      )}

      <div className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "discover"} className={tab === "discover" ? "active" : ""} onClick={() => setTab("discover")}>
          Discover
        </button>
        <button role="tab" aria-selected={tab === "mine"} className={tab === "mine" ? "active" : ""} onClick={() => setTab("mine")}>
          Joined ({mine.length})
        </button>
      </div>

      <form className="filters" onSubmit={onSearch}>
        <div>
          <label htmlFor="f-city">City</label>
          <input id="f-city" value={filters.city} onChange={(e) => setFilters({ ...filters, city: e.target.value })} placeholder="e.g. Pune" />
        </div>
        <div>
          <label htmlFor="f-lang">Language</label>
          <input id="f-lang" value={filters.language} onChange={(e) => setFilters({ ...filters, language: e.target.value })} placeholder="e.g. Marathi" />
        </div>
        <div>
          <label htmlFor="f-gender">Gender eligibility</label>
          <select id="f-gender" value={filters.gender} onChange={(e) => setFilters({ ...filters, gender: e.target.value })}>
            <option value="">Any</option>
            {genders.map((g) => <option key={g} value={g}>{g}</option>)}
          </select>
        </div>
        <div className="filter-actions">
          <button className="btn">Search</button>
          <button type="button" className="btn secondary" onClick={clear}>Clear</button>
        </div>
      </form>

      {error && <div className="error" role="alert">{error}</div>}
      {loading ? <Skeletons /> : visible.length === 0 ? (
        <div className="card empty-state"><Sticker name="house" size={84} rotate={-6} />
          <h2>{tab === "mine" ? "You haven't joined a community yet" : "No communities match"}</h2>
          <p className="muted">
            {tab === "mine"
              ? "Open Discover and join one to start chatting."
              : "Try a different city or language, or start the first one yourself."}
          </p>
        </div>
      ) : (
        <div className="grid">
          {visible.map((c) => {
            const joined = joinedIds.has(c.id);
            return (
              <article key={c.id} className={`card community tone-${["pista", "blush", "olive", "sand"][c.id % 4]}`}>
                <Sticker name={["leaf", "flower", "sun", "sparkle"][c.id % 4]} size={46} rotate={10} className="corner" />
                <h2>{c.name}</h2>
                <div className="chips">
                  <span className="chip">{c.city}</span>
                  <span className="chip">{c.language}</span>
                  <span className="chip alt">{c.gender_eligibility}</span>
                </div>
                <p className="muted">{c.description || "No description yet."}</p>
                <div className="card-actions">
                  {joined ? (
                    <>
                      <Link className="btn" to={`/communities/${c.id}`}>Open chat</Link>
                      <button className="btn secondary" disabled={busyId === c.id} onClick={() => leave(c)}>Leave</button>
                    </>
                  ) : (
                    <button className="btn" disabled={busyId === c.id} onClick={() => join(c)}>
                      {busyId === c.id ? "Joining…" : "Join community"}
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

function CreateCommunity({ onDone }) {
  const toast = useToast();
  const [form, setForm] = useState({ name: "", city: "", language: "", gender_eligibility: "all", description: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = { ...form, description: form.description.trim() || null };
      await api.post("/communities/", body);
      toast("Community created");
      onDone();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally { setBusy(false); }
  };

  return (
    <form className="card form-grid" onSubmit={submit}>
      <div><label htmlFor="c-name">Name</label><input id="c-name" name="name" value={form.name} onChange={set} minLength={3} maxLength={100} required /></div>
      <div><label htmlFor="c-city">City</label><input id="c-city" name="city" value={form.city} onChange={set} minLength={2} required /></div>
      <div><label htmlFor="c-lang">Language</label><input id="c-lang" name="language" value={form.language} onChange={set} minLength={2} required /></div>
      <div>
        <label htmlFor="c-gender">Who can join</label>
        <input id="c-gender" name="gender_eligibility" value={form.gender_eligibility} onChange={set} list="gender-options" required />
        <datalist id="gender-options"><option value="all" /><option value="female" /><option value="male" /></datalist>
      </div>
      <div className="span2"><label htmlFor="c-desc">Description</label><textarea id="c-desc" name="description" value={form.description} onChange={set} rows={3} maxLength={2000} /></div>
      {error && <div className="error span2" role="alert">{error}</div>}
      <div className="span2"><button className="btn" disabled={busy}>{busy ? "Creating…" : "Create community"}</button></div>
    </form>
  );
}
