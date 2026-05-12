"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { supabase } from "@/lib/supabase";
import type { Vehicle } from "@/types/database";

export default function VehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadVehicles() {
      const { data } = await supabase
        .from("vehicles")
        .select("*")
        .order("created_at", { ascending: false });
      setVehicles(data ?? []);
      setLoading(false);
    }
    void loadVehicles();
  }, []);

  return (
    <AdminShell>
      <PageHeader
        title="Quản lý xe"
        description="Danh sách xe theo quyền truy cập RLS của tài khoản quản trị."
        action={<button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700">Thêm xe</button>}
      />
      <DataTable columns={["Biển số", "Hãng", "Dòng xe", "Màu", "Năm", "Tài xế", "Trạng thái"]}>
        {loading ? (
          <EmptyRow colSpan={7} text="Đang tải xe..." />
        ) : vehicles.length ? (
          vehicles.map((vehicle) => (
            <tr key={vehicle.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm font-black text-slate-900">{vehicle.license_plate}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.brand || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.model || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.color || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.year || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.assigned_driver_id?.slice(0, 8) || "-"}</td>
              <td className="px-4 py-3"><StatusBadge status={vehicle.status} /></td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={7} text="Chưa có xe." />
        )}
      </DataTable>
    </AdminShell>
  );
}
