from app.rules.engine import load_ruleset


def test_load_ruleset_has_mandatory_fields():
    ruleset = load_ruleset("app/rules/ruleset_v1.yaml")
    field_names = {f["field"] for f in ruleset["fields"]}
    assert {"mrp", "net_quantity", "mfg_date", "mfr_address"} <= field_names


def test_every_field_has_clause_ref():
    ruleset = load_ruleset("app/rules/ruleset_v1.yaml")
    for field in ruleset["fields"]:
        assert field.get("clause_ref"), f"{field['field']} missing clause_ref"
