"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import type { Profile } from "@/types/database";

type ProfileStatus = "idle" | "loading" | "ready" | "missing" | "error";

type AuthContextValue = {
  session: Session | null;
  profile: Profile | null;
  loading: boolean;
  profileStatus: ProfileStatus;
  profileError: string;
  signIn: (email: string, password: string) => Promise<{ error?: string }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
};

type CachedProfile = {
  userId: string;
  profile: Profile;
  cachedAt: number;
};

type QueryResponse<T> = {
  data: T | null;
  error: { message: string } | null;
};

const AuthContext = createContext<AuthContextValue | null>(null);
const PROFILE_CACHE_KEY = "web-admin:profile";
const PROFILE_CACHE_MAX_AGE_MS = 6 * 60 * 60 * 1000;

function withTimeout<T>(promise: PromiseLike<T>, timeoutMs = 30000): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timeout = window.setTimeout(() => {
      reject(new Error("Supabase request timed out"));
    }, timeoutMs);

    Promise.resolve(promise)
      .then((result) => {
        window.clearTimeout(timeout);
        resolve(result);
      })
      .catch((error) => {
        window.clearTimeout(timeout);
        reject(error);
      });
  });
}

function readCachedProfile(userId: string) {
  if (typeof window === "undefined") return null;

  try {
    const raw = window.localStorage.getItem(PROFILE_CACHE_KEY);
    if (!raw) return null;

    const cached = JSON.parse(raw) as CachedProfile;
    if (cached.userId !== userId) return null;
    if (Date.now() - cached.cachedAt > PROFILE_CACHE_MAX_AGE_MS) return null;
    return cached.profile;
  } catch {
    window.localStorage.removeItem(PROFILE_CACHE_KEY);
    return null;
  }
}

function writeCachedProfile(profile: Profile) {
  if (typeof window === "undefined") return;

  window.localStorage.setItem(
    PROFILE_CACHE_KEY,
    JSON.stringify({ userId: profile.id, profile, cachedAt: Date.now() } satisfies CachedProfile),
  );
}

function clearCachedProfile() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(PROFILE_CACHE_KEY);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const profileRef = useRef<Profile | null>(null);
  const loadingProfileForRef = useRef<string | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [profileStatus, setProfileStatus] = useState<ProfileStatus>("idle");
  const [profileError, setProfileError] = useState("");

  const setCurrentProfile = useCallback((nextProfile: Profile | null) => {
    profileRef.current = nextProfile;
    setProfile(nextProfile);

    if (nextProfile) {
      writeCachedProfile(nextProfile);
    }
  }, []);

  const loadProfile = useCallback(
    async (userId: string, options?: { preferCache?: boolean }) => {
      if (loadingProfileForRef.current === userId) return;

      const cachedProfile = options?.preferCache ? readCachedProfile(userId) : null;
      if (cachedProfile) {
        setCurrentProfile(cachedProfile);
        setProfileStatus("ready");
        setProfileError("");
      } else {
        setProfileStatus("loading");
        setProfileError("");
      }

      loadingProfileForRef.current = userId;

      try {
        const { data, error } = await withTimeout<QueryResponse<Profile>>(
          supabase
            .from("profiles")
            .select("*")
            .eq("id", userId)
            .maybeSingle(),
          15000,
        );

        if (error) {
          setProfileStatus(profileRef.current ? "ready" : "error");
          setProfileError(error.message);
          return;
        }

        if (!data) {
          setCurrentProfile(null);
          clearCachedProfile();
          setProfileStatus("missing");
          return;
        }

        setCurrentProfile(data);
        setProfileStatus("ready");
      } catch {
        setProfileStatus(profileRef.current ? "ready" : "error");
        setProfileError("Khong ket noi duoc Supabase. Web van giu phien dang nhap va se thu lai khi co mang.");
      } finally {
        loadingProfileForRef.current = null;
      }
    },
    [setCurrentProfile],
  );

  const refreshProfile = useCallback(async () => {
    if (session?.user.id) {
      await loadProfile(session.user.id);
    }
  }, [loadProfile, session]);

  useEffect(() => {
    let mounted = true;

    withTimeout(supabase.auth.getSession(), 15000)
      .then(({ data }) => {
        if (!mounted) return;

        setSession(data.session);

        if (data.session?.user.id) {
          const cachedProfile = readCachedProfile(data.session.user.id);
          if (cachedProfile) {
            setCurrentProfile(cachedProfile);
            setProfileStatus("ready");
            setProfileError("");
          }

          void loadProfile(data.session.user.id, { preferCache: !cachedProfile });
        } else {
          setCurrentProfile(null);
          setProfileStatus("idle");
          setProfileError("");
          clearCachedProfile();
        }
      })
      .catch(() => {
        if (!mounted) return;
        setProfileStatus(profileRef.current ? "ready" : "error");
        setProfileError("Khong khoi phuc duoc phien dang nhap. Kiem tra mang roi thu lai.");
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    const { data: subscription } = supabase.auth.onAuthStateChange(async (_event, nextSession) => {
      setSession(nextSession);

      if (nextSession?.user.id) {
        await loadProfile(nextSession.user.id, { preferCache: true });
      } else {
        setCurrentProfile(null);
        setProfileStatus("idle");
        setProfileError("");
        clearCachedProfile();
      }

      setLoading(false);
    });

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, [loadProfile, setCurrentProfile]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      profile,
      loading,
      profileStatus,
      profileError,
      refreshProfile,
      signIn: async (email: string, password: string) => {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) return { error: error.message };
        if (data.user?.id) {
          await loadProfile(data.user.id);
        }
        return {};
      },
      signOut: async () => {
        await supabase.auth.signOut();
        setCurrentProfile(null);
        setSession(null);
        setProfileStatus("idle");
        setProfileError("");
        clearCachedProfile();
        router.push("/login");
      },
    }),
    [loadProfile, loading, profile, profileError, profileStatus, refreshProfile, router, session, setCurrentProfile],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
