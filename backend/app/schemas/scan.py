from pydantic import BaseModel


class FindingResponse(BaseModel):
    id: int
    field_name: str | None
    verdict: str
    rule_id: str
    rule_clause_ref: str
    detail_message: str | None
    tier: str
    ruleset_version: int | None = None
    overridden_by: int | None = None
    override_reason: str | None = None

    class Config:
        from_attributes = True


class DeclarationResponse(BaseModel):
    id: int
    field_name: str
    raw_text: str | None
    normalized_value: str | None
    confidence: float | None

    class Config:
        from_attributes = True


class ScanResponse(BaseModel):
    id: int
    source_type: str
    status: str
    product_name: str | None
    manufacturer_name: str | None
    category: str | None
    net_quantity_declared: float | None
    net_quantity_unit: str | None
    findings: list[FindingResponse] = []
    declarations: list[DeclarationResponse] = []

    class Config:
        from_attributes = True


class ScanSummary(BaseModel):
    id: int
    source_type: str
    status: str
    product_name: str | None
    manufacturer_name: str | None
    category: str | None

    class Config:
        from_attributes = True


class OverrideRequest(BaseModel):
    finding_id: int
    reason: str


class ListingCreateRequest(BaseModel):
    source_url: str | None = None
    text: str | None = None
    product_name: str | None = None
    manufacturer_name: str | None = None
    category: str | None = None
    net_quantity_declared: float | None = None
    net_quantity_unit: str | None = None
