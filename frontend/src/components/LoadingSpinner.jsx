export default function LoadingSpinner({ label = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-3" role="status" aria-live="polite">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-fuchsia-300 border-t-transparent" />
      <span className="text-sm text-slate-300">{label}</span>
    </div>
  );
}
