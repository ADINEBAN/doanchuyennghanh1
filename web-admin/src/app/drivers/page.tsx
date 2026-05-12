"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { supabase } from "@/lib/supabase";
import type { Profile } from "@/types/database";

export default function DriversPage() {
  const [drivers, setDrivers] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDrivers() {
      const { data } = await supabase
        .from("profiles")
        .select("*")
        .eq("role", "DRIVER")
        .order("created_at", { ascending: false });
      setDrivers(data ?? []);
      setLoading(false);
    }
    void loadDrivers();
  }, []);

  return (
    <AdminShell>
      <PageHeader
        title="Quản lý tài xế"
        description="Danh sách tài khoản DRIVER do hãng xe quản lý."
        action={<button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700">Tạo tài xế</button>}
      />
      <DataTable columns={["Họ tên", "Email", "Số điện thoại", "Username", "Trạng thái"]}>
        {loading ? (
          <EmptyRow colSpan={5} text="Đang tải tài xế..." />
        ) : drivers.length ? (
          drivers.map((driver) => (
            <tr key={driver.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm font-black text-slate-900">{driver.full_name || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{driver.email}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{driver.phone || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{driver.username || "-"}</td>
              <td className="px-4 py-3"><StatusBadge status={driver.status} /></td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={5} text="Chưa có tài xế." />
        )}
      </DataTable>
    </AdminShell>
  );
}
