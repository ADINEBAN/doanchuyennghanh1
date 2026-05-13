"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AlertTriangle, Car, Radio, UserCheck, UserX, Users } from "lucide-react";
import Link from "next/link";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { useAuth } from "@/contexts/AuthContext";
import { alertTypeLabel, formatDateTime } from "@/lib/format";
import { getDriverPresence, LIVE_STATUS_POLL_MS } from "@/lib/live-status";
import { supabase } from "@/lib/supabase";
import { useCachedState } from "@/hooks/useCachedState";
import type { Alert, DriverLiveStatus, MonitoringSession, Profile, Vehicle } from "@/types/database";

type Counts = {
  drivers: number;
  vehicles: number;
  onlineDrivers: number;
  monitoringDrivers: number;
  offlineDrivers: number;
  alertsToday: number;
};

export default function DashboardPage() {
  const { profile } = useAuth();
  const cacheScope = profile?.id ?? "guest";
  const [drivers, setDrivers, hadDrivers] = useCachedState<Profile[]>(`web-admin:${cacheScope}:dashboard:drivers`, []);
  const [vehicles, setVehicles, hadVehicles] = useCachedState<Vehicle[]>(`web-admin:${cacheScope}:dashboard:vehicles`, []);
  const [liveStatuses, setLiveStatuses, hadLiveStatuses] = useCachedState<DriverLiveStatus[]>(`web-admin:${cacheScope}:dashboard:live-statuses`, []);
  const [runningSessions, setRunningSessions, hadRunningSessions] = useCachedState<MonitoringSession[]>(`web-admin:${cacheScope}:dashboard:running-sessions`, []);
  const [recentAlerts, setRecentAlerts, hadRecentAlerts] = useCachedState<Alert[]>(`web-admin:${cacheScope}:dashboard:recent-alerts`, []);
  const [currentTime, setCurrentTime] = useState(() => Date.now());
  const [loading, setLoading] = useState(
    !(hadDrivers || hadVehicles || hadLiveStatuses || hadRunningSessions || hadRecentAlerts),
  );
  const isLoadingRef = useRef(false);

  const loadDashboard = useCallback(async () => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;

    try {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      let driversQuery = supabase.from("profiles").select("*").eq("role", "DRIVER").order("full_name");
      let vehiclesQuery = supabase.from("vehicles").select("*").order("created_at", { ascending: false });
      let liveQuery = supabase.from("driver_live_status").select("*");
      let sessionsQuery = supabase
        .from("monitoring_sessions")
        .select("*")
        .eq("status", "running")
        .order("started_at", { ascending: false })
        .limit(8);
      let alertsQuery = supabase
        .from("alerts")
        .select("*")
        .order("triggered_at", { ascending: false })
        .limit(8);

      if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
        driversQuery = driversQuery.eq("company_id", profile.company_id);
        vehiclesQuery = vehiclesQuery.eq("company_id", profile.company_id);
        liveQuery = liveQuery.eq("company_id", profile.company_id);
        sessionsQuery = sessionsQuery.eq("company_id", profile.company_id);
        alertsQuery = alertsQuery.eq("company_id", profile.company_id);
      }

      const [driverRows, vehicleRows, liveRows, sessionRows, alertRows] = await Promise.all([
        driversQuery,
        vehiclesQuery,
        liveQuery,
        sessionsQuery,
        alertsQuery,
      ]);

      setDrivers(driverRows.data ?? []);
      setVehicles(vehicleRows.data ?? []);
      setLiveStatuses(liveRows.data ?? []);
      setRunningSessions(sessionRows.data ?? []);
      setRecentAlerts(alertRows.data ?? []);
      setCurrentTime(Date.now());
    } finally {
      isLoadingRef.current = false;
      setLoading(false);
    }
  }, [profile, setDrivers, setLiveStatuses, setRecentAlerts, setRunningSessions, setVehicles]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadDashboard();
    }, 0);
    const clock = window.setInterval(() => {
      setCurrentTime(Date.now());
      void loadDashboard();
    }, LIVE_STATUS_POLL_MS);
    const channel = supabase
      .channel("dashboard-live")
      .on("postgres_changes", { event: "*", schema: "public", table: "driver_live_status" }, () => {
        void loadDashboard();
      })
      .on("postgres_changes", { event: "*", schema: "public", table: "monitoring_sessions" }, () => {
        void loadDashboard();
      })
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "alerts" }, () => {
        void loadDashboard();
      })
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          void loadDashboard();
        }
      });

    return () => {
      window.clearTimeout(timer);
      window.clearInterval(clock);
      void supabase.removeChannel(channel);
    };
  }, [loadDashboard]);

  const driverMap = useMemo(() => new Map(drivers.map((driver) => [driver.id, driver])), [drivers]);
  const vehicleMap = useMemo(() => new Map(vehicles.map((vehicle) => [vehicle.id, vehicle])), [vehicles]);

  const counts = useMemo<Counts>(() => {
    const liveByDriver = new Map(liveStatuses.map((live) => [live.driver_id, live]));
    const onlineDrivers = drivers.filter((driver) => getDriverPresence(liveByDriver.get(driver.id), currentTime).online).length;
    const monitoringDrivers = drivers.filter((driver) => getDriverPresence(liveByDriver.get(driver.id), currentTime).monitoring).length;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return {
      drivers: drivers.length,
      vehicles: vehicles.length,
      onlineDrivers,
      monitoringDrivers,
      offlineDrivers: Math.max(drivers.length - onlineDrivers, 0),
      alertsToday: recentAlerts.filter((alert) => new Date(alert.triggered_at) >= today).length,
    };
  }, [currentTime, drivers, liveStatuses, recentAlerts, vehicles.length]);

  const activeLiveRows = useMemo(() => {
    return liveStatuses
      .filter((live) => getDriverPresence(live, currentTime).online)
      .sort((left, right) => new Date(right.last_seen_at).getTime() - new Date(left.last_seen_at).getTime())
      .slice(0, 8);
  }, [currentTime, liveStatuses]);

  return (
    <AdminShell>
      <PageHeader
        title="Dashboard realtime"
        description="Theo dõi tài xế online, phiên đang giám sát và cảnh báo mới nhất từ desktop app."
        action={<Badge tone="green"><Radio className="mr-1 h-3.5 w-3.5" />Realtime + fallback</Badge>}
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        <StatCard title="Tài xế" value={counts.drivers} icon={Users} helper="Tổng tài khoản DRIVER đang quản lý" />
        <StatCard title="Đang online" value={counts.onlineDrivers} icon={UserCheck} tone="green" helper="Có heartbeat hợp lệ từ desktop app" />
        <StatCard title="Đang giám sát" value={counts.monitoringDrivers} icon={Radio} tone="green" helper="Đang có phiên giám sát thật" />
        <StatCard title="Offline" value={counts.offlineDrivers} icon={UserX} tone="amber" helper="Không có heartbeat trong thời gian cho phép" />
        <StatCard title="Xe" value={counts.vehicles} icon={Car} helper="Tổng xe trong phạm vi quản lý" />
        <StatCard title="Cảnh báo mới nhất" value={recentAlerts.length} icon={AlertTriangle} tone="red" helper="Các cảnh báo gần đây nhất" />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <section>
          <h3 className="mb-3 text-base font-black text-slate-950">Tài xế đang online</h3>
          <DataTable columns={["Tài xế", "Trạng thái", "Rủi ro", "Xe", "Cập nhật"]}>
            {loading ? (
              <EmptyRow colSpan={5} text="Đang tải trạng thái realtime..." />
            ) : activeLiveRows.length ? (
              activeLiveRows.map((live) => {
                const driver = driverMap.get(live.driver_id);
                const vehicle = live.vehicle_id ? vehicleMap.get(live.vehicle_id) : null;
                const presence = getDriverPresence(live, currentTime);

                return (
                  <tr key={live.driver_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-black text-slate-900">
                      <Link href={`/drivers/${live.driver_id}`} className="text-blue-700 hover:text-blue-900 hover:underline">
                        {driver?.full_name || driver?.email || live.driver_id.slice(0, 8)}
                      </Link>
                    </td>
                    <td className="px-4 py-3 text-sm text-slate-600">{presence.label}</td>
                    <td className="px-4 py-3"><StatusBadge status={live.risk_level} /></td>
                    <td className="px-4 py-3 text-sm text-slate-600">{vehicle?.license_plate || "-"}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(live.last_seen_at)}</td>
                  </tr>
                );
              })
            ) : (
              <EmptyRow colSpan={5} text="Chưa có tài xế online." />
            )}
          </DataTable>
        </section>

        <section>
          <h3 className="mb-3 text-base font-black text-slate-950">Phiên đang chạy thật</h3>
          <DataTable columns={["Phiên", "Tài xế", "Xe", "Bắt đầu", "Trạng thái"]}>
            {loading ? (
              <EmptyRow colSpan={5} text="Đang tải phiên..." />
            ) : runningSessions.length ? (
              runningSessions.map((session) => {
                const driver = driverMap.get(session.user_id);
                const vehicle = session.vehicle_id ? vehicleMap.get(session.vehicle_id) : null;

                return (
                  <tr key={session.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-sm font-semibold text-slate-700">{session.id.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{driver?.full_name || driver?.email || session.user_id.slice(0, 8)}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{vehicle?.license_plate || "-"}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.started_at)}</td>
                    <td className="px-4 py-3"><StatusBadge status={session.status} /></td>
                  </tr>
                );
              })
            ) : (
              <EmptyRow colSpan={5} text="Chưa có phiên đang chạy." />
            )}
          </DataTable>
        </section>
      </div>

      <section className="mt-6">
        <h3 className="mb-3 text-base font-black text-slate-950">Cảnh báo mới nhất</h3>
        <DataTable columns={["Thời gian", "Tài xế", "Loại", "Rủi ro", "EAR", "MAR"]}>
          {loading ? (
            <EmptyRow colSpan={6} text="Đang tải cảnh báo..." />
          ) : recentAlerts.length ? (
            recentAlerts.map((alert) => {
              const driver = driverMap.get(alert.user_id);

              return (
                <tr key={alert.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(alert.triggered_at)}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{driver?.full_name || driver?.email || alert.user_id.slice(0, 8)}</td>
                  <td className="px-4 py-3 text-sm font-semibold text-slate-800">{alertTypeLabel(alert.alert_type)}</td>
                  <td className="px-4 py-3"><StatusBadge status={alert.risk_level} /></td>
                  <td className="px-4 py-3 text-sm text-slate-600">{alert.ear_value?.toFixed(3) ?? "-"}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">{alert.mar_value?.toFixed(3) ?? "-"}</td>
                </tr>
              );
            })
          ) : (
            <EmptyRow colSpan={6} text="Chưa có cảnh báo." />
          )}
        </DataTable>
      </section>
    </AdminShell>
  );
}
