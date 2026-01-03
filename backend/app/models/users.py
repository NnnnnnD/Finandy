import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=True)
    is_primary = Column(String, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    channels = relationship("UserChannel", back_populates="user")
    accounts = relationship("Account", back_populates="user")

    def __repr__(self):
        return f"<User id={self.id} name={self.name}>"
