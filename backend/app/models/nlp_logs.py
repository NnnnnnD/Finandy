import uuid
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.core.database import Base


class NLPLog(Base):
    __tablename__ = "nlp_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    raw_text = Column(Text, nullable=False)

    predicted_type = Column(String)
    predicted_account = Column(String)
    confidence = Column(Float)

    final_type = Column(String)
    final_account = Column(String)

    source = Column(String, default="rule")  # rule | ml | corrected
    created_at = Column(DateTime, default=datetime.utcnow)
