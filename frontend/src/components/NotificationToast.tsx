import type { Notification } from "../types";

const styles: Record<Notification["type"], string> = {
  connected: "border-slate-600 bg-slate-800",
  match_request: "border-brand-500/50 bg-brand-900/40",
  match_accepted: "border-emerald-500/50 bg-emerald-900/30",
  match_rejected: "border-rose-500/50 bg-rose-900/30",
};

export function NotificationToast({
  notification,
  onDismiss,
}: {
  notification: Notification;
  onDismiss: () => void;
}) {
  return (
    <div
      className={`animate-in slide-in-from-right rounded-xl border p-4 shadow-xl backdrop-blur-sm ${styles[notification.type] ?? styles.connected}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-white">{notification.title}</p>
          <p className="mt-1 text-sm text-slate-300">{notification.message}</p>
        </div>
        <button
          onClick={onDismiss}
          className="shrink-0 text-slate-400 transition hover:text-white"
          aria-label="Dismiss"
        >
          ✕
        </button>
      </div>
    </div>
  );
}
