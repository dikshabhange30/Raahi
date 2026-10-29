import AuthLayout from "../components/AuthLayout";
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";


export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ identifier: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const info = location.state?.message;

  const onChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { data } = await api.post("/auth/login", form);
      // The OTP step needs an email: use what was typed, else what the backend returned.
      const email = form.identifier.includes("@") ? form.identifier : data?.email || "";
      navigate("/verify-login", { state: { email } });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout>
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Welcome back</h1>
        <p className="muted">Log in to reach your communities.</p>
        {info && <div className="success">{info}</div>}

        <label htmlFor="identifier">Username, email or full name</label>
        <input id="identifier" name="identifier" value={form.identifier} onChange={onChange} required />

        <label htmlFor="password">Password</label>

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

        <p className="muted" style={{ textAlign: "right", marginTop: "4px" }}>
        <Link to="/forgot-password">Forgot password?</Link>
        </p>

        {error && <div className="error" role="alert">{error}</div>}
        <button className="btn" disabled={busy}>{busy ? "Checking…" : "Continue"}</button>
        <p className="muted">New here? <Link to="/register">Create an account</Link></p>
      </form>
    </AuthLayout>
  );
}
