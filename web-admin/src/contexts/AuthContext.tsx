"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import type { Profile } from "@/types/database";

type AuthContextValue = {
  session: Session | null;
  profile: Profile | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error?: string }>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

type QueryResponse<T> = {
  data: T | null;
  error: { message: string } | null;
};

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

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = useCallback(async (userId: string) => {
    try {
      const { data, error } = await withTimeout<QueryResponse<Profile>>(
        supabase
          .from("profiles")
          .select("*")
          .eq("id", userId)
          .maybeSingle(),
      );

      if (error || !data) {
        setProfile(null);
        return;
      }
      setProfile(data);
    } catch {
      // Keep the current profile during transient Supabase/network delays so the
      // admin UI does not kick the user back to login while the session is valid.
    }
  }, []);

  const refreshProfile = useCallback(async () => {
    if (session?.user.id) {
      await loadProfile(session.user.id);
    }
  }, [loadProfile, session]);

  useEffect(() => {
    let mounted = true;

    withTimeout(supabase.auth.getSession(), 6000)
      .then(async ({ data }) => {
        if (!mounted) return;
        setSession(data.session);
        if (data.session?.user.id) {
          await loadProfile(data.session.user.id);
        }
      })
      .catch(() => {
        // Do not clear a browser session just because the initial restore failed.
      })
      .finally(() => {
        if (mounted) {
          setLoading(false);
        }
      });

    const { data: subscription } = supabase.auth.onAuthStateChange(
      async (_event, nextSession) => {
        setSession(nextSession);
        if (nextSession?.user.id) {
          await loadProfile(nextSession.user.id);
        } else {
          setProfile(null);
        }
        setLoading(false);
      },
    );

    return () => {
      mounted = false;
      subscription.subscription.unsubscribe();
    };
  }, [loadProfile]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      profile,
      loading,
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
        setProfile(null);
        setSession(null);
        router.push("/login");
      },
    }),
    [loadProfile, loading, profile, refreshProfile, router, session],
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
