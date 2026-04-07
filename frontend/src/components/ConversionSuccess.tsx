"use client";

import type { ConversionResult } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { CheckCircle2, ExternalLink, RotateCcw } from "lucide-react";
import { motion } from "framer-motion";

interface ConversionSuccessProps {
  result: ConversionResult;
  onReset: () => void;
}

export function ConversionSuccess({ result, onReset }: ConversionSuccessProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-md mx-auto text-center"
    >
      <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
        >
          <CheckCircle2 className="w-16 h-16 text-[#FC4C02] mx-auto mb-4" />
        </motion.div>

        <h2 className="text-2xl font-bold mb-2">Activity Synced!</h2>
        <p className="text-muted-foreground mb-6">
          Your AllTrails activity has been successfully uploaded to Strava
          {result.upload_method === "gpx" ? " with full GPS data" : ""}.
        </p>

        <div className="flex flex-col gap-3">
          <a
            href={result.strava_activity_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button variant="strava" size="lg" className="w-full rounded-xl">
              View on Strava
              <ExternalLink className="w-4 h-4 ml-2" />
            </Button>
          </a>

          <Button
            variant="outline"
            size="lg"
            className="w-full rounded-xl"
            onClick={onReset}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Sync Another Activity
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
