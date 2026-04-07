"use client";

import { useState } from "react";
import { getLoginUrl } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowRight, Loader2 } from "lucide-react";

export function ConnectStravaButton() {
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    try {
      const { url } = await getLoginUrl();
      window.location.href = url;
    } catch {
      setLoading(false);
    }
  };

  return (
    <Button
      variant="strava"
      size="lg"
      onClick={handleConnect}
      disabled={loading}
      className="rounded-xl px-8 py-6 text-lg font-semibold group"
    >
      {loading ? (
        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
      ) : (
        <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24" fill="currentColor">
          <path d="M15.387 17.944l-2.089-4.116h-3.065L15.387 24l5.15-10.172h-3.066m-7.008-5.599l2.836 5.598h4.172L10.463 0l-7 13.828h4.169" />
        </svg>
      )}
      {loading ? "Connecting..." : "Connect with Strava"}
      {!loading && (
        <ArrowRight className="ml-3 w-5 h-5 opacity-70 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-300" />
      )}
    </Button>
  );
}
