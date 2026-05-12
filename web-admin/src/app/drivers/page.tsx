"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { useAuth } from "@/contexts/AuthContext";
import { roleLabel } from "@/lib/format";
import { getDriverPresence, LIVE_STATUS_POLL_MS } from "@/lib/live-status";
import { supabase } from "@/lib/supabase";
import type { Company, DriverLiveStatus, Profile, UserRole } from "@/types/database";

type AccountForm = {
  email: string;
  password: string;
  fullName: string;
  phone: string;
  role: Extract<UserRole, "COMPANY_ADMIN" | "DRIVER">;
  companyId: string;
};

const emptyForm: AccountForm = {
  email: "",
  password: "123456",
  fullName: "",
  phone: "",
  role: "DRIVER",
  companyId: "",
};

export default function DriversPage() {
  const { profile, session } = useAuth();
  const [users, setUsers] = useState<Profile[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [liveStatuses, setLiveStatuses] = useState<DriverLiveStatus[]>([]);
  const [currentTime, setCurrentTime] = useState(() => Date.now());
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [form, setForm] = useState<AccountForm>(emptyForm);
  const isLoadingLiveRef = useRef(false);

  const loadLiveStatuses = useCallback(async () => {
    if (isLoadingLiveRef.current) return;

    isLoadingLiveRef.current = true;
    try {
      let query = supabase.from("driver_live_status").select("*");
      if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
        query = query.eq("company_id", profile.company_id);
      }

      const { data, error } = await query;
      if (!error) {
        setLiveStatuses(data ?? []);
        setCurrentTime(Date.now());
      }
    } finally {
      isLoadingLiveRef.current = false;
    }
  }, [profile]);

  const loadData = useCallback(async () => {
    try {
      let usersQuery = supabase
        .from("profiles")
        .select("*")
        .in("role", ["DRIVER", "COMPANY_ADMIN"])
        .order("created_at", { ascending: false });
      let companiesQuery = supabase.from("companies").select("*").order("name");

      if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
        usersQuery = usersQuery.eq("company_id", profile.company_id);
        companiesQuery = companiesQuery.eq("id", profile.company_id);
      }

      const [userRows, companyRows] = await Promise.all([usersQuery, companiesQuery]);
      setUsers(userRows.data ?? []);
      setCompanies(companyRows.data ?? []);
      await loadLiveStatuses();
    } finally {
      setLoading(false);
    }
  }, [loadLiveStatuses, profile]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadData();
    }, 0);
    const clock = window.setInterval(() => {
      setCurrentTime(Date.now());
      void loadLiveStatuses();
    }, LIVE_STATUS_POLL_MS);
    const channel = supabase
      .channel("drivers-live-status")
      .on("postgres_changes", { event: "*", schema: "public", table: "driver_live_status" }, () => {
        void loadLiveStatuses();
      })
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          void loadLiveStatuses();
        }
      });

    return () => {
      window.clearTimeout(timer);
      window.clearInterval(clock);
      void supabase.removeChannel(channel);
    };
  }, [loadData, loadLiveStatuses]);

  function openCreateForm() {
    setForm({
      ...emptyForm,
      role: profile?.role === "SUPER_ADMIN" ? "COMPANY_ADMIN" : "DRIVER",
      companyId: profile?.role === "COMPANY_ADMIN" ? profile.company_id || "" : companies[0]?.id || "",
    });
    setError("");
    setSuccess("");
    setShowForm(true);
  }

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    const token = session?.access_token;
    if (!token) {
      setSaving(false);
      setError("Phiên đăng nhập không hợp lệ.");
      return;
    }

    const response = await fetch("/api/admin/create-user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        email: form.email.trim(),
        password: form.password,
        fullName: form.fullName.trim(),
        phone: form.phone.trim(),
        role: form.role,
        companyId: form.companyId,
      }),
    });

    const result = (await response.json()) as { error?: string };
    setSaving(false);

    if (!response.ok || result.error) {
      setError(result.error || "Không thể tạo tài khoản.");
      return;
    }

    setSuccess("Tạo tài khoản thành công.");
    setForm(emptyForm);
    setShowForm(false);
    await loadData();
  }

  async function updateStatus(user: Profile, status: "active" | "locked") {
    await supabase.from("profiles").update({ status }).eq("id", user.id);
    await loadData();
  }

  return (
    <AdminShell>
      <PageHeader
        title="Quản lý tài khoản"
        description="Tạo và quản lý COMPANY_ADMIN, DRIVER theo quyền hiện tại."
        action={
          <button
            onClick={openCreateForm}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700"
          >
            Tạo tài khoản
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={createAccount} className="mb-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Họ tên</span>
              <input
                value={form.fullName}
                onChange={(event) => setForm((current) => ({ ...current, fullName: event.target.value }))}
                required
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Email</span>
              <input
                value={form.email}
                onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))}
                type="email"
                required
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Mật khẩu</span>
              <input
                value={form.password}
                onChange={(event) => setForm((current) => ({ ...current, password: event.target.value }))}
                required
                minLength={6}
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Số điện thoại</span>
              <input
                value={form.phone}
                onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Vai trò</span>
              <select
                value={form.role}
                disabled={profile?.role !== "SUPER_ADMIN"}
                onChange={(event) =>
                  setForm((current) => ({ ...current, role: event.target.value as AccountForm["role"] }))
                }
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              >
                {profile?.role === "SUPER_ADMIN" ? <option value="COMPANY_ADMIN">Quản lý hãng xe</option> : null}
                <option value="DRIVER">Tài xế</option>
              </select>
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Hãng xe</span>
              <select
                value={form.companyId}
                disabled={profile?.role === "COMPANY_ADMIN"}
                onChange={(event) => setForm((current) => ({ ...current, companyId: event.target.value }))}
                required
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              >
                <option value="">Chọn hãng</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {error ? <div className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm font-bold text-rose-700">{error}</div> : null}
          <div className="mt-5 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50">
              Hủy
            </button>
            <button disabled={saving} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700 disabled:bg-blue-300">
              {saving ? "Đang tạo..." : "Tạo tài khoản"}
            </button>
          </div>
        </form>
      ) : null}

      {success ? <div className="mb-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-bold text-emerald-700">{success}</div> : null}

      <DataTable columns={["Họ tên", "Email", "Điện thoại", "Vai trò", "Trạng thái tài khoản", "Phiên giám sát", "Thao tác"]}>
        {loading ? (
          <EmptyRow colSpan={7} text="Đang tải tài khoản..." />
        ) : users.length ? (
          users.map((user) => {
            const live = liveStatuses.find((item) => item.driver_id === user.id);
            const presence = getDriverPresence(live, currentTime);
            return (
              <tr key={user.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-black text-slate-900">
                  {user.role === "DRIVER" ? (
                    <Link href={`/drivers/${user.id}`} className="text-blue-700 hover:text-blue-900 hover:underline">
                      {user.full_name || user.email}
                    </Link>
                  ) : (
                    user.full_name || "-"
                  )}
                </td>
                <td className="px-4 py-3 text-sm text-slate-600">{user.email}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{user.phone || "-"}</td>
                <td className="px-4 py-3 text-sm font-bold text-slate-700">{roleLabel(user.role)}</td>
                <td className="px-4 py-3"><StatusBadge status={user.status} /></td>
                <td className="px-4 py-3">
                  {user.role !== "DRIVER" ? (
                    <span className="text-sm text-slate-400">-</span>
                  ) : presence.monitoring ? (
                    <span className="inline-flex items-center rounded-md bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 ring-1 ring-blue-200">
                      Đang giám sát
                    </span>
                  ) : presence.online ? (
                    <span className="inline-flex items-center rounded-md bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 ring-1 ring-emerald-200">
                      Đã đăng nhập app
                    </span>
                  ) : (
                    <span className="text-sm text-slate-400">Offline</span>
                  )}
                </td>
                <td className="space-x-2 px-4 py-3 text-sm">
                  <button
                    onClick={() => void updateStatus(user, user.status === "locked" ? "active" : "locked")}
                    className="font-bold text-rose-700 hover:text-rose-900"
                  >
                    {user.status === "locked" ? "Mở khóa" : "Khóa"}
                  </button>
                </td>
              </tr>
            );
          })
        ) : (
          <EmptyRow colSpan={7} text="Chưa có tài khoản." />
        )}
      </DataTable>
    </AdminShell>
  );
}
