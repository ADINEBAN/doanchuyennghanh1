"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/lib/supabase";
import type { Company, Profile, Vehicle, VehicleStatus } from "@/types/database";

type VehicleForm = {
  id?: string;
  company_id: string;
  license_plate: string;
  brand: string;
  model: string;
  color: string;
  year: string;
  status: VehicleStatus;
  assigned_driver_id: string;
};

const emptyForm: VehicleForm = {
  company_id: "",
  license_plate: "",
  brand: "",
  model: "",
  color: "",
  year: "",
  status: "available",
  assigned_driver_id: "",
};

export default function VehiclesPage() {
  const { profile } = useAuth();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [drivers, setDrivers] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState<VehicleForm>(emptyForm);

  const loadData = useCallback(async () => {
    let vehicleQuery = supabase.from("vehicles").select("*").order("created_at", { ascending: false });
    let companyQuery = supabase.from("companies").select("*").order("name");
    let driverQuery = supabase.from("profiles").select("*").eq("role", "DRIVER").order("full_name");

    if (profile?.role === "COMPANY_ADMIN" && profile.company_id) {
      vehicleQuery = vehicleQuery.eq("company_id", profile.company_id);
      companyQuery = companyQuery.eq("id", profile.company_id);
      driverQuery = driverQuery.eq("company_id", profile.company_id);
    }

    const [vehicleRows, companyRows, driverRows] = await Promise.all([vehicleQuery, companyQuery, driverQuery]);
    setVehicles(vehicleRows.data ?? []);
    setCompanies(companyRows.data ?? []);
    setDrivers(driverRows.data ?? []);
    setLoading(false);
  }, [profile]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadData();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadData]);

  function openCreateForm() {
    setForm({
      ...emptyForm,
      company_id: profile?.role === "COMPANY_ADMIN" ? profile.company_id || "" : companies[0]?.id ?? "",
    });
    setError("");
    setShowForm(true);
  }

  function openEditForm(vehicle: Vehicle) {
    setForm({
      id: vehicle.id,
      company_id: vehicle.company_id,
      license_plate: vehicle.license_plate,
      brand: vehicle.brand || "",
      model: vehicle.model || "",
      color: vehicle.color || "",
      year: vehicle.year ? String(vehicle.year) : "",
      status: vehicle.status,
      assigned_driver_id: vehicle.assigned_driver_id || "",
    });
    setError("");
    setShowForm(true);
  }

  async function saveVehicle(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");

    const payload = {
      company_id: form.company_id,
      license_plate: form.license_plate.trim(),
      brand: form.brand.trim(),
      model: form.model.trim(),
      color: form.color.trim(),
      year: form.year ? Number(form.year) : null,
      status: form.status,
      assigned_driver_id: form.assigned_driver_id || null,
    };

    const result = form.id
      ? await supabase.from("vehicles").update(payload).eq("id", form.id)
      : await supabase.from("vehicles").insert(payload);

    setSaving(false);
    if (result.error) {
      setError(result.error.message);
      return;
    }

    setShowForm(false);
    setForm(emptyForm);
    await loadData();
  }

  return (
    <AdminShell>
      <PageHeader
        title="Quản lý xe"
        description="Thêm xe, cập nhật trạng thái và gán xe cho tài xế."
        action={
          <button onClick={openCreateForm} className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700">
            Thêm xe
          </button>
        }
      />

      {showForm ? (
        <form onSubmit={saveVehicle} className="mb-6 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <div className="grid gap-4 md:grid-cols-3">
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Hãng xe</span>
              <select value={form.company_id} disabled={profile?.role === "COMPANY_ADMIN"} onChange={(event) => setForm((current) => ({ ...current, company_id: event.target.value }))} required className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100">
                <option value="">Chọn hãng</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>{company.name}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Biển số</span>
              <input value={form.license_plate} onChange={(event) => setForm((current) => ({ ...current, license_plate: event.target.value }))} required className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Trạng thái</span>
              <select value={form.status} onChange={(event) => setForm((current) => ({ ...current, status: event.target.value as VehicleStatus }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100">
                <option value="available">Sẵn sàng</option>
                <option value="assigned">Đã gán</option>
                <option value="maintenance">Bảo trì</option>
                <option value="inactive">Không hoạt động</option>
              </select>
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Hãng xe sản xuất</span>
              <input value={form.brand} onChange={(event) => setForm((current) => ({ ...current, brand: event.target.value }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Dòng xe</span>
              <input value={form.model} onChange={(event) => setForm((current) => ({ ...current, model: event.target.value }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Năm</span>
              <input value={form.year} onChange={(event) => setForm((current) => ({ ...current, year: event.target.value }))} type="number" className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Màu</span>
              <input value={form.color} onChange={(event) => setForm((current) => ({ ...current, color: event.target.value }))} className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
            </label>
            <label className="block md:col-span-2">
              <span className="text-sm font-bold text-slate-700">Tài xế được gán</span>
              <select
                value={form.assigned_driver_id}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    assigned_driver_id: event.target.value,
                    status: event.target.value ? "assigned" : current.status,
                  }))
                }
                className="mt-2 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              >
                <option value="">Chưa gán</option>
                {drivers.map((driver) => (
                  <option key={driver.id} value={driver.id}>{driver.full_name || driver.email}</option>
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
              {saving ? "Đang lưu..." : "Lưu xe"}
            </button>
          </div>
        </form>
      ) : null}

      <DataTable columns={["Biển số", "Hãng", "Dòng xe", "Màu", "Năm", "Tài xế", "Trạng thái", "Thao tác"]}>
        {loading ? (
          <EmptyRow colSpan={8} text="Đang tải xe..." />
        ) : vehicles.length ? (
          vehicles.map((vehicle) => (
            <tr key={vehicle.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-sm font-black text-slate-900">{vehicle.license_plate}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.brand || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.model || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.color || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">{vehicle.year || "-"}</td>
              <td className="px-4 py-3 text-sm text-slate-600">
                {drivers.find((driver) => driver.id === vehicle.assigned_driver_id)?.full_name ||
                  vehicle.assigned_driver_id?.slice(0, 8) ||
                  "-"}
              </td>
              <td className="px-4 py-3"><StatusBadge status={vehicle.status} /></td>
              <td className="px-4 py-3 text-sm">
                <button onClick={() => openEditForm(vehicle)} className="font-bold text-blue-700 hover:text-blue-900">
                  Sửa
                </button>
              </td>
            </tr>
          ))
        ) : (
          <EmptyRow colSpan={8} text="Chưa có xe." />
        )}
      </DataTable>
    </AdminShell>
  );
}
