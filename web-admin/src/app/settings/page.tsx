"use client";

import { useCallback, useEffect, useState } from "react";
import { Save, ServerCog } from "lucide-react";
import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";
import { DataTable, EmptyRow } from "@/components/ui/DataTable";
import { StatusBadge } from "@/components/ui/Badge";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/lib/supabase";
import { useCachedState } from "@/hooks/useCachedState";
import type { AIModel, SystemSetting } from "@/types/database";

type ModelForm = {
  name: string;
  version: string;
  file_path: string;
  class_labels: string;
};

const defaultModelForm: ModelForm = {
  name: "",
  version: "1.0",
  file_path: "ml/exported_models/drowsiness_model.keras",
  class_labels: "normal,closed_eyes,yawning,drowsy",
};

export default function SettingsPage() {
  const { profile } = useAuth();
  const cacheScope = profile?.id ?? "guest";
  const [settings, setSettings, hadSettings] = useCachedState<SystemSetting[]>(`web-admin:${cacheScope}:settings:system`, []);
  const [models, setModels, hadModels] = useCachedState<AIModel[]>(`web-admin:${cacheScope}:settings:models`, []);
  const [modelForm, setModelForm] = useState<ModelForm>(defaultModelForm);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(!(hadSettings || hadModels));
  const isSuperAdmin = profile?.role === "SUPER_ADMIN";

  const loadSettings = useCallback(async () => {
    if (!isSuperAdmin) {
      setLoading(false);
      return;
    }

    const [settingRows, modelRows] = await Promise.all([
      supabase.from("system_settings").select("*").order("key"),
      supabase.from("ai_models").select("*").order("created_at", { ascending: false }),
    ]);
    setSettings(settingRows.data ?? []);
    setModels(modelRows.data ?? []);
    setLoading(false);
  }, [isSuperAdmin, setModels, setSettings]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadSettings();
    }, 0);
    return () => window.clearTimeout(timer);
  }, [loadSettings]);

  async function saveSetting(setting: SystemSetting) {
    const { error } = await supabase
      .from("system_settings")
      .update({ value: setting.value, updated_by: profile?.id ?? null })
      .eq("id", setting.id);

    setMessage(error ? error.message : "Đã lưu cài đặt hệ thống.");
    if (!error) void loadSettings();
  }

  async function addModel() {
    if (!modelForm.name.trim() || !modelForm.file_path.trim()) {
      setMessage("Tên model và đường dẫn file là bắt buộc.");
      return;
    }

    const { error } = await supabase.from("ai_models").insert({
      name: modelForm.name.trim(),
      version: modelForm.version.trim() || "1.0",
      file_path: modelForm.file_path.trim(),
      file_format: modelForm.file_path.endsWith(".tflite") ? "tflite" : "keras",
      class_labels: modelForm.class_labels.trim(),
      num_classes: modelForm.class_labels.split(",").filter(Boolean).length,
      status: "active",
      created_by: profile?.id ?? null,
    });

    setMessage(error ? error.message : "Đã thêm model AI.");
    if (!error) {
      setModelForm(defaultModelForm);
      void loadSettings();
    }
  }

  if (!isSuperAdmin) {
    return (
      <AdminShell>
        <PageHeader title="Cài đặt hệ thống" description="Chỉ SUPER_ADMIN được cấu hình hệ thống và model AI." />
      </AdminShell>
    );
  }

  return (
    <AdminShell>
      <PageHeader
        title="Cài đặt hệ thống"
        description="Quản lý ngưỡng mặc định và khai báo model AI sau khi train."
        action={<ServerCog className="h-5 w-5 text-blue-700" />}
      />

      {message ? (
        <div className="mb-4 rounded-lg border border-blue-100 bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-800">
          {message}
        </div>
      ) : null}

      <section>
        <h3 className="mb-3 text-base font-black text-slate-950">System settings</h3>
        <DataTable columns={["Key", "Value", "Kiểu", "Mô tả", ""]}>
          {loading ? (
            <EmptyRow colSpan={5} text="Đang tải cài đặt..." />
          ) : settings.length ? (
            settings.map((setting) => (
              <tr key={setting.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-black text-slate-900">{setting.key}</td>
                <td className="px-4 py-3">
                  <input
                    value={setting.value}
                    onChange={(event) =>
                      setSettings((rows) =>
                        rows.map((row) => row.id === setting.id ? { ...row, value: event.target.value } : row),
                      )
                    }
                    className="w-36 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-900 outline-none focus:border-blue-500"
                  />
                </td>
                <td className="px-4 py-3 text-sm text-slate-600">{setting.data_type}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{setting.description || "-"}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => void saveSetting(setting)}
                    className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-3 py-2 text-sm font-black text-white hover:bg-blue-700"
                  >
                    <Save className="h-4 w-4" />
                    Lưu
                  </button>
                </td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={5} text="Chưa có system_settings." />
          )}
        </DataTable>
      </section>

      <section className="mt-6">
        <h3 className="mb-3 text-base font-black text-slate-950">AI models</h3>
        <div className="mb-4 grid gap-3 rounded-lg border border-slate-200 bg-white p-4 md:grid-cols-4">
          <input
            placeholder="Tên model"
            value={modelForm.name}
            onChange={(event) => setModelForm({ ...modelForm, name: event.target.value })}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
          <input
            placeholder="Version"
            value={modelForm.version}
            onChange={(event) => setModelForm({ ...modelForm, version: event.target.value })}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500"
          />
          <input
            placeholder="File path"
            value={modelForm.file_path}
            onChange={(event) => setModelForm({ ...modelForm, file_path: event.target.value })}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 md:col-span-2"
          />
          <input
            placeholder="Labels"
            value={modelForm.class_labels}
            onChange={(event) => setModelForm({ ...modelForm, class_labels: event.target.value })}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 md:col-span-3"
          />
          <button
            onClick={() => void addModel()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700"
          >
            Thêm model
          </button>
        </div>

        <DataTable columns={["Tên", "Version", "File", "Labels", "Trạng thái"]}>
          {models.length ? (
            models.map((model) => (
              <tr key={model.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-sm font-black text-slate-900">{model.name}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{model.version || "-"}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{model.file_path}</td>
                <td className="px-4 py-3 text-sm text-slate-600">{model.class_labels || "-"}</td>
                <td className="px-4 py-3"><StatusBadge status={model.status} /></td>
              </tr>
            ))
          ) : (
            <EmptyRow colSpan={5} text="Chưa khai báo model AI." />
          )}
        </DataTable>
      </section>
    </AdminShell>
  );
}
