"use client";

import { Dispatch, SetStateAction, useCallback, useEffect, useRef, useState } from "react";

type CacheResult<T> = {
  value: T;
  found: boolean;
};

function readCache<T>(key: string, fallback: T): CacheResult<T> {
  if (typeof window === "undefined") return { value: fallback, found: false };

  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return { value: fallback, found: false };
    return { value: JSON.parse(raw) as T, found: true };
  } catch {
    window.localStorage.removeItem(key);
    return { value: fallback, found: false };
  }
}

export function useCachedState<T>(key: string, fallback: T): [T, Dispatch<SetStateAction<T>>, boolean] {
  const fallbackRef = useRef(fallback);
  const [hadCache, setHadCache] = useState(() => readCache(key, fallback).found);
  const [shouldWrite, setShouldWrite] = useState(hadCache);
  const [state, setState] = useState<T>(() => readCache(key, fallback).value);

  const setCachedState = useCallback<Dispatch<SetStateAction<T>>>((nextState) => {
    setShouldWrite(true);
    setState(nextState);
  }, []);

  useEffect(() => {
    const cached = readCache(key, fallbackRef.current);
    setHadCache(cached.found);
    setShouldWrite(cached.found);
    setState(cached.value);
  }, [key]);

  useEffect(() => {
    if (!shouldWrite) return;
    window.localStorage.setItem(key, JSON.stringify(state));
  }, [key, shouldWrite, state]);

  return [state, setCachedState, hadCache];
}
