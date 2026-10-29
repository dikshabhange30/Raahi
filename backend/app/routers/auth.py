

# This endpoint:
# - Validates the submitted data through UserRegister.
# - Checks for duplicate usernames and emails.
# - Hashes the password.
# - Saves the user in PostgreSQL.
# - Returns the new user's public details without the password hash.


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, LoginOTP, RegistrationOTP, PasswordResetOTP
from app.schemas import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    LoginOTPVerify,
    RegistrationOTPVerify,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)


import secrets
from datetime import datetime, timedelta, timezone

from app.models import LoginOTP, RegistrationOTP
from app.services.email import send_otp_email
from app.security import hash_password

router = APIRouter(prefix="/auth", tags=["Authentication"])



@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(
            or_(
                User.username == user_data.username,
                User.email == str(user_data.email),
            )
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered.",
        )

    new_user = User(
        username=user_data.username,
        email=str(user_data.email),
        password_hash=hash_password(user_data.password),
        is_email_verified=False,
    )

    otp = f"{secrets.randbelow(1_000_000):06d}"

    registration_otp = None

    try:
        db.add(new_user)
        db.flush()

        registration_otp = RegistrationOTP(
            user_id=new_user.id,
            otp_hash=hash_password(otp),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
            attempts=0,
        )

        db.add(registration_otp)
        db.commit()

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register user.",
        )

    try:
        send_otp_email(
            to_email=new_user.email,
            otp=otp,
            purpose="registration",
        )

    except Exception:
        db.delete(registration_otp)
        db.delete(new_user)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send verification email. Please try again.",
        )

    return {
        "message": "Registration successful. Check your email for the verification code.",
        "email": new_user.email,
    }




@router.post("/login")
def login_user(
    credentials: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == credentials.identifier,
                User.email == credentials.identifier,
            )
        )
        .first()
    )

    if (
        not user
        or not verify_password(
            credentials.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive",
        )

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )

    # Invalidate any previous unused login OTPs for this user.
    db.query(LoginOTP).filter(
        LoginOTP.user_id == user.id,
        LoginOTP.consumed_at.is_(None),
    ).update({"consumed_at": datetime.now(timezone.utc)})

    otp = f"{secrets.randbelow(1_000_000):06d}"

    login_otp = LoginOTP(
        user_id=user.id,
        otp_hash=hash_password(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        attempts=0,
    )

    db.add(login_otp)
    db.commit()

    try:
        send_otp_email(
            to_email=user.email,
            otp=otp,
            purpose="login",
        )
    except Exception:
        db.delete(login_otp)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send login OTP. Please try again.",
        )

    return {
        "message": "Login OTP sent to your registered email address.",
        "email": user.email,
    }



@router.post("/verify-login-otp")
def verify_login_otp(
    otp_data: LoginOTPVerify,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == str(otp_data.email)
    ).first()

    if not user or not user.is_active or not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login OTP request.",
        )

    login_otp = (
        db.query(LoginOTP)
        .filter(
            LoginOTP.user_id == user.id,
            LoginOTP.consumed_at.is_(None),
        )
        .order_by(LoginOTP.created_at.desc())
        .first()
    )

    if not login_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active login OTP. Please log in again.",
        )

    now = datetime.now(timezone.utc)

    if login_otp.expires_at <= now:
        login_otp.consumed_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please log in again.",
        )

    if login_otp.attempts >= 5:
        login_otp.consumed_at = now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. Please log in again.",
        )

    if not verify_password(otp_data.otp, login_otp.otp_hash):
        login_otp.attempts += 1

        if login_otp.attempts >= 5:
            login_otp.consumed_at = now

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP.",
        )

    # Consume the OTP before issuing the access token.
    login_otp.consumed_at = now
    db.commit()

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }



@router.post("/verify-email")
def verify_registration_email(
    otp_data: RegistrationOTPVerify,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == str(otp_data.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification request.",
        )

    if user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified.",
        )

    registration_otp = (
        db.query(RegistrationOTP)
        .filter(
            RegistrationOTP.user_id == user.id,
            RegistrationOTP.consumed_at.is_(None),
        )
        .order_by(RegistrationOTP.created_at.desc())
        .first()
    )

    if not registration_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active verification code. Please register again.",
        )

    now = datetime.now(timezone.utc)
    expires_at = registration_otp.expires_at

    # Handle databases that return a timezone-naive datetime.
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)

    if expires_at <= now:
        registration_otp.consumed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code expired.",
        )

    if registration_otp.attempts >= 5:
        registration_otp.consumed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please register again.",
        )

    if not verify_password(
        otp_data.otp,
        registration_otp.otp_hash,
    ):
        registration_otp.attempts += 1

        if registration_otp.attempts >= 5:
            registration_otp.consumed_at = datetime.now(timezone.utc)

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect verification code.",
        )

    registration_otp.consumed_at = datetime.now(timezone.utc)
    user.is_email_verified = True
    db.commit()

    return {"message": "Email verified successfully."}



@router.post("/forgot-password")
def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    email = str(request.email)

    user = db.query(User).filter(
        User.email == email
    ).first()

    # Do not reveal whether an email is registered.
    generic_response = {
        "message": "If an eligible account exists, a password reset OTP has been sent."
    }

    if not user or not user.is_active or not user.is_email_verified:
        return generic_response

    now = datetime.now(timezone.utc)

    # Invalidate previous unused password-reset OTPs.
    db.query(PasswordResetOTP).filter(
        PasswordResetOTP.user_id == user.id,
        PasswordResetOTP.consumed_at.is_(None),
    ).update(
        {"consumed_at": now},
        synchronize_session=False,
    )

    otp = f"{secrets.randbelow(1_000_000):06d}"

    reset_otp = PasswordResetOTP(
        user_id=user.id,
        otp_hash=hash_password(otp),
        expires_at=now + timedelta(minutes=10),
        attempts=0,
    )

    db.add(reset_otp)
    db.commit()

    try:
        send_otp_email(
            to_email=user.email,
            otp=otp,
            purpose="password_reset",
        )
    except Exception:
        reset_otp.consumed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to send password reset email. Please try again.",
        )

    return generic_response


@router.post("/reset-password")
def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    email = str(reset_data.email)

    user = db.query(User).filter(
        User.email == email,
    ).first()

    if not user or not user.is_active or not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset request.",
        )

    reset_otp = (
        db.query(PasswordResetOTP)
        .filter(
            PasswordResetOTP.user_id == user.id,
            PasswordResetOTP.consumed_at.is_(None),
        )
        .order_by(PasswordResetOTP.created_at.desc())
        .first()
    )

    if not reset_otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active password reset OTP. Request a new one.",
        )

    now = datetime.now(timezone.utc)
    expires_at = reset_otp.expires_at

    # Handle timezone-naive datetimes returned by the database.
    if expires_at.tzinfo is None:
        now = now.replace(tzinfo=None)

    if expires_at <= now:
        reset_otp.consumed_at = datetime.now(timezone.utc)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Request a new password reset OTP.",
        )

    if reset_otp.attempts >= 5:
        reset_otp.consumed_at = datetime.now(timezone.utc)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many incorrect attempts. Request a new OTP.",
        )

    if not verify_password(reset_data.otp, reset_otp.otp_hash):
        reset_otp.attempts += 1

        if reset_otp.attempts >= 5:
            reset_otp.consumed_at = datetime.now(timezone.utc)

        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP.",
        )

    # Save the new password as a hash, never as plain text.
    user.password_hash = hash_password(reset_data.new_password)

    # Prevent the OTP from being reused.
    reset_otp.consumed_at = datetime.now(timezone.utc)

    # Invalidate other outstanding password-reset OTPs.
    db.query(PasswordResetOTP).filter(
        PasswordResetOTP.user_id == user.id,
        PasswordResetOTP.id != reset_otp.id,
        PasswordResetOTP.consumed_at.is_(None),
    ).update(
        {"consumed_at": datetime.now(timezone.utc)},
        synchronize_session=False,
    )

    db.commit()

    return {
        "message": "Password reset successfully. Please log in with your new password."
    }
