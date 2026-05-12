"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Building2, Car, Gauge, Radio, Users } from "lucide-react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { alertTypeLabel, formatDateTime } from "@/lib/format";
import { supabase } from "@/lib/supabase";
import type { Alert, MonitoringSession } from "@/types/database";

type Counts = {
  companies: number;
  drivers: number;
  vehicles: number;
  sessions: number;
  runningSessions: number;
  alertsToday: number;
};

export default function DashboardPage() {
  const [counts, setCounts] = useState<Counts>({
    companies: 0,
    drivers: 0,
    vehicles: 0,
    sessions: 0,
    runningSessions: 0,
    alertsToday: 0,
  });
  const [runningSessions, setRunningSessions] = useState<MonitoringSession[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  async function loadDashboard() {
    setLoading(true);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const [
      companies,
      drivers,
      vehicles,
      sessions,
      running,
      alertsToday,
      runningRows,
      alertRows,
    ] = await Promise.all([
      supabase.from("companies").select("id", { count: "exact", head: true }),
      supabase.from("profiles").select("id", { count: "exact", head: true }).eq("role", "DRIVER"),
      supabase.from("vehicles").select("id", { count: "exact", head: true }),
      supabase.from("monitoring_sessions").select("id", { count: "exact", head: true }),
      supabase.from("monitoring_sessions").select("id", { count: "exact", head: true }).eq("status", "running"),
      supabase.from("alerts").select("id", { count: "exact", head: true }).gte("triggered_at", today.toISOString()),
      supabase
        .from("monitoring_sessions")
        .select("*")
        .eq("status", "running")
        .order("started_at", { ascending: false })
        .limit(6),
      supabase
        .from("alerts")
        .select("*")
        .order("triggered_at", { ascending: false })
        .limit(6),
    ]);

    setCounts({
      companies: companies.count ?? 0,
      drivers: drivers.count ?? 0,
      vehicles: vehicles.count ?? 0,
      sessions: sessions.count ?? 0,
      runningSessions: running.count ?? 0,
      alertsToday: alertsToday.count ?? 0,
    });
    setRunningSessions(runningRows.data ?? []);
    setRecentAlerts(alertRows.data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadDashboard();
    }, 0);

    const channel = supabase
      .channel("dashboard-live")
      .on("postgres_changes", { event: "*", schema: "public", table: "monitoring_sessions" }, () => {
        void loadDashboard();
      })
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "alerts" }, () => {
        void loadDashboard();
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
        title="Dashboard"
        description="Theo dõi phiên giám sát, cảnh báo và dữ liệu vận hành từ desktop app."
        action={<Badge tone="green"><Radio className="mr-1 h-3.5 w-3.5" />Realtime</Badge>}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard title="Hãng xe" value={counts.companies} icon={Building2} helper="Đơn vị dịch vụ trong hệ thống" />
        <StatCard title="Tài xế" value={counts.drivers} icon={Users} tone="green" helper="Tài khoản DRIVER đang quản lý" />
        <StatCard title="Xe" value={counts.vehicles} icon={Car} helper="Tổng xe có trong hệ thống" />
        <StatCard title="Phiên giám sát" value={counts.sessions} icon={Gauge} helper="Tổng phiên đã ghi nhận" />
        <StatCard title="Đang hoạt động" value={counts.runningSessions} icon={Radio} tone="green" helper="Phiên đang chạy realtime" />
        <StatCard title="Cảnh báo hôm nay" value={counts.alertsToday} icon={AlertTriangle} tone="red" helper="Cảnh báo từ 00:00 hôm nay" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section>
          <h3 className="mb-3 text-base font-black text-slate-950">Phiên đang chạy</h3>
          <DataTable columns={["Mã phiên", "Tài xế", "Bắt đầu", "Trạng thái"]}>
            {loading ? (
              <EmptyRow colSpan={4} text="Đang tải..." />
            ) : runningSessions.length ? (
              runningSessions.map((session) => (
                <tr key={session.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm font-semibold text-slate-700">{session.id.slice(0, 8)}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{session.user_id.slice(0, 8)}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.started_at)}</td>
                  <td className="px-4 py-3"><StatusBadge status={session.status} /></td>
                </tr>
              ))
            ) : (
              <EmptyRow colSpan={4} text="Chưa có phiên đang chạy." />
            )}
          </DataTable>
        </section>

        <section>
          <h3 className="mb-3 text-base font-black text-slate-950">Cảnh báo gần đây</h3>
          <DataTable columns={["Thời gian", "Loại", "Rủi ro", "Tài xế"]}>
            {loading ? (
              <EmptyRow colSpan={4} text="Đang tải..." />
            ) : recentAlerts.length ? (
              recentAlerts.map((alert) => (
                <tr key={alert.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(alert.triggered_at)}</td>
                  <td className="px-4 py-3 text-sm font-semibold text-slate-800">{alertTypeLabel(alert.alert_type)}</td>
                  <td className="px-4 py-3"><StatusBadge status={alert.risk_level} /></td>
                  <td className="px-4 py-3 text-sm text-slate-600">{alert.user_id.slice(0, 8)}</td>
                </tr>
              ))
            ) : (
              <EmptyRow colSpan={4} text="Chưa có cảnh báo." />
            )}
          </DataTable>
        </section>
      </div>
    </AdminShell>
  );
}
