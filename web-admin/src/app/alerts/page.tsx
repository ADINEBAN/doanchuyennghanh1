"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { alertTypeLabel, formatDateTime } from "@/lib/format";
import { supabase } from "@/lib/supabase";
import type { Alert } from "@/types/database";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadAlerts() {
    const { data } = await supabase
      .from("alerts")
      .select("*")
      .order("triggered_at", { ascending: false })
      .limit(150);
    setAlerts(data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadAlerts();
    }, 0);
    const channel = supabase
      .channel("alerts-page")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "alerts" }, () => {
        void loadAlerts();
      })
      .subscribe();

    return () => {
      window.clearTimeout(timer);
      void supabase.removeChannel(channel);
    };
  }, []);

  return (
    <AdminShell>
      <PageHeader
        title="Lịch sử cảnh báo"
        description="Cảnh báo realtime từ desktop app: mắt nhắm, ngáp, buồn ngủ, mất tập trung."
      />
      <DataTable columns={["Thời gian", "Tài xế", "Loại", "Rủi ro", "EAR", "MAR", "Yaw", "Pitch"]}>
        {loading ? (
          <EmptyRow colSpan={8} text="Đang tải cảnh báo..." />
        ) : alerts.length ? (
          alerts.map((alert) => (
            <tr key={alert.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(alert.triggered_at)}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{alert.user_id.slice(0, 8)}</td>
              <td className="px-4 py-3 text-sm font-bold text-slate-800">{alertTypeLabel(alert.alert_type)}</td>
              <td className="px-4 py-3"><StatusBadge status={alert.risk_level} /></td>
              <td className="px-4 py-3 text-sm text-slate-600">{alert.ear_value?.toFixed(3) ?? "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{alert.mar_value?.toFixed(3) ?? "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{alert.head_yaw?.toFixed(1) ?? "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{alert.head_pitch?.toFixed(1) ?? "-"}</td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={8} text="Chưa có cảnh báo." />
        )}
      </DataTable>
    </AdminShell>
  );
}
