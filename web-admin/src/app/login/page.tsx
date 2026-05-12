"use client";

import { FormEvent, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const searchParams = useSearchParams();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(searchParams.get("driver") ? "Tài khoản DRIVER chỉ dùng cho desktop app." : "");
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const result = await signIn(email, password);
    if (result.error) {
      setError(result.error);
    }
    setLoading(false);
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 px-5">
      <section className="grid w-full max-w-5xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl lg:grid-cols-[1.05fr_0.95fr]">
        <div className="hidden bg-slate-950 p-10 text-white lg:block">
          <div className="inline-flex items-center gap-2 rounded-lg bg-white/10 px-3 py-2 text-sm font-bold text-blue-100">
            <ShieldCheck className="h-4 w-4" />
            Driver Monitor Admin
          </div>
          <h1 className="mt-16 max-w-md text-4xl font-black leading-tight tracking-tight">
            Quản lý tài xế, xe và cảnh báo theo thời gian thực.
          </h1>
          <p className="mt-5 max-w-md text-base leading-7 text-slate-300">
            Web admin dành cho SUPER_ADMIN và COMPANY_ADMIN. DRIVER tiếp tục sử dụng desktop app để giám sát webcam.
          </p>
          <div className="mt-12 grid grid-cols-2 gap-3">
            {["Phiên đang chạy", "Cảnh báo realtime", "Quản lý xe", "Thống kê vận hành"].map((item) => (
              <div key={item} className="rounded-lg border border-white/10 bg-white/5 p-4 text-sm font-bold">
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="p-8 sm:p-10">
          <div className="mb-8">
            <div className="mb-3 inline-flex rounded-lg bg-blue-50 px-3 py-1 text-xs font-black uppercase tracking-wide text-blue-700">
              Web Admin
            </div>
            <h2 className="text-3xl font-black tracking-tight text-slate-950">Đăng nhập</h2>
            <p className="mt-2 text-sm font-medium text-slate-500">
              Sử dụng tài khoản quản trị được cấp trong hệ thống.
            </p>
          </div>

          <form onSubmit={onSubmit} className="space-y-5">
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Email</span>
              <input
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                type="email"
                required
                className="mt-2 h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium outline-none ring-blue-500 transition focus:border-blue-500 focus:ring-2"
                placeholder="admin@example.com"
              />
            </label>
            <label className="block">
              <span className="text-sm font-bold text-slate-700">Mật khẩu</span>
              <input
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                type="password"
                required
                className="mt-2 h-11 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm font-medium outline-none ring-blue-500 transition focus:border-blue-500 focus:ring-2"
                placeholder="Nhập mật khẩu"
              />
            </label>

            {error ? (
              <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm font-semibold text-rose-700">
                {error}
              </div>
            ) : null}

            <button
              type="submit"
              disabled={loading}
              className="h-11 w-full rounded-lg bg-blue-600 px-4 text-sm font-black text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
            >
              {loading ? "Đang đăng nhập..." : "Đăng nhập"}
            </button>
          </form>
        </div>
      </section>
    </main>
  );
}
