import { RetroGrid } from "@/components/ui/retro-grid";
import ResultClient from "./ResultClient";

export default async function Page({ params }: { params: { rid: string } }) {
  const param = await params;
  const jobId = param.rid;
  return (
    <div className="relative min-h-screen w-full bg-linear-to-br from-green-50 via-emerald-50 to-teal-50 dark:from-slate-950 dark:via-slate-900 dark:to-green-950">
      <div className="fixed inset-0 z-0">
        <RetroGrid className="opacity-30" />
      </div>

      {/* ResultClient will handle data fetching */}
      <ResultClient rid={jobId} />
    </div>
  );
}
