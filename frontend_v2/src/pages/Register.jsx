import AuthLayout from "../components/AuthLayout";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";



export default function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await api.post("/auth/register", form);
      navigate("/verify-email", { state: { email: form.email } });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout>
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Join Raahi</h1>
        <p className="muted">Find people from your own language and background, right in your city.</p>

        <label htmlFor="username">Username</label>
        <input id="username" name="username" value={form.username} onChange={onChange} minLength={3} maxLength={50} required />

        <label htmlFor="email">Email</label>
        <input id="email" name="email" type="email" value={form.email} onChange={onChange} required />

        <label htmlFor="password">Password (at least 8 characters)</label>
        <div className="password-field">
          <input
            id="password"
            name="password"
            type={showPassword ? "text" : "password"}
            value={form.password}
            onChange={onChange}
            required
          />

          <button
            type="button"
            className="password-toggle"
            onClick={() => setShowPassword((previous) => !previous)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
          </button>
        </div>

        {error && <div className="error" role="alert">{error}</div>}
        <button className="btn" disabled={busy}>{busy ? "Creating account…" : "Create account"}</button>
        <p className="muted">Already have an account? <Link to="/login">Log in</Link></p>
      </form>
    </AuthLayout>
  );
}
