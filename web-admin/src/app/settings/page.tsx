import { AdminShell } from "@/components/layout/AdminShell";
import { PageHeader } from "@/components/ui/PageHeader";

export default function SettingsPage() {
  return (
    <AdminShell>
      <PageHeader
        title="Cài đặt hệ thống"
        description="Khu vực dành cho SUPER_ADMIN cấu hình ngưỡng mặc định và model AI."
      />
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-black text-slate-950">Sẽ triển khai ở bước tiếp theo</h3>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Phần này sẽ đọc/ghi bảng system_settings và ai_models. Những tác vụ nhạy cảm sẽ đi qua Next.js API route server-side.
        </p>
      </section>
    </AdminShell>
  );
}
