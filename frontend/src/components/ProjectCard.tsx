import { Link } from "react-router-dom";
import type { Project } from "../types";

export function ProjectCard({ project }: { project: Project }) {
  return (
    <div className="group rounded-2xl border border-slate-800 bg-surface-800/60 p-5 transition hover:border-brand-500/40 hover:bg-surface-800">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <h3 className="truncate text-lg font-semibold text-white">{project.title}</h3>
          <p className="mt-2 line-clamp-3 text-sm leading-relaxed text-slate-400">
            {project.description}
          </p>
          {project.skills_needed && (
            <p className="mt-3 text-xs text-brand-300">
              Skills: {project.skills_needed}
            </p>
          )}
        </div>
      </div>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          {new Date(project.created_at).toLocaleDateString()}
        </span>
        <Link
          to={`/projects/${project.id}/matches`}
          className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-brand-500"
        >
          Find matches
        </Link>
      </div>
    </div>
  );
}
