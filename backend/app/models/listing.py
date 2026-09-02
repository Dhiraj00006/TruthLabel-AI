from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.db import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    source_url = Column(String)
    raw_text = Column(String)
    scraped_at = Column(DateTime, server_default=func.now())
