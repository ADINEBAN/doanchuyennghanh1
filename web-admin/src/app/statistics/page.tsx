"use client";

import { useEffect, useMemo, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatCard } from "@/components/ui/StatCard";
import { AlertTriangle, BarChart3, ShieldAlert } from "lucide-react";
import { alertTypeLabel } from "@/lib/format";
import { supabase } from "@/lib/supabase";
import type { Alert } from "@/types/database";

export default function StatisticsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAlerts() {
      const { data } = await supabase
        .from("alerts")
        .select("*")
        .order("triggered_at", { ascending: false })
        .limit(500);
      setAlerts(data ?? []);
      setLoading(false);
    }
    void loadAlerts();
  }, []);

  const byType = useMemo(() => {
    return alerts.reduce<Record<string, number>>((acc, alert) => {
      acc[alert.alert_type] = (acc[alert.alert_type] ?? 0) + 1;
      return acc;
    }, {});
  }, [alerts]);

  const byRisk = useMemo(() => {
    return alerts.reduce<Record<string, number>>((acc, alert) => {
      acc[alert.risk_level] = (acc[alert.risk_level] ?? 0) + 1;
      return acc;
    }, {});
  }, [alerts]);

  const dangerCount = alerts.filter((alert) => alert.risk_level === "danger" || alert.risk_level === "high").length;

  return (
    <AdminShell>
      <PageHeader title="Thống kê" description="Tổng hợp cảnh báo và mức độ rủi ro từ dữ liệu Supabase." />
      <div className="grid gap-4 md:grid-cols-3">
        <StatCard title="Tổng cảnh báo" value={alerts.length} icon={AlertTriangle} />
        <StatCard title="Cảnh báo cao/nguy hiểm" value={dangerCount} icon={ShieldAlert} tone="red" />
        <StatCard title="Loại cảnh báo" value={Object.keys(byType).length} icon={BarChart3} tone="green" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section>
          <h3 className="mb-3 text-base font-black text-slate-950">Theo loại cảnh báo</h3>
          <DataTable columns={["Loại", "Số lượng"]}>
            {loading ? (
              <EmptyRow colSpan={2} text="Đang tải thống kê..." />
            ) : Object.keys(byType).length ? (
              Object.entries(byType).map(([type, count]) => (
                <tr key={type}>
                  <td className="px-4 py-3 text-sm font-bold text-slate-800">{alertTypeLabel(type)}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{count}</td>
                </tr>
              ))
            ) : (
              <EmptyRow colSpan={2} text="Chưa có dữ liệu." />
            )}
          </DataTable>
        </section>

        <section>
          <h3 className="mb-3 text-base font-black text-slate-950">Theo mức rủi ro</h3>
          <DataTable columns={["Mức rủi ro", "Số lượng"]}>
            {loading ? (
              <EmptyRow colSpan={2} text="Đang tải thống kê..." />
            ) : Object.keys(byRisk).length ? (
              Object.entries(byRisk).map(([risk, count]) => (
                <tr key={risk}>
                  <td className="px-4 py-3 text-sm font-bold text-slate-800">{risk}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{count}</td>
                </tr>
              ))
            ) : (
              <EmptyRow colSpan={2} text="Chưa có dữ liệu." />
            )}
          </DataTable>
        </section>
      </div>
    </AdminShell>
  );
}
