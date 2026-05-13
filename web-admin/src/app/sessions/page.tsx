"use client";

import { useCallback, useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { useAuth } from "@/contexts/AuthContext";
import { formatDateTime, formatDuration } from "@/lib/format";
import { supabase } from "@/lib/supabase";
import { useCachedState } from "@/hooks/useCachedState";
import type { MonitoringSession, Profile, SessionStatus } from "@/types/database";

const sessionStatuses: Array<{ value: SessionStatus; label: string }> = [
  { value: "running", label: "Đang chạy" },
  { value: "stopped", label: "Đã dừng" },
  { value: "interrupted", label: "Gián đoạn" },
];

export default function SessionsPage() {
  const { profile } = useAuth();
  const cacheScope = profile?.id ?? "guest";
  const [sessions, setSessions, hadSessions] = useCachedState<MonitoringSession[]>(`web-admin:${cacheScope}:sessions:list`, []);
  const [drivers, setDrivers, hadDrivers] = useCachedState<Profile[]>(`web-admin:${cacheScope}:sessions:drivers`, []);
  const [loading, setLoading] = useState(!(hadSessions || hadDrivers));
  const [driverId, setDriverId] = useState("");
  const [status, setStatus] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const loadSessions = useCallback(async () => {
    let query = supabase
      .from("monitoring_sessions")
      .select("*")
      .order("started_at", { ascending: false })
      .limit(200);

    if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
      query = query.eq("company_id", profile.company_id);
    }
    if (driverId) query = query.eq("user_id", driverId);
    if (status) query = query.eq("status", status);
    if (fromDate) query = query.gte("started_at", new Date(`${fromDate}T00:00:00`).toISOString());
    if (toDate) query = query.lte("started_at", new Date(`${toDate}T23:59:59`).toISOString());

    const { data } = await query;
    setSessions(data ?? []);
    setLoading(false);
  }, [driverId, fromDate, profile, setSessions, status, toDate]);

  const loadDrivers = useCallback(async () => {
    let query = supabase.from("profiles").select("*").eq("role", "DRIVER").order("full_name");
    if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
      query = query.eq("company_id", profile.company_id);
    }
    const { data } = await query;
    setDrivers(data ?? []);
  }, [profile, setDrivers]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadDrivers();
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
  }, [loadDrivers, loadSessions]);

  return (
    <AdminShell>
      <PageHeader
        title="Phiên giám sát"
        description="Theo dõi phiên desktop app đang chạy, đã dừng hoặc bị gián đoạn."
      />

      <section className="mb-5 grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-5">
        <label className="block">
          <span className="text-xs font-bold uppercase text-slate-500">Tài xế</span>
          <select value={driverId} onChange={(event) => setDriverId(event.target.value)} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm">
            <option value="">Tất cả</option>
            {drivers.map((driver) => (
              <option key={driver.id} value={driver.id}>{driver.full_name || driver.email}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-xs font-bold uppercase text-slate-500">Trạng thái</span>
          <select value={status} onChange={(event) => setStatus(event.target.value)} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm">
            <option value="">Tất cả</option>
            {sessionStatuses.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-xs font-bold uppercase text-slate-500">Từ ngày</span>
          <input type="date" value={fromDate} onChange={(event) => setFromDate(event.target.value)} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm" />
        </label>
        <label className="block">
          <span className="text-xs font-bold uppercase text-slate-500">Đến ngày</span>
          <input type="date" value={toDate} onChange={(event) => setToDate(event.target.value)} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm" />
        </label>
        <div className="flex items-end gap-2">
          <button onClick={() => void loadSessions()} className="h-10 rounded-lg bg-blue-600 px-4 text-sm font-black text-white hover:bg-blue-700">Lọc</button>
          <button
            onClick={() => {
              setDriverId("");
              setStatus("");
              setFromDate("");
              setToDate("");
            }}
            className="h-10 rounded-lg border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 hover:bg-slate-50"
          >
            Xóa
          </button>
        </div>
      </section>

      <DataTable columns={["Mã phiên", "Tài xế", "Bắt đầu", "Kết thúc", "Thời lượng", "Cảnh báo", "Trạng thái"]}>
        {loading ? (
          <EmptyRow colSpan={7} text="Đang tải phiên giám sát..." />
        ) : sessions.length ? (
          sessions.map((session) => {
            const driver = drivers.find((item) => item.id === session.user_id);
            return (
              <tr key={session.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-bold text-slate-800">{session.id.slice(0, 8)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{driver?.full_name || driver?.email || session.user_id.slice(0, 8)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.started_at)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(session.ended_at)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{formatDuration(session.duration_seconds)}</td>
                <td className="px-4 py-3 text-sm font-bold text-slate-800">{session.total_alerts ?? 0}</td>
                <td className="px-4 py-3"><StatusBadge status={session.status} /></td>
              </tr>
            );
          })
        ) : (
          <EmptyRow colSpan={7} text="Chưa có phiên giám sát." />
        )}
      </DataTable>
    </AdminShell>
  );
}
