"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { exchangeToken } from "@/lib/api";
import { Loader2, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Suspense } from "react";

function CallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState("");

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const errorParam = searchParams.get("error");

    if (errorParam) {
      setError("Authorization was denied. Please try again.");
      return;
    }

    if (!code || !state) {
      setError("Invalid callback. Missing authorization code.");
      return;
    }

    exchangeToken(code, state)
      .then(() => {
        router.push("/convert");
      })
      .catch((err) => {
        setError(err?.message || "Failed to complete authorization. Please try again.");
      });
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Authorization Failed</h2>
          <p className="text-muted-foreground mb-6">{error}</p>
          <a href="/">
            <Button variant="strava">Try Again</Button>
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-10 h-10 text-[#FC4C02] animate-spin mx-auto mb-4" />
        <p className="text-muted-foreground">Connecting to Strava...</p>
      </div>
    </div>
  );
}

export default function CallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <Loader2 className="w-10 h-10 text-[#FC4C02] animate-spin" />
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
