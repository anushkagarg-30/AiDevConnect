import { useState, type FormEvent } from "react";
import { Link, Navigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";

function AuthLoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
    </div>
  );
}

export function Login() {
  const { login, user, loading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (loading) return <AuthLoadingScreen />;
  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-600 text-lg font-bold">
            AI
          </div>
          <h1 className="text-2xl font-bold text-white">Welcome back</h1>
          <p className="mt-2 text-slate-400">Sign in to find your next collaborator</p>
        </div>

        <form onSubmit={handleSubmit} className="rounded-2xl border border-slate-800 bg-surface-800/50 p-6">
          {error && (
            <div className="mb-4 rounded-lg border border-rose-500/30 bg-rose-900/20 px-3 py-2 text-sm text-rose-300">
              {error}
            </div>
          )}

          <label className="block text-sm font-medium text-slate-300">
            Email
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-surface-900 px-3 py-2 text-white outline-none focus:border-brand-500"
            />
          </label>

          <label className="mt-4 block text-sm font-medium text-slate-300">
            Password
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-700 bg-surface-900 px-3 py-2 text-white outline-none focus:border-brand-500"
            />
          </label>

          <button
            type="submit"
            disabled={submitting}
            className="mt-6 w-full rounded-lg bg-brand-600 py-2.5 font-medium text-white transition hover:bg-brand-500 disabled:opacity-50"
          >
            {submitting ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-400">
          Demo (password <span className="text-slate-300">demo1234</span> for all):
        </p>
        <ul className="mt-2 space-y-1 text-center text-xs text-slate-500">
          <li><span className="text-slate-400">alice@demo.com</span> — food / ML matching</li>
          <li><span className="text-slate-400">emma@demo.com</span> — justice / social impact</li>
          <li><span className="text-slate-400">carol@demo.com</span> — DevOps / infra</li>
        </ul>

        <p className="mt-2 text-center text-sm text-slate-400">
          No account?{" "}
          <Link to="/register" className="text-brand-400 hover:text-brand-300">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
