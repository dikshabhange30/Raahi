import AuthLayout from "../components/AuthLayout";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api, { getErrorMessage } from "../services/api";

export default function VerifyEmail() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState(location.state?.email || "");
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await api.post("/auth/verify-email", { email, otp });
      navigate("/login", { state: { message: "Email verified. You can log in now." } });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout>
      <form className="card auth-card" onSubmit={onSubmit}>
        <h1>Verify your email</h1>
        <p className="muted">Enter the 6-digit code we emailed you.</p>

        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />

        <label htmlFor="otp">6-digit code</label>
        <input id="otp" value={otp} onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
          maxLength={6} inputMode="numeric" pattern="\d{6}" required />

        {error && <div className="error" role="alert">{error}</div>}
        <button className="btn" disabled={busy}>{busy ? "Verifying…" : "Verify email"}</button>
      </form>
    </AuthLayout>
  );
}
