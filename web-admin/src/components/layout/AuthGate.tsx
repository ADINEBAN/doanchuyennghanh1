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
  const { loading, session, profile, profileStatus, profileError, refreshProfile, signOut } = useAuth();
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
    return <LoadingScreen text="Dang tai du lieu..." />;
  }

  if (!isPublic && !session) {
    return <LoadingScreen text="Dang chuyen ve trang dang nhap..." />;
  }

  if (!isPublic && session && !profile && profileStatus === "loading") {
    return <LoadingScreen text="Dang tai ho so quan tri..." />;
  }

  if (!isPublic && session && !profile && profileStatus === "error") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <div className="max-w-md rounded-lg border border-amber-200 bg-white p-5 text-center shadow-sm">
          <h1 className="text-base font-black text-slate-950">Mat ket noi tam thoi voi Supabase</h1>
          <p className="mt-2 text-sm text-slate-600">
            {profileError || "Web van giu phien dang nhap. Thu ket noi lai thay vi reload trang."}
          </p>
          <div className="mt-4 flex justify-center gap-2">
            <button
              onClick={() => void refreshProfile()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700"
            >
              Thu lai
            </button>
            <button
              onClick={() => void signOut()}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-black text-slate-700 hover:bg-slate-50"
            >
              Dang xuat
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!isPublic && session && profileStatus === "missing") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100">
        <div className="max-w-md rounded-lg border border-rose-200 bg-white p-5 text-center shadow-sm">
          <h1 className="text-base font-black text-slate-950">Tai khoan chua co ho so quan tri</h1>
          <p className="mt-2 text-sm text-slate-600">
            Tai khoan Auth ton tai nhung khong co ban ghi trong bang profiles. Vui long dung tai khoan web admin.
          </p>
          <button
            onClick={() => void signOut()}
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-black text-white hover:bg-blue-700"
          >
            Dang nhap lai
          </button>
        </div>
      </div>
    );
  }

  if (!isPublic && session && !profile) {
    return <LoadingScreen text="Dang chuan bi phien quan tri..." />;
  }

  if (!isPublic && profile?.role === "DRIVER") {
    return <LoadingScreen text="Tai khoan tai xe khong dung cho web admin..." />;
  }

  return <>{children}</>;
}
