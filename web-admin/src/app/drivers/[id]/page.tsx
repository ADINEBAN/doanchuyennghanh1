"use client";

import Link from "next/link";
import { use, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, ArrowLeft, Car, Clock, Radio, User } from "lucide-react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatusBadge } from "@/components/ui/Badge";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatCard } from "@/components/ui/StatCard";
import { useAuth } from "@/contexts/AuthContext";
import { alertTypeLabel, formatDateTime, formatDuration } from "@/lib/format";
import { getDriverPresence, LIVE_STATUS_POLL_MS } from "@/lib/live-status";
import { supabase } from "@/lib/supabase";
import { useCachedState } from "@/hooks/useCachedState";
import type { Alert, DriverLiveStatus, MonitoringSession, Profile, Vehicle } from "@/types/database";

type DriverDetailParams = {
  params: Promise<{ id: string }>;
};

export default function DriverDetailPage({ params }: DriverDetailParams) {
  const { id } = use(params);
  const { profile } = useAuth();
  const cacheScope = `${profile?.id ?? "guest"}:${id}`;
  const [driver, setDriver, hadDriver] = useCachedState<Profile | null>(`web-admin:${cacheScope}:driver-detail:driver`, null);
  const [vehicle, setVehicle, hadVehicle] = useCachedState<Vehicle | null>(`web-admin:${cacheScope}:driver-detail:vehicle`, null);
  const [live, setLive, hadLive] = useCachedState<DriverLiveStatus | null>(`web-admin:${cacheScope}:driver-detail:live`, null);
  const [sessions, setSessions, hadSessions] = useCachedState<MonitoringSession[]>(`web-admin:${cacheScope}:driver-detail:sessions`, []);
  const [alerts, setAlerts, hadAlerts] = useCachedState<Alert[]>(`web-admin:${cacheScope}:driver-detail:alerts`, []);
  const [currentTime, setCurrentTime] = useState(() => Date.now());
  const [loading, setLoading] = useState(!(hadDriver || hadVehicle || hadLive || hadSessions || hadAlerts));
  const isLoadingRef = useRef(false);

  const loadDriver = useCallback(async () => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;

    try {
      let driverQuery = supabase.from("profiles").select("*").eq("id", id).eq("role", "DRIVER");
      let vehicleQuery = supabase.from("vehicles").select("*").eq("assigned_driver_id", id);
      let liveQuery = supabase.from("driver_live_status").select("*").eq("driver_id", id);
      let sessionsQuery = supabase
        .from("monitoring_sessions")
        .select("*")
        .eq("user_id", id)
        .order("started_at", { ascending: false })
        .limit(20);
      let alertsQuery = supabase
        .from("alerts")
        .select("*")
        .eq("user_id", id)
        .order("triggered_at", { ascending: false })
        .limit(50);

      if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
        driverQuery = driverQuery.eq("company_id", profile.company_id);
        vehicleQuery = vehicleQuery.eq("company_id", profile.company_id);
        liveQuery = liveQuery.eq("company_id", profile.company_id);
        sessionsQuery = sessionsQuery.eq("company_id", profile.company_id);
        alertsQuery = alertsQuery.eq("company_id", profile.company_id);
      }

      const [driverRows, vehicleRows, liveRows, sessionRows, alertRows] = await Promise.all([
        driverQuery.maybeSingle(),
        vehicleQuery.maybeSingle(),
        liveQuery.maybeSingle(),
        sessionsQuery,
        alertsQuery,
      ]);

      setDriver(driverRows.data ?? null);
      setVehicle(vehicleRows.data ?? null);
      setLive(liveRows.data ?? null);
      setSessions(sessionRows.data ?? []);
      setAlerts(alertRows.data ?? []);
      setCurrentTime(Date.now());
    } finally {
      isLoadingRef.current = false;
      setLoading(false);
    }
  }, [id, profile, setAlerts, setDriver, setLive, setSessions, setVehicle]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadDriver();
    }, 0);
    const clock = window.setInterval(() => {
      setCurrentTime(Date.now());
      void loadDriver();
    }, LIVE_STATUS_POLL_MS);
    const channel = supabase
      .channel(`driver-detail-${id}`)
      .on("postgres_changes", { event: "*", schema: "public", table: "driver_live_status", filter: `driver_id=eq.${id}` }, () => {
        void loadDriver();
      })
      .on("postgres_changes", { event: "*", schema: "public", table: "monitoring_sessions", filter: `user_id=eq.${id}` }, () => {
        void loadDriver();
      })
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "alerts", filter: `user_id=eq.${id}` }, () => {
        void loadDriver();
      })
      .subscribe();

    return () => {
      window.clearTimeout(timer);
      window.clearInterval(clock);
      void supabase.removeChannel(channel);
    };
  }, [id, loadDriver]);

  const presence = getDriverPresence(live, currentTime);
  const totalDuration = useMemo(() => {
    return sessions.reduce((sum, session) => sum + (session.duration_seconds ?? 0), 0);
  }, [sessions]);
  const dangerAlerts = alerts.filter((alert) => alert.risk_level === "high" || alert.risk_level === "danger").length;

  if (!loading && !driver) {
    return (
      <AdminShell>
        <PageHeader
          title="Không tìm thấy tài xế"
          description="Tài khoản không tồn tại hoặc nằm ngoài phạm vi quản lý của bạn."
          action={
            <Link href="/drivers" className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50">
              <ArrowLeft className="h-4 w-4" />
              Quay lại
            </Link>
          }
        />
      </AdminShell>
    );
  }

  return (
    <AdminShell>
      <PageHeader
        title={driver?.full_name || driver?.email || "Chi tiết tài xế"}
        description="Thông tin cá nhân, xe được gán, trạng thái realtime, phiên giám sát và cảnh báo cá nhân."
        action={
          <Link href="/drivers" className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50">
            <ArrowLeft className="h-4 w-4" />
            Quay lại
          </Link>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard title="Trạng thái app" value={presence.label} icon={Radio} tone={presence.monitoring || presence.online ? "green" : "amber"} />
        <StatCard title="Số phiên" value={sessions.length} icon={Clock} helper="Các phiên gần nhất" />
        <StatCard title="Cảnh báo" value={alerts.length} icon={AlertTriangle} tone={alerts.length ? "red" : "blue"} />
        <StatCard title="Cảnh báo cao" value={dangerAlerts} icon={AlertTriangle} tone="red" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <User className="h-5 w-5 text-blue-700" />
            <h3 className="text-base font-black text-slate-950">Thông tin cá nhân</h3>
          </div>
          <dl className="grid gap-3 text-sm">
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Họ tên</dt><dd className="font-bold text-slate-900">{driver?.full_name || "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Email</dt><dd className="font-bold text-slate-900">{driver?.email || "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Điện thoại</dt><dd className="font-bold text-slate-900">{driver?.phone || "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Tài khoản</dt><dd><StatusBadge status={driver?.status} /></dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Đăng nhập cuối</dt><dd className="font-bold text-slate-900">{formatDateTime(driver?.last_login_at)}</dd></div>
          </dl>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Car className="h-5 w-5 text-blue-700" />
            <h3 className="text-base font-black text-slate-950">Xe được gán</h3>
          </div>
          <dl className="grid gap-3 text-sm">
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Biển số</dt><dd className="font-bold text-slate-900">{vehicle?.license_plate || "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Hãng xe</dt><dd className="font-bold text-slate-900">{vehicle?.brand || "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Dòng xe</dt><dd className="font-bold text-slate-900">{vehicle?.model || "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Trạng thái</dt><dd>{vehicle ? <StatusBadge status={vehicle.status} /> : "-"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-slate-500">Cập nhật realtime</dt><dd className="font-bold text-slate-900">{formatDateTime(live?.last_seen_at)}</dd></div>
          </dl>
        </section>
      </div>

      <section className="mt-6">
        <h3 className="mb-3 text-base font-black text-slate-950">Phiên giám sát gần đây</h3>
        <DataTable columns={["Phiên", "Bắt đầu", "Kết thúc", "Thời lượng", "Cảnh báo", "Trạng thái"]}>
          {loading ? (
            <EmptyRow colSpan={6} text="Đang tải phiên..." />
          ) : sessions.length ? (
            sessions.map((session) => (
              <tr key={session.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-bold text-slate-800">{session.id.slice(0, 8)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.started_at)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.ended_at)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{formatDuration(session.duration_seconds)}</td>
                <td className="px-4 py-3 text-sm font-bold text-slate-800">{session.total_alerts ?? 0}</td>
                <td className="px-4 py-3"><StatusBadge status={session.status} /></td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={6} text="Chưa có phiên giám sát." />
          )}
        </DataTable>
      </section>

      <section className="mt-6">
        <h3 className="mb-3 text-base font-black text-slate-950">Cảnh báo cá nhân</h3>
        <DataTable columns={["Thời gian", "Loại", "Rủi ro", "EAR", "MAR", "Yaw", "Pitch"]}>
          {loading ? (
            <EmptyRow colSpan={7} text="Đang tải cảnh báo..." />
          ) : alerts.length ? (
            alerts.map((alert) => (
              <tr key={alert.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(alert.triggered_at)}</td>
                <td className="px-4 py-3 text-sm font-bold text-slate-800">{alertTypeLabel(alert.alert_type)}</td>
                <td className="px-4 py-3"><StatusBadge status={alert.risk_level} /></td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.ear_value?.toFixed(3) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.mar_value?.toFixed(3) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.head_yaw?.toFixed(1) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.head_pitch?.toFixed(1) ?? "-"}</td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={7} text="Chưa có cảnh báo." />
          )}
        </DataTable>
      </section>

      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <div className="text-sm font-bold text-slate-700">Tổng thời lượng giám sát</div>
        <div className="mt-1 text-2xl font-black text-slate-950">{formatDuration(totalDuration)}</div>
      </div>
    </AdminShell>
  );
}
