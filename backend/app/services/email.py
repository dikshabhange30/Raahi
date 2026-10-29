
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_otp_email(to_email: str, otp: str, purpose: str) -> None:
    if purpose == "registration":
        subject = "Verify your Raahi email"
        heading = "Verify your email address"
        message = "Use this code to verify your Raahi account."

    elif purpose == "login":
        subject = "Your Raahi login code"
        heading = "Complete your Raahi login"
        message = "Use this code to finish signing in to Raahi."

    elif purpose == "password_reset":
        subject = "Reset your Raahi password"
        heading = "Reset your password"
        message = (
            "Use this code to reset your Raahi account password. "
            "If you did not request this, you can ignore this email."
        )

    else:
        raise ValueError("Invalid email purpose.")

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = settings.email_from
    email["To"] = to_email

    email.set_content(
        f"{heading}\n\n"
        f"{message}\n\n"
        f"Your OTP is: {otp}\n\n"
        "This code expires in 10 minutes."
    )

    email.add_alternative(
        f"""
        <html>
            <body>
                <h2>{heading}</h2>
                <p>{message}</p>
                <h1>{otp}</h1>
                <p>This code expires in 10 minutes.</p>
            </body>
        </html>
        """,
        subtype="html",
    )

    try:
        with smtplib.SMTP(
            settings.email_host,
            settings.email_port,
        ) as server:
            server.starttls()
            server.login(
                settings.email_username,
                settings.email_password,
            )
            server.send_message(email)

        print(f"OTP email sent successfully to {to_email}")

    except Exception as exc:
        print("Gmail SMTP email error:", repr(exc))
        raise
