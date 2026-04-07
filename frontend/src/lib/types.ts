export interface AllTrailsPhoto {
  url: string;
  caption: string | null;
}

export interface AllTrailsActivity {
  url: string;
  title: string;
  activity_type: string;
  distance_meters: number;
  elevation_gain_meters: number;
  duration_seconds: number;
  moving_time_seconds: number;
  avg_pace: string;
  calories: number;
  date: string;
  has_gps_data: boolean;
  coordinates: [number, number, number | null][];
  photos: AllTrailsPhoto[];
}

export interface ConversionResult {
  strava_activity_id: number;
  strava_activity_url: string;
  upload_method: "gpx" | "manual";
}

export interface AuthStatus {
  authenticated: boolean;
  athlete_id?: number;
  first_name?: string;
}

export interface ApiError {
  error: string;
  message: string;
  retryable?: boolean;
}
