"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertTriangle,
  BarChart3,
  Building2,
  Car,
  Gauge,
  LayoutDashboard,
  LogOut,
  Settings,
  Users,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { roleLabel } from "@/lib/format";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: ["SUPER_ADMIN", "COMPANY_ADMIN"] },
  { href: "/companies", label: "Hãng xe", icon: Building2, roles: ["SUPER_ADMIN"] },
  { href: "/vehicles", label: "Xe", icon: Car, roles: ["SUPER_ADMIN", "COMPANY_ADMIN"] },
  { href: "/drivers", label: "Tài xế", icon: Users, roles: ["SUPER_ADMIN", "COMPANY_ADMIN"] },
  { href: "/sessions", label: "Phiên giám sát", icon: Gauge, roles: ["SUPER_ADMIN", "COMPANY_ADMIN"] },
  { href: "/alerts", label: "Cảnh báo", icon: AlertTriangle, roles: ["SUPER_ADMIN", "COMPANY_ADMIN"] },
  { href: "/statistics", label: "Thống kê", icon: BarChart3, roles: ["SUPER_ADMIN", "COMPANY_ADMIN"] },
  { href: "/settings", label: "Cài đặt", icon: Settings, roles: ["SUPER_ADMIN"] },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { profile, signOut } = useAuth();
  const availableItems = navItems.filter((item) => profile && item.roles.includes(profile.role));

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-200 bg-white lg:flex lg:flex-col">
        <div className="border-b border-slate-200 px-6 py-5">
          <div className="text-lg font-black tracking-tight text-slate-950">Driver Monitor</div>
          <div className="mt-1 text-sm font-medium text-slate-500">Web Admin</div>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-4">
          {availableItems.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  active
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                }`}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-slate-200 p-4">
          <div className="rounded-lg bg-slate-50 p-3">
            <div className="text-sm font-bold text-slate-950">
              {profile?.full_name || profile?.email}
            </div>
            <div className="mt-1 text-xs font-semibold text-slate-500">
              {profile ? roleLabel(profile.role) : "-"}
            </div>
          </div>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 px-5 py-4 backdrop-blur">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Hệ thống giám sát tài xế</p>
              <h1 className="text-xl font-black tracking-tight text-slate-950">Quản trị vận hành</h1>
            </div>
            <button
              onClick={() => void signOut()}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-bold text-slate-700 shadow-sm hover:bg-slate-50"
            >
              <LogOut className="h-4 w-4" />
              Đăng xuất
            </button>
          </div>
        </header>
        <main className="p-5 lg:p-7">{children}</main>
      </div>
    </div>
  );
}
