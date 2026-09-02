from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.db import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    pdf_url = Column(String)
    editable_url = Column(String)
    generated_at = Column(DateTime, server_default=func.now())
