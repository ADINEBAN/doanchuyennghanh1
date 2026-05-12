"use client";

import { FormEvent, useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { supabase } from "@/lib/supabase";
import type { Company } from "@/types/database";

type CompanyForm = {
  id?: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  status: "active" | "inactive" | "locked";
};

const emptyForm: CompanyForm = {
  name: "",
  email: "",
  phone: "",
  address: "",
  status: "active",
};

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<CompanyForm>(emptyForm);

  async function loadCompanies() {
    const { data } = await supabase
      .from("companies")
      .select("*")
      .order("created_at", { ascending: false });
    setCompanies(data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadCompanies();
    }, 0);
    return () => window.clearTimeout(timer);
  }, []);

  function openCreateForm() {
    setForm(emptyForm);
    setError("");
    setShowForm(true);
  }

  function openEditForm(company: Company) {
    setForm({
      id: company.id,
      name: company.name,
      email: company.email || "",
      phone: company.phone || "",
      address: company.address || "",
      status: company.status,
    });
    setError("");
    setShowForm(true);
  }

  async function saveCompany(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");

    const payload = {
      name: form.name.trim(),
      email: form.email.trim(),
      phone: form.phone.trim(),
      address: form.address.trim(),
      status: form.status,
    };

    const result = form.id
      ? await supabase.from("companies").update(payload).eq("id", form.id)
      : await supabase.from("companies").insert(payload);

    setSaving(false);

    if (result.error) {
      setError(result.error.message);
      return;
    }

    setShowForm(false);
    setForm(emptyForm);
    await loadCompanies();
  }

  async function updateStatus(company: Company, status: CompanyForm["status"]) {
    await supabase.from("companies").update({ status }).eq("id", company.id);
    await loadCompanies();
  }

  return (
    <AdminShell>
      <PageHeader
        title="Quản lý hãng xe"
        description="Chỉ SUPER_ADMIN được xem và quản lý danh sách hãng xe."
        action={
          <button
            onClick={openCreateForm}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700"
          >
            Thêm hãng xe
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={saveCompany} className="mb-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Tên hãng</span>
              <input value={form.name} onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))} required className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Email</span>
              <input value={form.email} onChange={(event) => setForm((current) => ({ ...current, email: event.target.value }))} type="email" className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Điện thoại</span>
              <input value={form.phone} onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Trạng thái</span>
              <select value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as CompanyForm["status"] }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100">
                <option value="active">Đang hoạt động</option>
                <option value="inactive">Không hoạt động</option>
                <option value="locked">Đã khóa</option>
              </select>
            </label>
            <label className="block md:col-span-2">
              <span className="text-sm font-bold text-slate-700">Địa chỉ</span>
              <input value={form.address} onChange={(event) => setForm((current) => ({ ...current, address: event.target.value }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
          </div>
          {error ? <div className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm font-bold text-rose-700">{error}</div> : null}
          <div className="mt-5 flex justify-end gap-2">
            <button type="button" onClick={() => setShowForm(false)} className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-bold text-slate-700 hover:bg-slate-50">
              Hủy
            </button>
            <button disabled={saving} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700 disabled:bg-blue-300">
              {saving ? "Đang lưu..." : "Lưu hãng xe"}
            </button>
          </div>
        </form>
      ) : null}

      <DataTable columns={["Tên hãng", "Email", "Điện thoại", "Địa chỉ", "Trạng thái", "Thao tác"]}>
        {loading ? (
          <EmptyRow colSpan={6} text="Đang tải hãng xe..." />
        ) : companies.length ? (
          companies.map((company) => (
            <tr key={company.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm font-black text-slate-900">{company.name}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{company.email || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{company.phone || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{company.address || "-"}</td>
              <td className="px-4 py-3"><StatusBadge status={company.status} /></td>
              <td className="space-x-2 px-4 py-3 text-sm">
                <button onClick={() => openEditForm(company)} className="font-bold text-blue-700 hover:text-blue-900">
                  Sửa
                </button>
                <button onClick={() => void updateStatus(company, company.status === "locked" ? "active" : "locked")} className="font-bold text-rose-700 hover:text-rose-900">
                  {company.status === "locked" ? "Mở khóa" : "Khóa"}
                </button>
              </td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={6} text="Chưa có hãng xe." />
        )}
      </DataTable>
    </AdminShell>
  );
}
