"use client";

import { useCallback, useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { useAuth } from "@/contexts/AuthContext";
import { alertTypeLabel, formatDateTime } from "@/lib/format";
import { supabase } from "@/lib/supabase";
import { useCachedState } from "@/hooks/useCachedState";
import type { Alert, AlertType, Profile, RiskLevel } from "@/types/database";

const alertTypes: Array<{ value: AlertType; label: string }> = [
  { value: "closed_eyes", label: "Nhắm mắt" },
  { value: "yawning", label: "Ngáp" },
  { value: "drowsy", label: "Buồn ngủ" },
  { value: "distracted", label: "Mất tập trung" },
  { value: "face_not_detected", label: "Không thấy mặt" },
];

const riskLevels: Array<{ value: RiskLevel; label: string }> = [
  { value: "low", label: "Thấp" },
  { value: "medium", label: "Trung bình" },
  { value: "high", label: "Cao" },
  { value: "danger", label: "Nguy hiểm" },
];

export default function AlertsPage() {
  const { profile } = useAuth();
  const cacheScope = profile?.id ?? "guest";
  const [alerts, setAlerts, hadAlerts] = useCachedState<Alert[]>(`web-admin:${cacheScope}:alerts:list`, []);
  const [drivers, setDrivers, hadDrivers] = useCachedState<Profile[]>(`web-admin:${cacheScope}:alerts:drivers`, []);
  const [loading, setLoading] = useState(!(hadAlerts || hadDrivers));
  const [driverId, setDriverId] = useState("");
  const [alertType, setAlertType] = useState("");
  const [riskLevel, setRiskLevel] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");

  const loadAlerts = useCallback(async () => {
    let query = supabase
      .from("alerts")
      .select("*")
      .order("triggered_at", { ascending: false })
      .limit(300);

    if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
      query = query.eq("company_id", profile.company_id);
    }
    if (driverId) query = query.eq("user_id", driverId);
    if (alertType) query = query.eq("alert_type", alertType);
    if (riskLevel) query = query.eq("risk_level", riskLevel);
    if (fromDate) query = query.gte("triggered_at", new Date(`${fromDate}T00:00:00`).toISOString());
    if (toDate) query = query.lte("triggered_at", new Date(`${toDate}T23:59:59`).toISOString());

    const { data } = await query;
    setAlerts(data ?? []);
    setLoading(false);
  }, [alertType, driverId, fromDate, profile, riskLevel, setAlerts, toDate]);

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
  }, [loadAlerts, loadDrivers]);

  return (
    <AdminShell>
      <PageHeader
        title="Lịch sử cảnh báo"
        description="Cảnh báo realtime từ desktop app: mắt nhắm, ngáp, buồn ngủ, mất tập trung."
      />

      <section className="mb-5 grid gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-6">
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
          <span className="text-xs font-bold uppercase text-slate-500">Loại</span>
          <select value={alertType} onChange={(event) => setAlertType(event.target.value)} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm">
            <option value="">Tất cả</option>
            {alertTypes.map((item) => (
              <option key={item.value} value={item.value}>{item.label}</option>
            ))}
          </select>
        </label>
        <label className="block">
          <span className="text-xs font-bold uppercase text-slate-500">Rủi ro</span>
          <select value={riskLevel} onChange={(event) => setRiskLevel(event.target.value)} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm">
            <option value="">Tất cả</option>
            {riskLevels.map((item) => (
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
          <button onClick={() => void loadAlerts()} className="h-10 rounded-lg bg-blue-600 px-4 text-sm font-black text-white hover:bg-blue-700">Lọc</button>
          <button
            onClick={() => {
              setDriverId("");
              setAlertType("");
              setRiskLevel("");
              setFromDate("");
              setToDate("");
            }}
            className="h-10 rounded-lg border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 hover:bg-slate-50"
          >
            Xóa
          </button>
        </div>
      </section>

      <DataTable columns={["Thời gian", "Tài xế", "Loại", "Rủi ro", "EAR", "MAR", "Yaw", "Pitch"]}>
        {loading ? (
          <EmptyRow colSpan={8} text="Đang tải cảnh báo..." />
        ) : alerts.length ? (
          alerts.map((alert) => {
            const driver = drivers.find((item) => item.id === alert.user_id);
            return (
              <tr key={alert.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm text-slate-600">{formatDateTime(alert.triggered_at)}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{driver?.full_name || driver?.email || alert.user_id.slice(0, 8)}</td>
                <td className="px-4 py-3 text-sm font-bold text-slate-800">{alertTypeLabel(alert.alert_type)}</td>
                <td className="px-4 py-3"><StatusBadge status={alert.risk_level} /></td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.ear_value?.toFixed(3) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.mar_value?.toFixed(3) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.head_yaw?.toFixed(1) ?? "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{alert.head_pitch?.toFixed(1) ?? "-"}</td>
              </tr>
            );
          })
        ) : (
          <EmptyRow colSpan={8} text="Chưa có cảnh báo." />
        )}
      </DataTable>
    </AdminShell>
  );
}
