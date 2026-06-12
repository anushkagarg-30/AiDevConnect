import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import { ErrorBanner } from "../components/ErrorBanner";
import { MatchCard } from "../components/MatchCard";
import { useAuth } from "../context/AuthContext";
import type { MatchRequest } from "../types";

type Tab = "received" | "sent";

export function Matches() {
  const { token } = useAuth();
  const [tab, setTab] = useState<Tab>("received");
  const [sent, setSent] = useState<MatchRequest[]>([]);
  const [received, setReceived] = useState<MatchRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState(false);

  const loadMatches = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError("");
    try {
      const [sentList, receivedList] = await Promise.all([
        api.listSentMatches(token),
        api.listReceivedMatches(token),
      ]);
      setSent(sentList);
      setReceived(receivedList);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load matches");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  async function handleAccept(id: number) {
    if (!token) return;
    setActionLoading(true);
    setError("");
    try {
      await api.acceptMatch(token, id);
      await loadMatches();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to accept match");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleReject(id: number) {
    if (!token) return;
    setActionLoading(true);
    setError("");
    try {
      await api.rejectMatch(token, id);
      await loadMatches();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to decline match");
    } finally {
      setActionLoading(false);
    }
  }

  const items = tab === "received" ? received : sent;

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  if (error && !loading && sent.length === 0 && received.length === 0) {
    return <ErrorBanner message={error} onRetry={loadMatches} />;
  }

  return (
    <div>
      {error && (
        <div className="mb-4">
          <ErrorBanner message={error} />
        </div>
      )}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Match requests</h1>
        <p className="mt-2 text-slate-400">
          Manage collaboration requests. Accept or decline in real time.
        </p>
      </div>

      <div className="mb-6 flex gap-2">
        <TabButton
          active={tab === "received"}
          onClick={() => setTab("received")}
          label={`Received (${received.length})`}
        />
        <TabButton
          active={tab === "sent"}
          onClick={() => setTab("sent")}
          label={`Sent (${sent.length})`}
        />
      </div>

      {items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-700 p-12 text-center">
          <p className="text-slate-400">
            {tab === "received"
              ? "No match requests received yet."
              : "You haven't sent any match requests yet."}
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {items.map((match) => (
            <MatchCard
              key={match.id}
              match={match}
              variant={tab}
              onAccept={tab === "received" ? handleAccept : undefined}
              onReject={tab === "received" ? handleReject : undefined}
              loading={actionLoading}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TabButton({
  active,
  onClick,
  label,
}: {
  active: boolean;
  onClick: () => void;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
        active
          ? "bg-brand-600 text-white"
          : "border border-slate-700 text-slate-400 hover:border-slate-500"
      }`}
    >
      {label}
    </button>
  );
}
