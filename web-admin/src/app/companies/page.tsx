"use client";

import { useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { supabase } from "@/lib/supabase";
import type { Company } from "@/types/database";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCompanies() {
      const { data } = await supabase
        .from("companies")
        .select("*")
        .order("created_at", { ascending: false });
      setCompanies(data ?? []);
      setLoading(false);
    }
    void loadCompanies();
  }, []);

  return (
    <AdminShell>
      <PageHeader
        title="Quản lý hãng xe"
        description="Chỉ SUPER_ADMIN được xem và quản lý danh sách hãng xe."
        action={<button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700">Thêm hãng xe</button>}
      />
      <DataTable columns={["Tên hãng", "Email", "Điện thoại", "Địa chỉ", "Trạng thái"]}>
        {loading ? (
          <EmptyRow colSpan={5} text="Đang tải hãng xe..." />
        ) : companies.length ? (
          companies.map((company) => (
            <tr key={company.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm font-black text-slate-900">{company.name}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{company.email || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{company.phone || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{company.address || "-"}</td>
              <td className="px-4 py-3"><StatusBadge status={company.status} /></td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={5} text="Chưa có hãng xe." />
        )}
      </DataTable>
    </AdminShell>
  );
}
