type Advisory = { detail_message: string | null; rule_clause_ref: string };

/** Tier-3 advisory findings — kept visually separate from compliance verdicts. */
export default function AdvisoryPanel({ advisories }: { advisories: Advisory[] }) {
  if (advisories.length === 0) return null;
  return (
    <section aria-label="Advisory (non-binding)">
      <h2>Advisory — not a compliance verdict</h2>
      <ul>
        {advisories.map((a, i) => (
          <li key={i}>{a.detail_message}</li>
        ))}
      </ul>
    </section>
  );
}
