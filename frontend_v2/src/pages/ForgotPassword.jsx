


import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import api, { getErrorMessage } from "../services/api";
import { Eye, EyeOff } from "lucide-react";

export default function ForgotPassword() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [otpSent, setOtpSent] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);

  const requestOtp = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setBusy(true);

    try {
      const { data } = await api.post("/auth/forgot-password", {
        email: email.trim(),
      });

      setOtpSent(true);
      setSuccess(
        data.message || "If an eligible account exists, a reset OTP has been sent."
      );
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const resetPassword = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    setBusy(true);

    try {
      const { data } = await api.post("/auth/reset-password", {
        email: email.trim(),
        otp,
        new_password: newPassword,
      });

      navigate("/login", {
        replace: true,
        state: {
          message:
            data.message ||
            "Password reset successfully. Please log in with your new password.",
        },
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthLayout>
      <div className="card auth-card">
        <h1>Reset your password</h1>

        <p className="muted">
          {otpSent
            ? "Enter the OTP from your email and choose a new password."
            : "Enter your registered email address to receive a password reset OTP."}
        </p>

        {!otpSent ? (
          <form onSubmit={requestOtp}>
            <label htmlFor="reset-email">Registered email</label>
            <input
              id="reset-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />

            {error && <div className="error" role="alert">{error}</div>}
            {success && <div className="success">{success}</div>}

            <button className="btn" disabled={busy}>
              {busy ? "Sending OTP…" : "Send reset OTP"}
            </button>
          </form>
        ) : (
          <form onSubmit={resetPassword}>
            <label htmlFor="reset-email-display">Email</label>
            <input
              id="reset-email-display"
              type="email"
              value={email}
              readOnly
            />

            <label htmlFor="reset-otp">Six-digit OTP</label>
            <input
              id="reset-otp"
              type="text"
              inputMode="numeric"
              pattern="[0-9]{6}"
              maxLength={6}
              value={otp}
              onChange={(e) =>
                setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              autoComplete="one-time-code"
              required
            />

            <label htmlFor="new-password">New password</label>
            <div className="password-field">
                <input
                    id="new-password"
                    type={showNewPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    minLength={8}
                    maxLength={128}
                    autoComplete="new-password"
                    required
                />

                <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowNewPassword((previous) => !previous)}
                    aria-label={showNewPassword ? "Hide password" : "Show password"}
                >
                    {showNewPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
            </div>

            <label htmlFor="confirm-password">Confirm new password</label>
            <div className="password-field">
                <input
                    id="confirm-password"
                    type={showConfirmPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    minLength={8}
                    maxLength={128}
                    autoComplete="new-password"
                    required
                />

                <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowConfirmPassword((previous) => !previous)}
                    aria-label={showConfirmPassword ? "Hide password" : "Show password"}
                >
                    {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
            </div>

            {error && <div className="error" role="alert">{error}</div>}

            <button className="btn" disabled={busy}>
              {busy ? "Resetting password…" : "Reset password"}
            </button>

            <button
              type="button"
              className="btn"
              disabled={busy}
              onClick={() => {
                setOtpSent(false);
                setOtp("");
                setNewPassword("");
                setConfirmPassword("");
                setError("");
                setSuccess("");
              }}
            >
              Use another email
            </button>
          </form>
        )}

        <p className="muted">
          Remember your password? <Link to="/login">Back to login</Link>
        </p>
      </div>
    </AuthLayout>
  );
}
