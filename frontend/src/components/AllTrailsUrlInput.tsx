"use client";

import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, FileUp, Loader2, AlertCircle, Link2, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface GpxFileInputProps {
  onFileSelect: (file: File, sourceUrl?: string) => void;
  loading?: boolean;
  disabled?: boolean;
}

export function GpxFileInput({ onFileSelect, loading, disabled }: GpxFileInputProps) {
  const [file, setFile] = useState<File | null>(null);
  const [sourceUrl, setSourceUrl] = useState("");
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.name.toLowerCase().endsWith(".gpx")) {
      setError("Please select a .gpx file");
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      setError("File is too large (max 10MB)");
      return;
    }
    setError("");
    setFile(f);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files[0];
      if (f) handleFile(f);
    },
    [handleFile]
  );

  const handleSubmit = () => {
    if (!file) return;
    onFileSelect(file, sourceUrl || undefined);
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      {/* File Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !file && fileInputRef.current?.click()}
        className={cn(
          "relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer",
          dragOver
            ? "border-[#FC4C02] bg-[#FC4C02]/5"
            : file
              ? "border-[#428813] bg-[#428813]/5"
              : "border-border hover:border-[#FC4C02]/50 hover:bg-muted/50"
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".gpx"
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
          }}
          disabled={disabled || loading}
        />

        {file ? (
          <div className="flex items-center justify-center gap-3">
            <FileUp className="w-6 h-6 text-[#428813]" />
            <div className="text-left">
              <p className="font-medium text-foreground">{file.name}</p>
              <p className="text-sm text-muted-foreground">
                {(file.size / 1024).toFixed(0)} KB
              </p>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setFile(null);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
              className="p-1 hover:bg-background rounded-md ml-2"
            >
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
        ) : (
          <>
            <FileUp className="w-10 h-10 text-muted-foreground mx-auto mb-3" />
            <p className="text-foreground font-medium mb-1">
              Drop your GPX file here or click to browse
            </p>
            <p className="text-sm text-muted-foreground">
              Download your GPX from AllTrails: Activity &rarr; &hellip; &rarr; Download Route &rarr; GPX Track
            </p>
          </>
        )}
      </div>

      {/* Optional: AllTrails URL for reference in description */}
      {file && (
        <div className={cn(
          "flex items-center gap-2 rounded-xl border bg-background p-2 transition-all duration-200",
          "border-border focus-within:border-[#FC4C02]/50"
        )}>
          <div className="flex items-center pl-3 text-muted-foreground">
            <Link2 className="w-4 h-4" />
          </div>
          <input
            type="url"
            value={sourceUrl}
            onChange={(e) => setSourceUrl(e.target.value)}
            placeholder="Optional: Paste AllTrails activity URL for reference"
            className="flex-1 bg-transparent text-foreground placeholder:text-muted-foreground outline-none text-sm py-1.5"
            disabled={disabled || loading}
          />
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Submit Button */}
      {file && (
        <Button
          variant="strava"
          size="lg"
          onClick={handleSubmit}
          disabled={!file || loading || disabled}
          className="w-full rounded-xl"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              Analyze GPX
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </Button>
      )}
    </div>
  );
}
