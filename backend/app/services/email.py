
import resend
from app.core.config import settings


def send_otp_email(to_email: str, otp: str, purpose: str) -> None:
    resend.api_key = settings.resend_api_key

    if purpose == "registration":
        subject = "Verify your Raahi email"
        heading = "Verify your email address"
        message = "Use this code to verify your Raahi account."
    elif purpose == "login":
        subject = "Your Raahi login code"
        heading = "Complete your Raahi login"
        message = "Use this code to finish signing in to Raahi."
    else:
        raise ValueError("Invalid email purpose.")

    params = {
        "from": settings.email_from,
        "to": [to_email],
        "subject": subject,
        "html": f"""
            <h2>{heading}</h2>
            <p>{message}</p>
            <h1>{otp}</h1>
            <p>This code expires in 10 minutes.</p>
        """,
    }

    try:
        response = resend.Emails.send(params)
        print("Resend response:", response)
    except Exception as exc:
        print("Resend email error:", repr(exc))
        raise
