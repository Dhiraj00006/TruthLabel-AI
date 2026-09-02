import { useEffect, useState } from "react";
import { useRouter } from "next/router";

import AdvisoryPanel from "../components/AdvisoryPanel";
import FieldFindingCard from "../components/FieldFindingCard";
import { getScan } from "../lib/api";

export default function ScanResult() {
  const router = useRouter();
  const { id } = router.query;
  const [scan, setScan] = useState<any>(null);

  useEffect(() => {
    if (typeof id !== "string") return;
    getScan(id).then(setScan).catch(console.error);
  }, [id]);

  if (!scan) return <p>Loading…</p>;

  const compliance = scan.findings.filter((f: any) => f.tier !== "3_advisory");
  const advisories = scan.findings.filter((f: any) => f.tier === "3_advisory");

  return (
    <main>
      <h1>Scan #{scan.id} — {scan.status}</h1>
      {compliance.map((f: any, i: number) => (
        <FieldFindingCard key={i} finding={f} />
      ))}
      <AdvisoryPanel advisories={advisories} />
    </main>
  );
}
