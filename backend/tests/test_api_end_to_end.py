SAMPLE_LISTING_TEXT = """
Premium Almonds - Best in India!
Net Qty: 500g
MRP: Rs. 450.00 (incl. of all taxes)
Mfg Date: 03/2025
Country of Origin: USA
Consumer Care: 1800-123-4567, care@example.com
Marketed by: ExampleFoods Pvt Ltd, 123 Market Street, Mumbai 400001
600g extra free
"""

INCOMPLETE_LISTING_TEXT = "Just a plain product title with nothing else useful."


def test_create_listing_scan_and_findings(client):
    resp = client.post("/listings", json={
        "text": SAMPLE_LISTING_TEXT,
        "product_name": "Premium Almonds",
        "manufacturer_name": "ExampleFoods",
        "category": "Food",
        "net_quantity_declared": 500,
        "net_quantity_unit": "g",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "complete"

    findings_by_field = {f["field_name"]: f for f in data["findings"] if f["tier"] != "3_advisory"}
    assert findings_by_field["mrp"]["verdict"] == "compliant"
    assert findings_by_field["mfg_date"]["verdict"] == "compliant"
    assert findings_by_field["net_quantity"]["verdict"] == "compliant"

    for f in data["findings"]:
        assert f["rule_clause_ref"]

    advisories = [f for f in data["findings"] if f["tier"] == "3_advisory"]
    assert any("best in india" in (f["detail_message"] or "").lower() for f in advisories)
    assert any("extra" in (f["detail_message"] or "").lower() for f in advisories)


def test_missing_fields_are_not_detected_not_non_compliant(client):
    resp = client.post("/listings", json={"text": INCOMPLETE_LISTING_TEXT})
    assert resp.status_code == 200
    data = resp.json()
    for f in data["findings"]:
        if f["tier"] != "3_advisory":
            assert f["verdict"] in ("not_detected", "compliant")
            assert f["verdict"] != "non_compliant"


def test_image_scan_all_not_detected(client):
    resp = client.post("/scans", params={"product_name": "Mystery Product"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "complete"
    assert len(data["findings"]) > 0
    for f in data["findings"]:
        assert f["verdict"] == "not_detected"


def test_override_preserves_original_finding(client):
    resp = client.post("/listings", json={"text": INCOMPLETE_LISTING_TEXT})
    scan_id = resp.json()["id"]
    finding_id = resp.json()["findings"][0]["id"]
    original_verdict = resp.json()["findings"][0]["verdict"]

    override_resp = client.post(f"/scans/{scan_id}/override", json={
        "finding_id": finding_id,
        "reason": "Verified manually on physical label",
    })
    assert override_resp.status_code == 200
    updated = next(f for f in override_resp.json()["findings"] if f["id"] == finding_id)
    assert updated["verdict"] == original_verdict  # original finding preserved, not replaced
    assert updated["override_reason"] == "Verified manually on physical label"
    assert updated["overridden_by"] == 1


def test_dashboard_summary(client):
    client.post("/listings", json={"text": SAMPLE_LISTING_TEXT, "category": "Food"})
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_scans"] >= 1


def test_report_json_export(client):
    resp = client.post("/listings", json={"text": SAMPLE_LISTING_TEXT})
    scan_id = resp.json()["id"]
    report_resp = client.get(f"/scans/{scan_id}/report.json")
    assert report_resp.status_code == 200
    assert report_resp.json()["scan"]["id"] == scan_id


def test_report_html_export(client):
    resp = client.post("/listings", json={"text": SAMPLE_LISTING_TEXT})
    scan_id = resp.json()["id"]
    report_resp = client.get(f"/scans/{scan_id}/report.pdf")
    assert report_resp.status_code == 200
    assert "Findings" in report_resp.text


def test_login_with_seeded_demo_user(client):
    resp = client.post("/auth/login", json={"email": "inspector@truthlabel.ai", "password": "demo1234"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_rejects_wrong_password(client):
    resp = client.post("/auth/login", json={"email": "inspector@truthlabel.ai", "password": "wrong"})
    assert resp.status_code == 401
