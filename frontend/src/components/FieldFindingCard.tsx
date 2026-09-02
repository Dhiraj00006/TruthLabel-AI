import ConfidenceBadge from "./ConfidenceBadge";

type Finding = {
  field_name: string | null;
  verdict: "compliant" | "non_compliant" | "not_detected";
  rule_clause_ref: string;
  detail_message: string | null;
  confidence: number | null;
};

export default function FieldFindingCard({ finding }: { finding: Finding }) {
  return (
    <div data-verdict={finding.verdict}>
      <strong>{finding.field_name ?? "Unknown field"}</strong>
      <p>{finding.detail_message}</p>
      <small>{finding.rule_clause_ref}</small>
      <ConfidenceBadge confidence={finding.confidence} />
    </div>
  );
}
