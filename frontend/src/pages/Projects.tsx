import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError } from "../api/client";
import { ErrorBanner } from "../components/ErrorBanner";
import { ProjectCard } from "../components/ProjectCard";
import { useAuth } from "../context/AuthContext";
import type { Project } from "../types";

export function Projects() {
  const { token } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [skillsNeeded, setSkillsNeeded] = useState("");
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function loadProjects() {
    if (!token) return;
    setLoadError("");
    try {
      const data = await api.listProjects(token);
      setProjects(data);
    } catch (err) {
      setLoadError(err instanceof ApiError ? err.message : "Failed to load projects");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProjects();
  }, [token]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError("");
    setSubmitting(true);
    try {
      await api.createProject(token, {
        title,
        description,
        skills_needed: skillsNeeded || undefined,
      });
      setTitle("");
      setDescription("");
      setSkillsNeeded("");
      setShowForm(false);
      await loadProjects();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create project");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(projectId: number) {
    if (!token || !confirm("Delete this project?")) return;
    try {
      await api.deleteProject(token, projectId);
      await loadProjects();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to delete project");
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  if (loadError) {
    return <ErrorBanner message={loadError} onRetry={loadProjects} />;
  }

  return (
    <div>
      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Your projects</h1>
          <p className="mt-2 text-slate-400">
            Each project gets a 1536-dim embedding for semantic matching.
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500"
        >
          {showForm ? "Cancel" : "+ New project"}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="mb-8 rounded-2xl border border-slate-800 bg-surface-800/50 p-6"
        >
          {error && (
            <div className="mb-4 rounded-lg border border-rose-500/30 bg-rose-900/20 px-3 py-2 text-sm text-rose-300">
              {error}
            </div>
          )}

          <label className="block text-sm font-medium text-slate-300">
            Title
            <input
              required
              minLength={3}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="AI-powered recipe generator"
              className="mt-1 w-full rounded-lg border border-slate-700 bg-surface-900 px-3 py-2 text-white outline-none focus:border-brand-500"
            />
          </label>

          <label className="mt-4 block text-sm font-medium text-slate-300">
            Description
            <textarea
              required
              minLength={10}
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe your project idea, goals, and what you're building..."
              className="mt-1 w-full rounded-lg border border-slate-700 bg-surface-900 px-3 py-2 text-white outline-none focus:border-brand-500"
            />
          </label>

          <label className="mt-4 block text-sm font-medium text-slate-300">
            Skills needed (optional)
            <input
              value={skillsNeeded}
              onChange={(e) => setSkillsNeeded(e.target.value)}
              placeholder="React, Python, ML"
              className="mt-1 w-full rounded-lg border border-slate-700 bg-surface-900 px-3 py-2 text-white outline-none focus:border-brand-500"
            />
          </label>

          <button
            type="submit"
            disabled={submitting}
            className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50"
          >
            {submitting ? "Creating..." : "Submit project"}
          </button>
        </form>
      )}

      {projects.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-700 p-12 text-center">
          <p className="text-slate-400">No projects yet. Create one to start finding matches.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {projects.map((project) => (
            <div key={project.id} className="relative">
              <ProjectCard project={project} />
              <button
                onClick={() => handleDelete(project.id)}
                className="absolute top-4 right-4 text-xs text-slate-500 transition hover:text-rose-400"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
