import Link from "next/link";

export default function Home() {
  return (
    <main>
      <h1>TruthLabel AI</h1>
      <p>Compliance checking for packaged-commodity labels and e-commerce listings.</p>
      <p><Link href="/upload">Start a new scan →</Link></p>
    </main>
  );
}
