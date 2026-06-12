export function ErrorBanner({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-xl border border-rose-500/30 bg-rose-900/20 p-4">
      <p className="text-sm text-rose-200">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 text-sm font-medium text-rose-300 underline hover:text-rose-100"
        >
          Try again
        </button>
      )}
    </div>
  );
}
