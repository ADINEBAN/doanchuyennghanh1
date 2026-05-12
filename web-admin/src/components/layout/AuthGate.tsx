"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

const publicRoutes = new Set(["/login"]);

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
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <div className="flex items-center gap-3 rounded-lg border border-slate-200 bg-white px-5 py-4 text-sm font-semibold text-slate-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          Đang tải dữ liệu...
        </div>
      </div>
    );
  }

  if (!isPublic && (!session || !profile || profile.role === "DRIVER")) {
    return null;
  }

  return <>{children}</>;
}
