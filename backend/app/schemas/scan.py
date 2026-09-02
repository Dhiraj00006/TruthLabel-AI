from pydantic import BaseModel


class ScanCreateRequest(BaseModel):
    product_name: str | None = None
    manufacturer_name: str | None = None
    category: str | None = None
    net_quantity_declared: float | None = None
    net_quantity_unit: str | None = None
    package_height_mm: float | None = None


class FindingResponse(BaseModel):
    field_name: str | None
    verdict: str
    rule_clause_ref: str
    detail_message: str | None
    tier: str
    confidence: float | None = None

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    id: int
    status: str
    findings: list[FindingResponse] = []

    class Config:
        from_attributes = True
