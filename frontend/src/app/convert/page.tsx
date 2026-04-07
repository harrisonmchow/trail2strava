"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Header } from "@/components/Header";
import { GpxFileInput } from "@/components/AllTrailsUrlInput";
import { ActivityPreview } from "@/components/ActivityPreview";
import { ConversionProgress, type ConversionStep } from "@/components/ConversionProgress";
import { ConversionSuccess } from "@/components/ConversionSuccess";
import { getAuthStatus, analyzeGpxFile, uploadGpxFile } from "@/lib/api";
import type { AllTrailsActivity, ConversionResult, ApiError } from "@/lib/types";
import { AlertCircle, Mountain } from "lucide-react";
import { Button } from "@/components/ui/button";

type FlowState = "input" | "analyzing" | "preview" | "uploading" | "success" | "error";

export default function ConvertPage() {
  const router = useRouter();
  const [flowState, setFlowState] = useState<FlowState>("input");
  const [activity, setActivity] = useState<AllTrailsActivity | null>(null);
  const [result, setResult] = useState<ConversionResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const currentFileRef = useRef<File | null>(null);
  const currentSourceUrlRef = useRef<string>("");

  useEffect(() => {
    getAuthStatus()
      .then((status) => {
        if (!status.authenticated) {
          router.push("/");
        }
      })
      .catch(() => router.push("/"));
  }, [router]);

  const handleFileSelect = async (file: File, sourceUrl?: string) => {
    currentFileRef.current = file;
    currentSourceUrlRef.current = sourceUrl || "";
    setFlowState("analyzing");
    setError(null);

    try {
      const data = await analyzeGpxFile(file, sourceUrl);
      setActivity(data);
      setFlowState("preview");
    } catch (err) {
      setError(err as ApiError);
      setFlowState("error");
    }
  };

  const handleUpload = async (customTitle?: string) => {
    if (!currentFileRef.current) return;
    setFlowState("uploading");
    setError(null);

    try {
      const data = await uploadGpxFile(
        currentFileRef.current,
        customTitle,
        currentSourceUrlRef.current
      );
      setResult(data);
      setFlowState("success");
    } catch (err) {
      setError(err as ApiError);
      setFlowState("error");
    }
  };

  const handleReset = () => {
    setFlowState("input");
    setActivity(null);
    setResult(null);
    setError(null);
    currentFileRef.current = null;
    currentSourceUrlRef.current = "";
  };

  const getProgressStep = (): ConversionStep => {
    switch (flowState) {
      case "analyzing":
        return "analyzing";
      case "uploading":
        return "uploading";
      case "success":
        return "complete";
      default:
        return "analyzing";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-4 pt-24 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center gap-3 mb-4">
            <Mountain className="w-8 h-8 text-[#FC4C02]" />
            <h1 className="text-3xl font-bold">Sync Your Activity</h1>
          </div>
          <p className="text-muted-foreground max-w-lg mx-auto">
            Upload your AllTrails GPX file and we&apos;ll transfer it to your Strava
            account with GPS data, splits, and all the details.
          </p>
        </motion.div>

        {(flowState === "analyzing" || flowState === "uploading") && (
          <ConversionProgress currentStep={getProgressStep()} />
        )}

        <div className="mt-8">
          {flowState === "input" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <GpxFileInput onFileSelect={handleFileSelect} />
            </motion.div>
          )}

          {flowState === "analyzing" && (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-[#FC4C02] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-muted-foreground">
                Analyzing your GPX file...
              </p>
            </div>
          )}

          {flowState === "preview" && activity && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <ActivityPreview activity={activity} onUpload={handleUpload} />
            </motion.div>
          )}

          {flowState === "uploading" && (
            <div className="text-center py-12">
              <div className="w-12 h-12 border-4 border-[#FC4C02] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="text-muted-foreground">Uploading to Strava...</p>
              <p className="text-xs text-muted-foreground mt-1">
                Creating your activity with GPS data and splits
              </p>
            </div>
          )}

          {flowState === "success" && result && (
            <ConversionSuccess result={result} onReset={handleReset} />
          )}

          {flowState === "error" && error && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="max-w-md mx-auto text-center"
            >
              <div className="rounded-2xl border border-destructive/20 bg-destructive/5 p-8">
                <AlertCircle className="w-12 h-12 text-destructive mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">
                  Something went wrong
                </h3>
                <p className="text-sm text-muted-foreground mb-6">
                  {error.message}
                </p>
                <div className="flex gap-3 justify-center">
                  {error.retryable && (
                    <Button
                      variant="strava"
                      onClick={() => {
                        if (currentFileRef.current) {
                          handleFileSelect(
                            currentFileRef.current,
                            currentSourceUrlRef.current
                          );
                        }
                      }}
                    >
                      Try Again
                    </Button>
                  )}
                  <Button variant="outline" onClick={handleReset}>
                    Start Over
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </div>
      </main>
    </div>
  );
}
