import type { AllTrailsActivity, AuthStatus, ConversionResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({
      error: "unknown",
      message: "An unexpected error occurred",
    }));
    throw error;
  }

  return res.json();
}

async function fetchFormData<T>(
  path: string,
  formData: FormData
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    credentials: "include",
    body: formData,
    // Don't set Content-Type - browser sets it with boundary for multipart
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({
      error: "unknown",
      message: "An unexpected error occurred",
    }));
    throw error;
  }

  return res.json();
}

export async function getLoginUrl(): Promise<{ url: string; state: string }> {
  return fetchApi("/auth/login");
}

export async function exchangeToken(
  code: string,
  state: string
): Promise<{ athlete_id: number; first_name: string }> {
  return fetchApi("/auth/token", {
    method: "POST",
    body: JSON.stringify({ code, state }),
  });
}

export async function getAuthStatus(): Promise<AuthStatus> {
  return fetchApi("/auth/status");
}

export async function logout(): Promise<void> {
  await fetchApi("/auth/logout", { method: "POST" });
}

export async function analyzeGpxFile(
  file: File,
  sourceUrl?: string
): Promise<AllTrailsActivity> {
  const formData = new FormData();
  formData.append("file", file);
  if (sourceUrl) {
    formData.append("source_url", sourceUrl);
  }
  return fetchFormData("/convert/analyze-gpx", formData);
}

export async function uploadGpxFile(
  file: File,
  customTitle?: string,
  sourceUrl?: string
): Promise<ConversionResult> {
  const formData = new FormData();
  formData.append("file", file);
  if (customTitle) {
    formData.append("custom_title", customTitle);
  }
  if (sourceUrl) {
    formData.append("source_url", sourceUrl);
  }
  return fetchFormData("/convert/upload-gpx", formData);
}

export async function uploadActivity(
  url: string,
  customTitle?: string
): Promise<ConversionResult> {
  return fetchApi("/convert/upload", {
    method: "POST",
    body: JSON.stringify({ url, custom_title: customTitle }),
  });
}
