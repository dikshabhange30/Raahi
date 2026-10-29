import AuthLayout from "../components/AuthLayout";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function VerifyLogin() {
  const navigate = useNavigate();
  const location = useLocation();
  const { signIn } = useAuth();
  const [email, setEmail] = useState(location.state?.email || "");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const { data } = await api.post("/auth/verify-login-otp", { email, otp });
      await signIn(data.access_token);
      navigate("/communities", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout>
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Enter your login code</h1>
        <p className="muted">We emailed you a 6-digit code. Confirm your email below.</p>

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

        <label htmlFor="otp">6-digit code</label>
        <input id="otp" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
          maxLength={6} inputMode="numeric" pattern="\d{6}" required />

        {error && <div className="error" role="alert">{error}</div>}
        <button className="btn" disabled={busy}>{busy ? "Verifying…" : "Log in"}</button>
      </form>
    </AuthLayout>
  );
}
