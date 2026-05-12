import type { RiskLevel, SessionStatus, UserStatus, VehicleStatus } from "@/types/database";
import { statusLabel } from "@/lib/format";

type BadgeTone = "blue" | "green" | "amber" | "red" | "slate";

const toneClasses: Record<BadgeTone, string> = {
  blue: "bg-blue-50 text-blue-700 ring-blue-200",
  green: "bg-emerald-50 text-emerald-700 ring-emerald-200",
  amber: "bg-amber-50 text-amber-700 ring-amber-200",
  red: "bg-rose-50 text-rose-700 ring-rose-200",
  slate: "bg-slate-100 text-slate-700 ring-slate-200",
};

export function Badge({ children, tone = "slate" }: { children: React.ReactNode; tone?: BadgeTone }) {
  return (
    <span className={`inline-flex items-center rounded-md px-2.5 py-1 text-xs font-semibold ring-1 ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}

export function StatusBadge({
  status,
}: {
  status: UserStatus | VehicleStatus | SessionStatus | RiskLevel | string | null | undefined;
}) {
  const tone =
    status === "active" || status === "running" || status === "available"
      ? "green"
      : status === "assigned" || status === "medium"
        ? "blue"
        : status === "high" || status === "danger" || status === "locked"
          ? "red"
          : status === "maintenance"
            ? "amber"
            : "slate";
  return <Badge tone={tone}>{statusLabel(status)}</Badge>;
}
