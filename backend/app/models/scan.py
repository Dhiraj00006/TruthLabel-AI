import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db import Base


class SourceType(str, enum.Enum):
    image = "image"
    listing = "listing"


class ScanStatus(str, enum.Enum):
    processing = "processing"
    complete = "complete"
    failed = "failed"


class PanelType(str, enum.Enum):
    front = "front"
    back = "back"
    side = "side"
    unknown = "unknown"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_type = Column(Enum(SourceType), nullable=False)
    product_name = Column(String)
    manufacturer_name = Column(String)
    category = Column(String)
    net_quantity_declared = Column(Float)
    net_quantity_unit = Column(String)
    status = Column(Enum(ScanStatus), nullable=False, default=ScanStatus.processing)
    created_at = Column(DateTime, server_default=func.now())

    images = relationship("ScanImage", back_populates="scan")
    declarations = relationship("Declaration", back_populates="scan")
    findings = relationship("Finding", back_populates="scan")


class ScanImage(Base):
    __tablename__ = "scan_images"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    panel_type = Column(Enum(PanelType), nullable=False, default=PanelType.unknown)
    image_url = Column(String, nullable=False)
    width_px = Column(Integer)
    height_px = Column(Integer)

    scan = relationship("Scan", back_populates="images")
