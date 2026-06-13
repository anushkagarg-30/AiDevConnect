import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../api/client";
import { ErrorBanner } from "../components/ErrorBanner";
import { useAuth } from "../context/AuthContext";
import type { Project, ProjectMatch } from "../types";

export function ProjectMatches() {
  const { projectId } = useParams<{ projectId: string }>();
  const { token } = useAuth();
  const [sourceProject, setSourceProject] = useState<Project | null>(null);
  const [matches, setMatches] = useState<ProjectMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [requesting, setRequesting] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    if (!token || !projectId) return;
    setLoading(true);
    setError("");
    try {
      const [projects, matchList] = await Promise.all([
        api.listProjects(token),
        api.getMatches(token, Number(projectId)),
      ]);
      setSourceProject(projects.find((p) => p.id === Number(projectId)) ?? null);
      setMatches(matchList);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load matches");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [token, projectId]);

  async function handleConnect(targetProjectId: number) {
    if (!token || !projectId) return;
    setRequesting(targetProjectId);
    setMessage("");
    try {
      await api.createMatchRequest(token, {
        project_id: targetProjectId,
        requester_project_id: Number(projectId),
      });
      setMessage("Match request sent! They'll be notified in real time.");
      setMatches((prev) => prev.filter((m) => m.project.id !== targetProjectId));
    } catch (err) {
      setMessage(err instanceof ApiError ? err.message : "Failed to send request");
    } finally {
      setRequesting(null);
    }
  }

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

  if (!sourceProject) {
    return (
      <div className="py-20 text-center">
        <p className="text-slate-400">Project not found.</p>
        <Link to="/projects" className="mt-4 inline-block text-brand-400">
          ← Back to projects
        </Link>
      </div>
    );
  }

  return (
    <div>
      <Link to="/projects" className="text-sm text-slate-400 hover:text-brand-300">
        ← Back to projects
      </Link>

      <div className="mt-4 mb-8">
        <h1 className="text-3xl font-bold text-white">Matches for "{sourceProject.title}"</h1>
        <p className="mt-2 text-slate-400">
          Ranked by Gemini embeddings + pgvector cosine similarity. Only projects above the
          similarity threshold are shown.
        </p>
      </div>

      {message && (
        <div className="mb-6 rounded-lg border border-brand-500/30 bg-brand-900/20 px-4 py-3 text-sm text-brand-200">
          {message}
        </div>
      )}

      {matches.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-700 p-12 text-center">
          <p className="text-slate-300 font-medium">No strong matches yet</p>
          <p className="mt-2 text-sm text-slate-400">
            We only surface collaborators with high semantic similarity (typically 72%+).
            Projects in unrelated domains — e.g. cooking vs. legal tech — are intentionally hidden.
          </p>
          <p className="mt-4 text-sm text-slate-500">
            Demo: log in as <span className="text-slate-300">emma@demo.com</span> for justice/social
            impact matches, or <span className="text-slate-300">alice@demo.com</span> for food/ML
            matches.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {matches.map((match) => (
            <div
              key={match.project.id}
              className="rounded-2xl border border-slate-800 bg-surface-800/60 p-5"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-white">{match.project.title}</h3>
                    <span className="rounded-full bg-brand-600/20 px-2.5 py-0.5 text-xs font-medium text-brand-300">
                      {(match.similarity * 100).toFixed(1)}% match
                    </span>
                  </div>
                  <p className="mt-1 text-sm text-slate-500">by @{match.owner_username}</p>
                  <p className="mt-3 text-sm leading-relaxed text-slate-400">
                    {match.project.description}
                  </p>
                  {match.project.skills_needed && (
                    <p className="mt-2 text-xs text-brand-300">
                      Skills: {match.project.skills_needed}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => handleConnect(match.project.id)}
                  disabled={requesting === match.project.id}
                  className="shrink-0 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-500 disabled:opacity-50"
                >
                  {requesting === match.project.id ? "Sending..." : "Connect"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
