import enum

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db import Base


class FieldName(str, enum.Enum):
    mfr_address = "mfr_address"
    net_quantity = "net_quantity"
    mrp = "mrp"
    mfg_date = "mfg_date"
    consumer_care = "consumer_care"
    country_of_origin = "country_of_origin"
    unit_sale_price = "unit_sale_price"
    commodity_name = "commodity_name"


class Declaration(Base):
    __tablename__ = "declarations"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    field_name = Column(Enum(FieldName), nullable=False)
    raw_text = Column(String)
    normalized_value = Column(String)
    bounding_box = Column(JSON)  # {x, y, w, h, image_id}
    confidence = Column(Float)

    scan = relationship("Scan", back_populates="declarations")
