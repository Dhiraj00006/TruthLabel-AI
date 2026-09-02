from fastapi import APIRouter

router = APIRouter()


@router.get("/scans/{scan_id}/report.pdf")
def get_report_pdf(scan_id: int):
    raise NotImplementedError


@router.get("/scans/{scan_id}/report.docx")
def get_report_editable(scan_id: int):
    raise NotImplementedError
