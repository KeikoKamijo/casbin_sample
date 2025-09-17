from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
from .associations import corporation_shop


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    address = Column(String)
    manager_name = Column(String)
    business_hours = Column(String)  # e.g., "9:00-20:00"
    is_active = Column(Boolean, default=True)
    corporation_id = Column(Integer, ForeignKey("corporations.id"))  # Direct relationship for primary owner
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    primary_corporation = relationship("Corporation", foreign_keys=[corporation_id], backref="owned_shops")
    corporations = relationship("Corporation", secondary=corporation_shop, back_populates="shops")