import type { MatchRequest } from "../types";

const statusStyles: Record<MatchRequest["status"], string> = {
  pending: "bg-amber-500/20 text-amber-300",
  accepted: "bg-emerald-500/20 text-emerald-300",
  rejected: "bg-rose-500/20 text-rose-300",
};

interface MatchCardProps {
  match: MatchRequest;
  variant: "sent" | "received";
  onAccept?: (id: number) => void;
  onReject?: (id: number) => void;
  loading?: boolean;
}

export function MatchCard({ match, variant, onAccept, onReject, loading }: MatchCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-surface-800/60 p-5">
      <div className="flex flex-wrap items-center gap-2">
        <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${statusStyles[match.status]}`}>
          {match.status}
        </span>
        <span className="text-xs text-slate-500">
          {new Date(match.created_at).toLocaleString()}
        </span>
      </div>

      <h3 className="mt-3 text-lg font-semibold text-white">{match.project.title}</h3>
      <p className="mt-1 text-sm text-slate-400">{match.project.description}</p>

      <div className="mt-4 space-y-1 text-sm text-slate-400">
        <p>
          <span className="text-slate-500">From:</span> @{match.requester_username}
        </p>
        <p>
          <span className="text-slate-500">To:</span> @{match.recipient_username}
        </p>
        {match.requester_project && (
          <p>
            <span className="text-slate-500">Their project:</span> {match.requester_project.title}
          </p>
        )}
      </div>

      {variant === "received" && match.status === "pending" && onAccept && onReject && (
        <div className="mt-4 flex gap-2">
          <button
            disabled={loading}
            onClick={() => onAccept(match.id)}
            className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:opacity-50"
          >
            Accept
          </button>
          <button
            disabled={loading}
            onClick={() => onReject(match.id)}
            className="rounded-lg border border-slate-600 px-4 py-2 text-sm font-medium text-slate-300 transition hover:border-slate-500 disabled:opacity-50"
          >
            Decline
          </button>
        </div>
      )}
    </div>
  );
}
