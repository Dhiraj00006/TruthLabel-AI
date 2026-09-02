"""Loads the declarative ruleset and evaluates declarations against it.

Every finding produced here must carry the rule's clause_ref (NFR2 auditability)
and the ruleset version that produced it (NFR1 reproducibility).
"""
import yaml

from app.config import settings


def load_ruleset(path: str = settings.ruleset_path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def evaluate_declarations(declarations: list[dict], ruleset: dict) -> list[dict]:
    """Return a list of finding dicts: rule_id, clause_ref, verdict, detail_message, tier."""
    raise NotImplementedError
