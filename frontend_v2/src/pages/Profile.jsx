import { useEffect, useState } from "react";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { initials } from "../utils";

export default function Profile() {
  const { user, refreshUser } = useAuth();
  const toast = useToast();
  const [form, setForm] = useState({ full_name: "", gender: "", city: "", profession: "", bio: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const genderLocked = Boolean(user.gender);

  useEffect(() => {
    setForm({
      full_name: user.full_name || "",
      gender: user.gender || "",
      city: user.city || "",
      profession: user.profession || "",
      bio: user.bio || "",
    });
  }, [user]);

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    const body = {
      full_name: form.full_name.trim() || null,
      city: form.city.trim() || null,
      profession: form.profession.trim() || null,
      bio: form.bio.trim() || null,
    };
    // Gender can only be set once, so only send it if it isn't set yet.
    if (!genderLocked && form.gender) body.gender = form.gender;
    try {
      await api.patch("/users/me", body);
      await refreshUser();
      toast("Profile saved");
    } catch (err) { setError(getErrorMessage(err)); }
    finally { setBusy(false); }
  };

  return (
    <div className="page">
      <header className="page-head">
        <div className="profile-head">
          <div className="avatar lg">{initials(user.full_name || user.username)}</div>
          <div>
            <h1>{user.full_name || user.username}</h1>
            <p className="muted">@{user.username} · {user.email}</p>
          </div>
        </div>
      </header>

      <form className="card form-grid" onSubmit={submit}>
        <div><label htmlFor="p-name">Full name</label><input id="p-name" name="full_name" value={form.full_name} onChange={set} maxLength={100} /></div>
        <div>
          <label htmlFor="p-gender">Gender</label>
          <select id="p-gender" name="gender" value={form.gender} onChange={set} disabled={genderLocked}>
            <option value="">Select…</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="other">Other</option>
          </select>
          {genderLocked && <p className="muted small">Gender can't be changed once it's set.</p>}
        </div>
        <div><label htmlFor="p-city">City</label><input id="p-city" name="city" value={form.city} onChange={set} maxLength={100} /></div>
        <div><label htmlFor="p-prof">Profession</label><input id="p-prof" name="profession" value={form.profession} onChange={set} maxLength={100} /></div>
        <div className="span2"><label htmlFor="p-bio">Bio</label><textarea id="p-bio" name="bio" rows={4} value={form.bio} onChange={set} maxLength={500} /></div>
        {error && <div className="error span2" role="alert">{error}</div>}
        <div className="span2"><button className="btn" disabled={busy}>{busy ? "Saving…" : "Save changes"}</button></div>
      </form>
    </div>
  );
}
