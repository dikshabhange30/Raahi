
# models.py defines how data is stored in PostgreSQL.


from sqlalchemy import Boolean, Column, Integer, String
from app.database import Base




from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    full_name = Column(String(100), nullable=True)
    gender = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    profession = Column(String(100), nullable=True)
    bio = Column(String(500), nullable=True)

    is_email_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)


class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    city = Column(String(100), index=True, nullable=False)
    language = Column(String(50), index=True, nullable=False)
    gender_eligibility = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)


class CommunityMember(Base):
    __tablename__ = "community_members"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "community_id",
            name="uq_community_member",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    community_id = Column(
        Integer,
        ForeignKey("communities.id"),
        nullable=False,
    )
    joined_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )



class HelpRequest(Base):
    __tablename__ = "help_requests"

    id = Column(Integer, primary_key=True, index=True)

    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    community_id = Column(Integer, ForeignKey("communities.id"), nullable=False)

    message = Column(String(1000), nullable=False)

    # pending -> accepted or rejected
    status = Column(String(20), nullable=False, default="pending")

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
