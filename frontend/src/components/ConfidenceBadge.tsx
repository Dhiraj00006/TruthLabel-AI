type Props = { confidence: number | null };

export default function ConfidenceBadge({ confidence }: Props) {
  if (confidence === null) return <span>NOT_DETECTED — needs review</span>;
  const label = confidence >= 0.8 ? "high" : confidence >= 0.5 ? "medium" : "low";
  return <span data-confidence-level={label}>{Math.round(confidence * 100)}%</span>;
}
