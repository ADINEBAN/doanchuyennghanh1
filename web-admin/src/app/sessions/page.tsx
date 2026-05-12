"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { formatDateTime, formatDuration } from "@/lib/format";
import { supabase } from "@/lib/supabase";
import type { MonitoringSession } from "@/types/database";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<MonitoringSession[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadSessions() {
    const { data } = await supabase
      .from("monitoring_sessions")
      .select("*")
      .order("started_at", { ascending: false })
      .limit(100);
    setSessions(data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadSessions();
    }, 0);
    const channel = supabase
      .channel("sessions-page")
      .on("postgres_changes", { event: "*", schema: "public", table: "monitoring_sessions" }, () => {
        void loadSessions();
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
        title="Phiên giám sát"
        description="Theo dõi phiên desktop app đang chạy, đã dừng hoặc bị gián đoạn."
      />
      <DataTable columns={["Mã phiên", "Tài xế", "Bắt đầu", "Kết thúc", "Thời lượng", "Cảnh báo", "Trạng thái"]}>
        {loading ? (
          <EmptyRow colSpan={7} text="Đang tải phiên giám sát..." />
        ) : sessions.length ? (
          sessions.map((session) => (
            <tr key={session.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm font-bold text-slate-800">{session.id.slice(0, 8)}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{session.user_id.slice(0, 8)}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.started_at)}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.ended_at)}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{formatDuration(session.duration_seconds)}</td>
              <td className="px-4 py-3 text-sm font-bold text-slate-800">{session.total_alerts ?? 0}</td>
              <td className="px-4 py-3"><StatusBadge status={session.status} /></td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={7} text="Chưa có phiên giám sát." />
        )}
      </DataTable>
    </AdminShell>
  );
}
