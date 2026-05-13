import { createClient } from "@supabase/supabase-js";
import { NextRequest, NextResponse } from "next/server";
import type { Profile, UserRole } from "@/types/database";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
const allowedRoles = ["COMPANY_ADMIN", "DRIVER"] as const;

type CreateUserBody = {
  email?: string;
  password?: string;
  fullName?: string;
  phone?: string;
  role?: UserRole;
  companyId?: string | null;
};

function adminClient() {
  if (!supabaseUrl || !serviceRoleKey) {
    throw new Error("Missing SUPABASE_SERVICE_ROLE_KEY in .env.local");
  }
  return createClient(supabaseUrl, serviceRoleKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });
}

function isAllowedRole(role: string | undefined): role is (typeof allowedRoles)[number] {
  return allowedRoles.includes(role as (typeof allowedRoles)[number]);
}

function isValidEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

async function cleanupCreatedUser(supabase: ReturnType<typeof adminClient>, userId: string) {
  await supabase.from("user_settings").delete().eq("user_id", userId);
  await supabase.from("profiles").delete().eq("id", userId);
  await supabase.auth.admin.deleteUser(userId);
}

export async function POST(request: NextRequest) {
  try {
    const token = request.headers.get("authorization")?.replace("Bearer ", "");
    if (!token) {
      return NextResponse.json({ error: "Missing authorization token" }, { status: 401 });
    }

    const body = (await request.json()) as CreateUserBody;
    const email = body.email?.trim().toLowerCase() ?? "";
    const password = body.password ?? "";
    const fullName = body.fullName?.trim() ?? "";
    const phone = body.phone?.trim() ?? "";

    if (!email || !password || !body.role) {
      return NextResponse.json({ error: "Missing email, password or role" }, { status: 400 });
    }

    if (!isValidEmail(email)) {
      return NextResponse.json({ error: "Invalid email format" }, { status: 400 });
    }

    if (password.length < 6) {
      return NextResponse.json({ error: "Password must be at least 6 characters" }, { status: 400 });
    }

    if (!isAllowedRole(body.role)) {
      return NextResponse.json({ error: "Only COMPANY_ADMIN or DRIVER can be created here" }, { status: 400 });
    }

    const supabase = adminClient();
    const {
      data: { user: requester },
      error: requesterError,
    } = await supabase.auth.getUser(token);

    if (requesterError || !requester) {
      return NextResponse.json({ error: "Invalid session" }, { status: 401 });
    }

    const { data: requesterProfileData } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", requester.id)
      .maybeSingle();
    const requesterProfile = requesterProfileData as Profile | null;

    if (!requesterProfile || requesterProfile.role === "DRIVER") {
      return NextResponse.json({ error: "Permission denied" }, { status: 403 });
    }

    const targetCompanyId =
      requesterProfile.role === "COMPANY_ADMIN"
        ? requesterProfile.company_id
        : body.companyId || requesterProfile.company_id;

    if (requesterProfile.role === "COMPANY_ADMIN" && body.role !== "DRIVER") {
      return NextResponse.json({ error: "COMPANY_ADMIN can only create DRIVER accounts" }, { status: 403 });
    }

    if (!targetCompanyId) {
      return NextResponse.json({ error: "Missing companyId" }, { status: 400 });
    }

    const { data: company, error: companyError } = await supabase
      .from("companies")
      .select("id")
      .eq("id", targetCompanyId)
      .maybeSingle();

    if (companyError || !company) {
      return NextResponse.json({ error: "Company does not exist" }, { status: 400 });
    }

    const { data: created, error: createError } = await supabase.auth.admin.createUser({
      email,
      password,
      email_confirm: true,
      user_metadata: {
        full_name: fullName,
        username: email.split("@")[0],
        role: body.role,
      },
    });

    if (createError || !created.user) {
      return NextResponse.json({ error: createError?.message || "Could not create user" }, { status: 400 });
    }

    const { error: profileError } = await supabase.from("profiles").upsert({
      id: created.user.id,
      email,
      username: email.split("@")[0],
      full_name: fullName,
      phone,
      role: body.role,
      status: "active",
      company_id: targetCompanyId,
    });

    if (profileError) {
      await cleanupCreatedUser(supabase, created.user.id);
      return NextResponse.json({ error: profileError.message }, { status: 400 });
    }

    const { error: settingsError } = await supabase
      .from("user_settings")
      .upsert({ user_id: created.user.id }, { onConflict: "user_id" });
    if (settingsError) {
      await cleanupCreatedUser(supabase, created.user.id);
      return NextResponse.json({ error: settingsError.message }, { status: 400 });
    }

    return NextResponse.json({
      user: {
        id: created.user.id,
        email,
        role: body.role,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unexpected server error" },
      { status: 500 },
    );
  }
}
