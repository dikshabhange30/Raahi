
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=False)
    city = Column(String(100), nullable=False)
    profession = Column(String(100), nullable=True)
    preferred_contact = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)
    
    is_admin = Column(
    Boolean,
    default=False,
    nullable=False
)


class Language(Base):
    __tablename__ = "languages"

    language_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class UserLanguage(Base):
    __tablename__ = "user_languages"

    user_language_id = Column(Integer, primary_key=True, index=True )
    user_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )     
    language_id = Column( Integer, ForeignKey("languages.language_id"), nullable=False )
    __table_args__ = ( #It prevents the same user from selecting the same language twice.
        UniqueConstraint(
            "user_id",
            "language_id",
            name="uq_user_language"
        ),)


class HelpType(Base):
    __tablename__ = "help_types"

    help_type_id = Column( Integer, primary_key=True, index=True)
    name = Column( String(100), unique=True, nullable=False)   
    description = Column( Text, nullable=True)       
    is_active = Column( Boolean, default=True, nullable=False )


class UserHelpOffered(Base):
    __tablename__ = "user_help_offered"

    user_help_offered_id = Column( Integer, primary_key=True, index=True )
    user_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    help_type_id = Column( Integer, ForeignKey("help_types.help_type_id"), nullable=False )

    __table_args__ = (
        UniqueConstraint( "user_id", "help_type_id", name="uq_user_help_offered"),
    )

class UserHelpNeeded(Base):
    __tablename__ = "user_help_needed"

    user_help_needed_id = Column( Integer, primary_key=True, index=True )
    user_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    help_type_id = Column( Integer, ForeignKey("help_types.help_type_id"), nullable=False )

    __table_args__ = (
        UniqueConstraint( "user_id", "help_type_id", name="uq_user_help_needed"),)


class Community(Base):
    __tablename__ = "communities"

    community_id = Column( Integer, primary_key=True, index=True )
    name = Column( String(150), unique=True, nullable=False )
    city = Column( String(100), nullable=False )
    language = Column( String(50), nullable=False )
    gender = Column( String(20), nullable=False )
    description = Column( Text, nullable=True )
    is_active = Column( Boolean, default=True, nullable=False )
    created_at = Column( DateTime(timezone=True), server_default=func.now() )

class CommunityMember(Base):
    __tablename__ = "community_members"

    membership_id = Column( Integer, primary_key=True, index=True )
    user_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    community_id = Column( Integer, ForeignKey("communities.community_id"), nullable=False )
    joined_at = Column( DateTime(timezone=True), server_default=func.now())
    left_at = Column( DateTime(timezone=True), nullable=True )
    is_active = Column( Boolean, default=True, nullable=False )

    __table_args__ = (
        UniqueConstraint("user_id", "community_id",name="uq_user_community" ), )

class GroupMessage(Base):
    __tablename__ = "group_messages"

    group_message_id = Column( Integer, primary_key=True, index=True )
    community_id = Column( Integer, ForeignKey("communities.community_id"), nullable=False )
    sender_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    message = Column( Text, nullable=False )
    created_at = Column( DateTime(timezone=True), server_default=func.now() )

class HelpRequest(Base):
    __tablename__ = "help_requests"

    help_request_id = Column( Integer, primary_key=True, index=True )
    community_id = Column( Integer, ForeignKey("communities.community_id"), nullable=False )
    needer_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    helper_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    message = Column( Text, nullable=False )
    status = Column( String(20), default="pending", nullable=False )
    created_at = Column( DateTime(timezone=True), server_default=func.now() )
    responded_at = Column( DateTime(timezone=True), nullable=True )

class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id = Column( Integer, primary_key=True, index=True )
    help_request_id = Column( Integer, ForeignKey("help_requests.help_request_id"), unique=True, nullable=False )
    created_at = Column( DateTime(timezone=True), server_default=func.now() )
    is_active = Column( Boolean, default=True, nullable=False )

class Message(Base):
    __tablename__ = "messages"

    message_id = Column( Integer, primary_key=True, index=True )
    conversation_id = Column( Integer, ForeignKey("conversations.conversation_id"), nullable=False )
    sender_id = Column( Integer, ForeignKey("users.user_id"), nullable=False )
    message = Column( Text, nullable=False )
    created_at = Column( DateTime(timezone=True), server_default=func.now() )
    is_read = Column( Boolean, default=False, nullable=False )

