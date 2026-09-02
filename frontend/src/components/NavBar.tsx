import Link from "next/link";

export default function NavBar() {
  return (
    <nav>
      <Link href="/upload">New scan</Link>
      <Link href="/history">History</Link>
      <Link href="/dashboard">Dashboard</Link>
      <Link href="/login">Login</Link>
    </nav>
  );
}
