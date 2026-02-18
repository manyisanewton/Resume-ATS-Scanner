export default function AuthSkeleton() {
  return (
    <div className="mx-auto w-full max-w-5xl overflow-hidden rounded-3xl border border-fuchsia-500/50 bg-slate-950/70 shadow-[0_0_30px_rgba(168,85,247,0.35)]">
      <div className="grid min-h-[560px] grid-cols-1 md:grid-cols-[1fr_1.25fr]">
        <div className="space-y-4 p-8 md:p-12">
          <div className="h-5 w-40 animate-pulse rounded bg-fuchsia-500/40" />
          <div className="h-10 w-56 animate-pulse rounded bg-fuchsia-500/30" />
          <div className="h-4 w-64 animate-pulse rounded bg-slate-700" />
          <div className="h-4 w-44 animate-pulse rounded bg-slate-700" />
        </div>
        <div className="space-y-5 p-8 md:p-12">
          <div className="h-10 w-32 animate-pulse rounded bg-slate-700" />
          <div className="h-12 w-full animate-pulse rounded-xl bg-slate-800" />
          <div className="h-12 w-full animate-pulse rounded-xl bg-slate-800" />
          <div className="h-12 w-full animate-pulse rounded-xl bg-slate-800" />
          <div className="h-11 w-full animate-pulse rounded-full bg-fuchsia-500/40" />
        </div>
      </div>
    </div>
  );
}
