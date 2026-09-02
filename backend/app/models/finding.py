import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Verdict(str, enum.Enum):
    compliant = "compliant"
    non_compliant = "non_compliant"
    not_detected = "not_detected"


class Tier(str, enum.Enum):
    presence = "1_presence"
    format_placement = "2_format_placement"
    advisory = "3_advisory"


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    declaration_id = Column(Integer, ForeignKey("declarations.id"), nullable=True)
    rule_id = Column(String, nullable=False)
    rule_clause_ref = Column(String, nullable=False)
    verdict = Column(Enum(Verdict), nullable=False)
    detail_message = Column(String)
    tier = Column(Enum(Tier), nullable=False)
    overridden_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    override_reason = Column(String, nullable=True)

    scan = relationship("Scan", back_populates="findings")
