"use client";

import { cn } from "@/lib/utils";
import { Check, Loader2 } from "lucide-react";

export type ConversionStep = "analyzing" | "generating" | "uploading" | "complete";

interface ConversionProgressProps {
  currentStep: ConversionStep;
}

const STEPS = [
  { key: "analyzing", label: "Analyzing Activity" },
  { key: "generating", label: "Generating Data" },
  { key: "uploading", label: "Uploading to Strava" },
  { key: "complete", label: "Complete" },
] as const;

function getStepIndex(step: ConversionStep): number {
  return STEPS.findIndex((s) => s.key === step);
}

export function ConversionProgress({ currentStep }: ConversionProgressProps) {
  const currentIndex = getStepIndex(currentStep);

  return (
    <div className="w-full max-w-xl mx-auto py-6">
      <div className="flex items-center justify-between">
        {STEPS.map((step, index) => {
          const isComplete = index < currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <div key={step.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm transition-all duration-300",
                    isComplete && "bg-[#FC4C02] text-white",
                    isCurrent && "bg-[#FC4C02]/10 text-[#FC4C02] ring-2 ring-[#FC4C02]",
                    !isComplete && !isCurrent && "bg-muted text-muted-foreground"
                  )}
                >
                  {isComplete ? (
                    <Check className="w-5 h-5" />
                  ) : isCurrent ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span
                  className={cn(
                    "text-xs mt-2 text-center whitespace-nowrap",
                    isCurrent ? "text-[#FC4C02] font-medium" : "text-muted-foreground"
                  )}
                >
                  {step.label}
                </span>
              </div>
              {index < STEPS.length - 1 && (
                <div
                  className={cn(
                    "flex-1 h-0.5 mx-3 mt-[-1.25rem] transition-all duration-500",
                    index < currentIndex ? "bg-[#FC4C02]" : "bg-muted"
                  )}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
