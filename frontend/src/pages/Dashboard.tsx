import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { ErrorBanner } from "../components/ErrorBanner";
import { useAuth } from "../context/AuthContext";
import type { MatchRequest, Project } from "../types";

export function Dashboard() {
  const { user, token } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [received, setReceived] = useState<MatchRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [projectList, receivedList] = await Promise.all([
        api.listProjects(token),
        api.listReceivedMatches(token),
      ]);
      setProjects(projectList);
      setReceived(receivedList);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return <ErrorBanner message={error} onRetry={load} />;
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Hey, {user?.username}</h1>
        <p className="mt-2 text-slate-400">
          Find collaborators using semantic similarity — powered by pgvector embeddings.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Your projects" value={projects.length} />
        <StatCard
          label="Pending requests"
          value={received.filter((m) => m.status === "pending").length}
          accent
        />
        <StatCard
          label="Accepted matches"
          value={received.filter((m) => m.status === "accepted").length}
        />
      </div>

      {received.filter((m) => m.status === "pending").length > 0 && (
        <section className="mt-8">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Pending match requests</h2>
            <Link to="/matches" className="text-sm text-brand-400 hover:text-brand-300">
              View all →
            </Link>
          </div>
          <div className="rounded-2xl border border-brand-500/30 bg-brand-900/10 p-4">
            <p className="text-sm text-brand-200">
              You have {received.filter((m) => m.status === "pending").length} pending collaboration
              request{received.filter((m) => m.status === "pending").length !== 1 ? "s" : ""}.
            </p>
          </div>
        </section>
      )}

      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Recent projects</h2>
          <Link
            to="/projects"
            className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-500"
          >
            + New project
          </Link>
        </div>

        {projects.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-slate-700 p-8 text-center">
            <p className="text-slate-400">No projects yet. Submit your first idea to start matching.</p>
            <Link
              to="/projects"
              className="mt-4 inline-block text-sm text-brand-400 hover:text-brand-300"
            >
              Create a project →
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {projects.slice(0, 4).map((project) => (
              <Link
                key={project.id}
                to={`/projects/${project.id}/matches`}
                className="rounded-xl border border-slate-800 bg-surface-800/50 p-4 transition hover:border-brand-500/40"
              >
                <h3 className="font-medium text-white">{project.title}</h3>
                <p className="mt-1 line-clamp-2 text-sm text-slate-400">{project.description}</p>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function StatCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: number;
  accent?: boolean;
}) {
  return (
    <div
      className={`rounded-2xl border p-5 ${
        accent ? "border-brand-500/30 bg-brand-900/20" : "border-slate-800 bg-surface-800/50"
      }`}
    >
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-white">{value}</p>
    </div>
  );
}
