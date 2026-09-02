export default function Login() {
  return (
    <main>
      <h1>TruthLabel AI — Sign in</h1>
      <form>
        <input type="email" name="email" placeholder="Email" required />
        <input type="password" name="password" placeholder="Password" required />
        <button type="submit">Sign in</button>
      </form>
    </main>
  );
}
