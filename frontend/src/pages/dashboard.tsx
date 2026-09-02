import { useEffect, useState } from "react";

import { getDashboardSummary } from "../lib/api";

export default function Dashboard() {
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    getDashboardSummary().then(setSummary).catch(console.error);
  }, []);

  return (
    <main>
      <h1>Compliance dashboard</h1>
      <pre>{summary ? JSON.stringify(summary, null, 2) : "Loading…"}</pre>
    </main>
  );
}
