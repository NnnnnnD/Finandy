import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Balance | Saving
    is_primary = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")

    transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.account_id",
        back_populates="account",
    )

    aliases = relationship("AccountAlias", back_populates="account")

    __table_args__ = (
        Index("idx_accounts_user", "user_id"),
    )
