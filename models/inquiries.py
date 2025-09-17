from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Inquiry(Base):
    __tablename__ = "inquiries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, in_progress, resolved, closed
    priority = Column(String, default="normal")  # low, normal, high, urgent
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True)
    corporation_id = Column(Integer, ForeignKey("corporations.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id], backref="inquiries_created")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], backref="inquiries_assigned")
    shop = relationship("Shop", backref="inquiries")
    corporation = relationship("Corporation", backref="inquiries")