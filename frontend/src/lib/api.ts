const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function createScan(formData: FormData) {
  const res = await fetch(`${API_BASE}/scans`, { method: "POST", body: formData });
  if (!res.ok) throw new Error(`createScan failed: ${res.status}`);
  return res.json();
}

export async function getScan(scanId: string) {
  const res = await fetch(`${API_BASE}/scans/${scanId}`);
  if (!res.ok) throw new Error(`getScan failed: ${res.status}`);
  return res.json();
}

export async function overrideFinding(scanId: string, findingId: string, reason: string) {
  const res = await fetch(`${API_BASE}/scans/${scanId}/override`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ finding_id: findingId, reason }),
  });
  if (!res.ok) throw new Error(`overrideFinding failed: ${res.status}`);
  return res.json();
}

export async function getDashboardSummary(params: Record<string, string> = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(`${API_BASE}/dashboard/summary?${qs}`);
  if (!res.ok) throw new Error(`getDashboardSummary failed: ${res.status}`);
  return res.json();
}
