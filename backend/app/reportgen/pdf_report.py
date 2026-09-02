"""Builds the per-scan report from findings + evidence images.

v1 renders HTML (self-contained, no extra native deps). True PDF export via WeasyPrint
is deferred — WeasyPrint needs GTK/Pango system libraries that aren't part of this
project's demo environment yet; swap `render_html` output through weasyprint.HTML(...).write_pdf()
once that's available.
"""
import os

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def render_html(scan, findings, declarations) -> str:
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    template = env.get_template("report.html")

    declarations_by_id = {d.id: d for d in declarations}
    compliance_findings = [f for f in findings if f.tier != "3_advisory"]
    advisory_findings = [f for f in findings if f.tier == "3_advisory"]

    return template.render(
        scan=scan,
        findings=compliance_findings,
        advisories=advisory_findings,
        declarations_by_id=declarations_by_id,
    )
