import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)

    type = Column(String, nullable=False)  # income | expense | transfer
    amount = Column(BigInteger, nullable=False)
    description = Column(String)

    transaction_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship(
        "Account",
        foreign_keys=[account_id],
        back_populates="transactions",
    )

    __table_args__ = (
        Index("idx_tx_account_time", "account_id", "transaction_at"),
    )
