import uuid
from datetime import datetime, date
from sqlalchemy import Column, Date, DateTime, BigInteger, String, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class BalanceCheckpoint(Base):
    __tablename__ = "balance_checkpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)

    balance = Column(BigInteger, nullable=False)
    checkpoint_date = Column(Date, nullable=False)
    source = Column(String, default="manual")

    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account")

    __table_args__ = (
        Index("idx_checkpoint_account_date", "account_id", "checkpoint_date"),
    )
