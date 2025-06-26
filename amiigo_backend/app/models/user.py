from sqlalchemy import Column, Integer, String, DateTime, func, Boolean # Added Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base # Import the Base from our central location

class User(Base):
    """
    SQLAlchemy model for Users.
    Corresponds to the "Users" table in the database schema.
    """
    # __tablename__ = "users" # Optional: Base class handles this, but can be explicit

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    # Optional: Fields for account status, email verification, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False) # For email verification status

    # --- Relationships ---
    # One-to-one relationship with Profile
    # `uselist=False` makes it a scalar (one-to-one) attribute.
    # `back_populates` links it to the corresponding attribute in the Profile model.
    # profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan") # Commented out for now

    # One-to-many relationship with UserInterests (association object)
    # user_interests = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")

    # Swipes made by this user
    # swipes_made = relationship(
    #     "Swipe",
    #     foreign_keys="[Swipe.swiper_user_id]", # Explicitly define if foreign keys are ambiguous
    #     back_populates="swiper",
    #     cascade="all, delete-orphan"
    # )
    # Swipes received by this user (on their profile)
    # swipes_received = relationship(
    #     "Swipe",
    #     foreign_keys="[Swipe.swiped_user_id]",
    #     back_populates="swiped_on",
    #     cascade="all, delete-orphan"
    # )

    # Matches involving this user (as user1)
    # matches_as_user1 = relationship(
    #     "Match",
    #     foreign_keys="[Match.user1_id]",
    #     back_populates="user1",
    #     cascade="all, delete-orphan"
    # )
    # Matches involving this user (as user2)
    # matches_as_user2 = relationship(
    #     "Match",
    #     foreign_keys="[Match.user2_id]",
    #     back_populates="user2",
    #     cascade="all, delete-orphan"
    # )

    # Messages sent by this user
    # messages_sent = relationship(
    #     "Message",
    #     foreign_keys="[Message.sender_user_id]",
    #     back_populates="sender",
    #     cascade="all, delete-orphan"
    # )
    # Messages received by this user
    # messages_received = relationship(
    #     "Message",
    #     foreign_keys="[Message.receiver_user_id]",
    #     back_populates="receiver",
    #     cascade="all, delete-orphan"
    # )


    def __repr__(self):
        return f"<User(user_id={self.user_id}, email='{self.email}')>"

# Note:
# - The DDL used `SERIAL` for `user_id`. SQLAlchemy's `Integer, primary_key=True, autoincrement=True`
#   is the equivalent for PostgreSQL when the table is created via SQLAlchemy.
#   If the table is created by external DDL using SERIAL, SQLAlchemy will still work correctly.
# - `DateTime(timezone=True)` is for timezone-aware datetimes. `server_default=func.now()` uses the DB's now().
# - Relationships are commented out for now and will be defined as we create the other models.
# - Added `is_active` and `is_verified` as common useful fields for a User model.
# ``` # Removed offending backticks
