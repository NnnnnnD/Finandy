import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserChannel(Base):
    __tablename__ = "user_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    channel_type = Column(String, nullable=False)  # telegram | whatsapp
    channel_user_id = Column(String, nullable=False)
    is_primary = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="channels")

    def __repr__(self):
        return f"<UserChannel {self.channel_type}:{self.channel_user_id}>"
