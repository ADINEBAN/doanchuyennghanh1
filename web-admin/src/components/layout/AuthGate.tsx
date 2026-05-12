"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const publicRoutes = new Set(["/login"]);

function LoadingScreen({ text }: { text: string }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100">
      <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-600 shadow-sm">
        <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
        {text}
      </div>
    </div>
  );
}

export function AuthGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { loading, session, profile } = useAuth();
  const isPublic = publicRoutes.has(pathname);

  useEffect(() => {
    if (loading) return;

    if (!session && !isPublic) {
      router.replace("/login");
      return;
    }

    if (session && profile?.role === "DRIVER") {
      router.replace("/login?driver=1");
      return;
    }

    if (session && profile && isPublic && profile.role !== "DRIVER") {
      router.replace("/dashboard");
    }
  }, [isPublic, loading, profile, router, session]);

  if (loading) {
    return <LoadingScreen text="Đang tải dữ liệu..." />;
  }

  if (!isPublic && !session) {
    return <LoadingScreen text="Đang chuyển về trang đăng nhập..." />;
  }

  if (!isPublic && session && !profile) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <div className="max-w-md rounded-lg border border-rose-200 bg-white p-5 text-center shadow-sm">
          <h1 className="text-base font-black text-slate-950">Không tải được hồ sơ đăng nhập</h1>
          <p className="mt-2 text-sm text-slate-600">
            Kiểm tra kết nối Supabase hoặc đăng nhập lại bằng tài khoản quản trị web.
          </p>
          <button
            onClick={() => router.replace("/login")}
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700"
          >
            Về đăng nhập
          </button>
        </div>
      </div>
    );
  }

  if (!isPublic && profile?.role === "DRIVER") {
    return <LoadingScreen text="Tài khoản tài xế không dùng cho web admin..." />;
  }

  return <>{children}</>;
}
