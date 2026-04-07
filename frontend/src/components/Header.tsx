"use client";

import { useEffect, useState } from "react";
import { getAuthStatus, logout } from "@/lib/api";
import type { AuthStatus } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { LogOut, Mountain } from "lucide-react";

export function Header() {
  const [auth, setAuth] = useState<AuthStatus | null>(null);

  useEffect(() => {
    getAuthStatus().then(setAuth).catch(() => setAuth({ authenticated: false }));
  }, []);

  const handleLogout = async () => {
    await logout();
    window.location.href = "/";
  };

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <a href="/" className="flex items-center gap-2 text-lg font-bold text-foreground">
          <Mountain className="w-6 h-6 text-[#FC4C02]" />
          <span>Trail2Strava</span>
        </a>

        {auth?.authenticated && (
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              Hi, {auth.first_name}
            </span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="w-4 h-4 mr-2" />
              Disconnect
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
