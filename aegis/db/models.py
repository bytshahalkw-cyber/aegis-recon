from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from aegis.db.session import Base

class ScanModel(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="SUCCESS")

    findings = relationship("FindingModel", back_populates="scan", cascade="all, delete-orphan")

class FindingModel(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    module_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, default="INFO")

    scan = relationship("ScanModel", back_populates="findings")
