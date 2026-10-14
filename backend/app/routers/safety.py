



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserBlock, UserReport
from app.schemas import UserReportCreate, UserReportResponse
from app.routers.users import get_current_user

router = APIRouter(prefix="/safety", tags=["Safety"])


def require_admin(user: User):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required.")


@router.post("/block/{user_id}")
def block_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot block yourself.")

    target = db.query(User).filter(
        User.id == user_id,
        User.is_active == True,
    ).first()

    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    existing = db.query(UserBlock).filter(
        UserBlock.blocker_id == current_user.id,
        UserBlock.blocked_id == user_id,
    ).first()

    if existing:
        return {"message": "User is already blocked."}

    db.add(UserBlock(blocker_id=current_user.id, blocked_id=user_id))
    db.commit()
    return {"message": "User blocked successfully."}


@router.delete("/block/{user_id}")
def unblock_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    block = db.query(UserBlock).filter(
        UserBlock.blocker_id == current_user.id,
        UserBlock.blocked_id == user_id,
    ).first()

    if not block:
        raise HTTPException(status_code=404, detail="Block record not found.")

    db.delete(block)
    db.commit()
    return {"message": "User unblocked successfully."}


@router.get("/blocked")
def list_blocked_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    blocks = db.query(UserBlock).filter(
        UserBlock.blocker_id == current_user.id
    ).all()

    return [
        {"user_id": block.blocked_id, "blocked_at": block.created_at}
        for block in blocks
    ]


@router.post("/reports", response_model=UserReportResponse, status_code=201)
def report_user(
    payload: UserReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.reported_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot report yourself.")

    target = db.query(User).filter(
        User.id == payload.reported_user_id
    ).first()

    if not target:
        raise HTTPException(status_code=404, detail="Reported user not found.")

    report = UserReport(
        reporter_id=current_user.id,
        reported_user_id=payload.reported_user_id,
        community_id=payload.community_id,
        reason=payload.reason.strip(),
    )

    if not report.reason:
        raise HTTPException(status_code=422, detail="Reason cannot be empty.")

    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.get("/admin/reports", response_model=list[UserReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return db.query(UserReport).order_by(UserReport.created_at.desc()).all()


@router.patch("/admin/reports/{report_id}")
def update_report_status(
    report_id: int,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    allowed_statuses = {"reviewed", "action_taken", "dismissed"}
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Status must be reviewed, action_taken, or dismissed.",
        )

    report = db.get(UserReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    report.status = new_status
    db.commit()
    db.refresh(report)
    return {"message": "Report status updated.", "id": report.id, "status": report.status}


@router.patch("/admin/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found.")

    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot deactivate yourself.")

    target.is_active = False
    db.commit()
    return {"message": "User deactivated successfully."}


