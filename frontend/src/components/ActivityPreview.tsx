"use client";

import { useState } from "react";
import type { AllTrailsActivity } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { formatDistance, formatElevation, formatDuration } from "@/lib/utils";
import {
  MapPin,
  Mountain,
  Clock,
  Route,
  Upload,
  Loader2,
  Pencil,
  Check,
  X,
  Flame,
  Gauge,
  Camera,
  Info,
  Image as ImageIcon,
} from "lucide-react";

interface ActivityPreviewProps {
  activity: AllTrailsActivity;
  onUpload: (customTitle?: string) => void;
  loading?: boolean;
}

export function ActivityPreview({ activity, onUpload, loading }: ActivityPreviewProps) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(activity.title);

  return (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
        {/* Header */}
        <div className="bg-gradient-to-r from-[#428813]/10 to-[#FC4C02]/10 px-6 py-4 border-b border-border">
          <div className="flex items-center justify-between">
            {editing ? (
              <div className="flex items-center gap-2 flex-1">
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="flex-1 bg-background border border-border rounded-lg px-3 py-1.5 text-lg font-semibold outline-none focus:border-[#FC4C02]"
                  autoFocus
                />
                <button onClick={() => setEditing(false)} className="p-1.5 hover:bg-background rounded-md">
                  <Check className="w-4 h-4 text-[#428813]" />
                </button>
                <button onClick={() => { setTitle(activity.title); setEditing(false); }} className="p-1.5 hover:bg-background rounded-md">
                  <X className="w-4 h-4 text-muted-foreground" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-semibold text-foreground">{title}</h3>
                <button onClick={() => setEditing(true)} className="p-1 hover:bg-background/50 rounded-md">
                  <Pencil className="w-3.5 h-3.5 text-muted-foreground" />
                </button>
              </div>
            )}
            <span className="text-sm font-medium px-3 py-1 rounded-full bg-[#428813]/10 text-[#428813] shrink-0 ml-2">
              {activity.activity_type}
            </span>
          </div>
          {activity.date && (
            <p className="text-sm text-muted-foreground mt-1">{activity.date}</p>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 p-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <Route className="w-4 h-4 text-[#FC4C02]" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Distance</p>
              <p className="font-semibold">{formatDistance(activity.distance_meters)}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <Mountain className="w-4 h-4 text-[#428813]" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Elevation Gain</p>
              <p className="font-semibold">{formatElevation(activity.elevation_gain_meters)}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <Clock className="w-4 h-4 text-blue-500" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">
                {activity.moving_time_seconds > 0 ? "Moving Time" : "Duration"}
              </p>
              <p className="font-semibold">
                {formatDuration(activity.moving_time_seconds || activity.duration_seconds)}
              </p>
            </div>
          </div>
          {activity.avg_pace && (
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-muted">
                <Gauge className="w-4 h-4 text-orange-500" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Avg Pace</p>
                <p className="font-semibold">{activity.avg_pace}</p>
              </div>
            </div>
          )}
          {activity.calories > 0 && (
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-muted">
                <Flame className="w-4 h-4 text-red-500" />
              </div>
              <div>
                <p className="text-xs text-muted-foreground">Calories</p>
                <p className="font-semibold">{activity.calories.toLocaleString()}</p>
              </div>
            </div>
          )}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-muted">
              <MapPin className="w-4 h-4 text-purple-500" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">GPS Data</p>
              <p className="font-semibold">{activity.has_gps_data ? "Available" : "None"}</p>
            </div>
          </div>
        </div>

        {/* Photos */}
        {activity.photos.length > 0 && (
          <div className="px-6 pb-4">
            <div className="flex items-center gap-2 mb-3">
              <Camera className="w-4 h-4 text-muted-foreground" />
              <p className="text-sm font-medium text-muted-foreground">
                {activity.photos.length} Photo{activity.photos.length > 1 ? "s" : ""}
              </p>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-2">
              {activity.photos.map((photo, i) => (
                <a
                  key={i}
                  href={photo.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="shrink-0 rounded-lg overflow-hidden border border-border hover:border-[#FC4C02]/50 transition-colors"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={photo.url}
                    alt={photo.caption || `Activity photo ${i + 1}`}
                    className="w-24 h-24 object-cover"
                    loading="lazy"
                  />
                </a>
              ))}
            </div>
            <div className="flex items-start gap-2 mt-2 p-2 rounded-lg bg-amber-50 border border-amber-200">
              <Info className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-xs text-amber-700">
                Strava&apos;s API doesn&apos;t support photo uploads. Photo links will be included in the activity description.
              </p>
            </div>
          </div>
        )}

        {/* KM Splits Info */}
        {activity.has_gps_data && (
          <div className="px-6 pb-4">
            <div className="flex items-start gap-2 p-2 rounded-lg bg-blue-50 border border-blue-200">
              <ImageIcon className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
              <p className="text-xs text-blue-700">
                KM splits will be automatically calculated by Strava from the GPS data.
              </p>
            </div>
          </div>
        )}

        {/* Upload Button */}
        <div className="px-6 pb-6">
          <Button
            variant="strava"
            size="lg"
            className="w-full rounded-xl"
            onClick={() => onUpload(title !== activity.title ? title : undefined)}
            disabled={loading}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Uploading to Strava...
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 mr-2" />
                Sync to Strava
              </>
            )}
          </Button>
          {!activity.has_gps_data && (
            <p className="text-xs text-muted-foreground text-center mt-2">
              No GPS data found. Activity will be created without a map or splits.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
